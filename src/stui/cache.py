from __future__ import annotations

import functools
import hashlib
import inspect
import marshal
import math
import pickle
import threading
import time
import weakref
from collections import OrderedDict
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, ParamSpec, TypeVar

from .runtime import _get_process_active_runtime, get_current_runtime

P = ParamSpec("P")
T = TypeVar("T")

_monotonic = time.monotonic


class CacheSerializationError(TypeError):
    """Raised when cache arguments or data results cannot be serialized."""


@dataclass(frozen=True)
class _CacheEntry:
    value: Any
    created_at: float


@dataclass(frozen=True)
class _InFlightFill:
    event: threading.Event
    owner_thread_id: int


_RuntimeIdentity = tuple[str, str]
_FallbackIdentity = tuple[str, str, object]
_CacheIdentity = _RuntimeIdentity | _FallbackIdentity


@dataclass
class _FunctionCache:
    fingerprint: str
    entries: OrderedDict[bytes, _CacheEntry] = field(default_factory=OrderedDict)
    inflight: dict[bytes, _InFlightFill] = field(default_factory=dict)


@dataclass(frozen=True)
class CacheStats:
    """Non-sensitive aggregate counts for one cache namespace."""

    functions: int = 0
    entries: int = 0
    in_flight: int = 0

    def as_dict(self) -> dict[str, int]:
        return {
            "functions": self.functions,
            "entries": self.entries,
            "in_flight": self.in_flight,
        }


_CACHE_MISS = object()


