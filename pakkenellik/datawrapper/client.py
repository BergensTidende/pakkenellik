"""Compatibility wrapper for the upstream datawrapper package."""

try:
    from datawrapper import Datawrapper
except ImportError as error:  # pragma: no cover
    raise ImportError(
        "Datawrapper support requires the optional dependency. "
        'Install with `uv add "pakkenellik[datawrapper]"` or install '
        "`datawrapper` directly."
    ) from error

__all__ = ["Datawrapper"]