class _CacheNamespace:
    def __init__(self, kind: Literal["data", "resource"]) -> None:
        self._kind = kind
        self._lock = threading.RLock()
        self._runtime_owners: weakref.WeakSet[Any] = weakref.WeakSet()
        self._hooked_runtimes: weakref.WeakSet[Any] = weakref.WeakSet()
        self._fallback_registry: dict[_CacheIdentity, _FunctionCache] = {}

    def __call__(
        self,
        func: Callable[P, T] | None = None,
        *,
        ttl: int | float | None = None,
        max_entries: int | None = None,
    ):
        normalized_ttl = _validate_ttl(ttl)
        normalized_max_entries = _validate_max_entries(max_entries)

        def decorate(target: Callable[P, T]) -> Callable[P, T]:
            if not callable(target):
                raise TypeError("Cache decorators can only be applied to callables.")
            return self._decorate(
                target,
                ttl=normalized_ttl,
                max_entries=normalized_max_entries,
            )

        if func is None:
            return decorate
        return decorate(func)

    def clear(self) -> None:
        """Clear every entry owned by this cache namespace in this process."""
        with self._lock:
            for runtime in tuple(self._runtime_owners):
                runtime._clear_cache_registry(self)
            self._fallback_registry.clear()

    def _clear_runtime(self, runtime: Any) -> None:
        """Clear this namespace for one app runtime without affecting others."""
        with self._lock:
            runtime._clear_cache_registry(self)

    def stats(self, runtime: Any | None = None) -> CacheStats:
        """Return aggregate counts without exposing cache keys or values."""
        if runtime is None:
            runtime = _context_runtime_or_none()
        if runtime is None:
            raise RuntimeError(
                "Cache diagnostics require an active Runtime or an explicit runtime."
            )
        with self._lock:
            registry = runtime._get_cache_registry(self, create=False)
            return _registry_stats(registry)

    def _decorate(
        self,
        func: Callable[P, T],
        *,
        ttl: float | None,
        max_entries: int | None,
    ) -> Callable[P, T]:
        runtime_identity = _function_identity(func)
        fallback_identity = (*runtime_identity, object())
        fingerprint = _function_fingerprint(
            func,
            kind=self._kind,
            ttl=ttl,
            max_entries=max_entries,
        )
        decoration_runtime = _context_runtime_or_none()
        decoration_runtime_ref = (
            weakref.ref(decoration_runtime) if decoration_runtime is not None else None
        )

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            argument_key = _argument_key(func, args, kwargs, cache_kind=self._kind)

            while True:
                cached_value: Any = _CACHE_MISS
                owns_fill = False
                with self._lock:
                    registry, uses_fallback = self._registry_for_current_runtime(
                        decoration_runtime_ref
                    )
                    identity: _CacheIdentity = (
                        fallback_identity if uses_fallback else runtime_identity
                    )
                    function_cache = registry.get(identity)
                    if (
                        function_cache is None
                        or function_cache.fingerprint != fingerprint
                    ):
                        function_cache = _FunctionCache(fingerprint=fingerprint)
                        registry[identity] = function_cache

                    entry = function_cache.entries.get(argument_key)
                    if entry is not None:
                        now = _monotonic()
                        if ttl is None or now - entry.created_at < ttl:
                            function_cache.entries.move_to_end(argument_key)
                            cached_value = entry.value
                        else:
                            del function_cache.entries[argument_key]

                    inflight = function_cache.inflight.get(argument_key)
                    if cached_value is _CACHE_MISS and inflight is None:
                        inflight = _InFlightFill(
                            event=threading.Event(),
                            owner_thread_id=threading.get_ident(),
                        )
                        function_cache.inflight[argument_key] = inflight
                        owns_fill = True
                    elif (
                        cached_value is _CACHE_MISS
                        and inflight is not None
                        and inflight.owner_thread_id == threading.get_ident()
                    ):
                        name = _function_display_name(func)
                        raise RuntimeError(
                            "st.cache_"
                            f"{self._kind} detected a recursive cache fill for "
                            f"{name!r}. A cached function cannot request the same "
                            "key before its first call finishes."
                        )

                if cached_value is not _CACHE_MISS:
                    return self._restore_value(cached_value, func)
                if owns_fill:
                    break
                assert inflight is not None
                inflight.event.wait()

            try:
                result = func(*args, **kwargs)
                stored_value, return_value = self._prepare_value(result, func)
            except BaseException:
                with self._lock:
                    if function_cache.inflight.get(argument_key) is inflight:
                        function_cache.inflight.pop(argument_key, None)
                    inflight.event.set()
                raise

            with self._lock:
                if registry.get(identity) is function_cache:
                    function_cache.entries[argument_key] = _CacheEntry(
                        value=stored_value,
                        created_at=_monotonic(),
                    )
                    function_cache.entries.move_to_end(argument_key)

                    if max_entries is not None:
                        while len(function_cache.entries) > max_entries:
                            function_cache.entries.popitem(last=False)

                if function_cache.inflight.get(argument_key) is inflight:
                    function_cache.inflight.pop(argument_key, None)
                inflight.event.set()
            return return_value

        def clear_function() -> None:
            with self._lock:
                self._fallback_registry.pop(fallback_identity, None)
                for runtime in tuple(self._runtime_owners):
                    registry = runtime._get_cache_registry(self, create=False)
                    if registry is not None:
                        registry.pop(runtime_identity, None)

        setattr(wrapper, "clear", clear_function)
        return wrapper

    def _registry_for_current_runtime(
        self,
        decoration_runtime_ref: weakref.ReferenceType[Any] | None,
    ) -> tuple[dict[_CacheIdentity, _FunctionCache], bool]:
        runtime = _runtime_for_call(
            self._kind,
            decoration_runtime_ref,
        )
        if runtime is None:
            return self._fallback_registry, True

        registry = runtime._get_cache_registry(self)
        assert registry is not None
        self._runtime_owners.add(runtime)
        self._register_source_change_hook(runtime)
        return registry, False

    def _register_source_change_hook(self, runtime: Any) -> None:
        if runtime in self._hooked_runtimes:
            return
        add_callback = getattr(runtime, "add_source_change_callback", None)
        if not callable(add_callback):
            return

        runtime_ref = weakref.ref(runtime)

        def clear_runtime_cache(
            _changed_paths: frozenset[Path],
            _source_revision: int,
        ) -> None:
            owner = runtime_ref()
            if owner is None:
                return
            with self._lock:
                owner._clear_cache_registry(self)

        add_callback(clear_runtime_cache)
        self._hooked_runtimes.add(runtime)

    def _prepare_value(
        self,
        value: T,
        func: Callable[..., Any],
    ) -> tuple[Any, T]:
        if self._kind == "resource":
            return value, value

        try:
            payload = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
            copied_value = pickle.loads(payload)
        except Exception as exc:
            name = _function_display_name(func)
            raise CacheSerializationError(
                "st.cache_data could not serialize the return value from "
                f"{name!r} ({type(exc).__name__}). Return a pickle-compatible "
                "value or use st.cache_resource."
            ) from exc
        return payload, copied_value

    def _restore_value(self, stored_value: Any, func: Callable[..., Any]) -> T:
        if self._kind == "resource":
            return stored_value

        try:
            return pickle.loads(stored_value)
        except Exception as exc:
            name = _function_display_name(func)
            raise CacheSerializationError(
                "st.cache_data could not restore the cached return value from "
                f"{name!r} ({type(exc).__name__}). Clear the function cache and "
                "recompute the value."
            ) from exc


def _validate_ttl(ttl: int | float | None) -> float | None:
    if ttl is None:
        return None
    if isinstance(ttl, bool) or not isinstance(ttl, int | float):
        raise ValueError("ttl must be None or a positive finite number.")
    numeric_ttl = float(ttl)
    if not math.isfinite(numeric_ttl) or numeric_ttl <= 0:
        raise ValueError("ttl must be None or a positive finite number.")
    return numeric_ttl


def _validate_max_entries(max_entries: int | None) -> int | None:
    if max_entries is None:
        return None
    if (
        isinstance(max_entries, bool)
        or not isinstance(max_entries, int)
        or max_entries <= 0
    ):
        raise ValueError("max_entries must be None or a positive integer.")
    return max_entries


def _function_identity(func: Callable[..., Any]) -> _RuntimeIdentity:
    return (_function_source_path(func), func.__qualname__)


def _function_display_name(func: Callable[..., Any]) -> str:
    module = getattr(func, "__module__", "")
    if module and module != "__main__":
        return f"{module}.{func.__qualname__}"
    return func.__qualname__


def _function_source_path(func: Callable[..., Any]) -> str:
    code = getattr(func, "__code__", None)
    filename = getattr(code, "co_filename", None)
    if not filename:
        return f"<{getattr(func, '__module__', 'unknown')}>"
    if filename.startswith("<") and filename.endswith(">"):
        return filename
    return str(Path(filename).expanduser().resolve())


def _context_runtime_or_none() -> Any | None:
    try:
        return get_current_runtime()
    except RuntimeError:
        return None


def _runtime_for_call(
    kind: str,
    decoration_runtime_ref: weakref.ReferenceType[Any] | None,
) -> Any | None:
    current_runtime = _context_runtime_or_none()
    if current_runtime is not None:
        return current_runtime

    if decoration_runtime_ref is not None:
        decoration_runtime = decoration_runtime_ref()
        if decoration_runtime is None:
            raise RuntimeError(
                f"st.cache_{kind} cannot run because its owning Runtime no longer "
                "exists."
            )
        return decoration_runtime

    if _get_process_active_runtime() is not None:
        raise RuntimeError(
            f"st.cache_{kind} cannot assign a contextless worker call to the "
            "active Runtime. Define the cached function inside the stui script "
            "or propagate the Runtime context explicitly."
        )
    return None


def _function_fingerprint(
    func: Callable[..., Any],
    *,
    kind: str,
    ttl: float | None,
    max_entries: int | None,
) -> str:
    digest = hashlib.sha256()
    code = getattr(func, "__code__", None)
    if code is not None:
        digest.update(marshal.dumps(code))

    source_path = _function_source_path(func)
    if not source_path.startswith("<"):
        try:
            digest.update(Path(source_path).read_bytes())
        except OSError:
            pass

    digest.update(_fingerprint_value(getattr(func, "__defaults__", None)))
    digest.update(_fingerprint_value(getattr(func, "__kwdefaults__", None)))
    closure = getattr(func, "__closure__", None) or ()
    closure_values: list[Any] = []
    for cell in closure:
        try:
            closure_values.append(cell.cell_contents)
        except ValueError:
            closure_values.append("<empty-cell>")
    digest.update(_fingerprint_value(tuple(closure_values)))
    digest.update(f"{kind}:{ttl!r}:{max_entries!r}".encode())
    return digest.hexdigest()


def _fingerprint_value(value: Any, seen: set[int] | None = None) -> bytes:
    try:
        return pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception:
        pass

    value_id = id(value)
    seen = set() if seen is None else seen
    value_type = type(value)
    type_name = f"{value_type.__module__}.{value_type.__qualname__}"
    if value_id in seen:
        return f"<cycle:{type_name}:{value_id}>".encode()

    seen.add(value_id)
    try:
        if isinstance(value, dict):
            items = sorted(
                (
                    _fingerprint_value(key, seen),
                    _fingerprint_value(item, seen),
                )
                for key, item in value.items()
            )
            return b"<dict>" + b"".join(
                len(key).to_bytes(8, "big") + key + item for key, item in items
            )
        if isinstance(value, list | tuple):
            parts = [_fingerprint_value(item, seen) for item in value]
            return f"<{type_name}>".encode() + b"".join(
                len(part).to_bytes(8, "big") + part for part in parts
            )
        if isinstance(value, set | frozenset):
            parts = sorted(_fingerprint_value(item, seen) for item in value)
            return f"<{type_name}>".encode() + b"".join(
                len(part).to_bytes(8, "big") + part for part in parts
            )
        try:
            representation = repr(value)
        except Exception:
            representation = f"id={value_id}"
        return f"<{type_name}:id={value_id}:{representation}>".encode()
    finally:
        seen.remove(value_id)


def _argument_key(
    func: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    *,
    cache_kind: str,
) -> bytes:
    signature = inspect.signature(func)
    bound = signature.bind(*args, **kwargs)
    bound.apply_defaults()
    try:
        normalized: list[tuple[str, Any]] = []
        for name, value in bound.arguments.items():
            parameter = signature.parameters[name]
            if parameter.kind is inspect.Parameter.VAR_KEYWORD:
                value = tuple(sorted(value.items()))
            normalized.append((name, value))
        payload = pickle.dumps(tuple(normalized), protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as exc:
        name = _function_display_name(func)
        raise CacheSerializationError(
            f"st.cache_{cache_kind} could not create a cache key for {name!r} "
            f"({type(exc).__name__}). Arguments must be pickle-compatible."
        ) from exc
    return hashlib.sha256(payload).digest()


cache_data = _CacheNamespace("data")
cache_resource = _CacheNamespace("resource")


def _registry_stats(
    registry: dict[_CacheIdentity, _FunctionCache] | None,
) -> CacheStats:
    if not registry:
        return CacheStats()
    return CacheStats(
        functions=len(registry),
        entries=sum(
            len(function_cache.entries) for function_cache in registry.values()
        ),
        in_flight=sum(
            len(function_cache.inflight) for function_cache in registry.values()
        ),
    )


def _combine_stats(stats: Iterable[CacheStats]) -> CacheStats:
    functions = 0
    entries = 0
    in_flight = 0
    for item in stats:
        functions += item.functions
        entries += item.entries
        in_flight += item.in_flight
    return CacheStats(
        functions=functions,
        entries=entries,
        in_flight=in_flight,
    )


def cache_info(runtime: Any | None = None) -> dict[str, object]:
    """Return versioned aggregate cache diagnostics for one app runtime."""
    data = cache_data.stats(runtime)
    resource = cache_resource.stats(runtime)
    total = _combine_stats((data, resource))
    return {
        "schema_version": "stui.cache_info.v1",
        "data": data.as_dict(),
        "resource": resource.as_dict(),
        "total": total.as_dict(),
    }


__all__ = ["CacheStats", "cache_data", "cache_info", "cache_resource"]
