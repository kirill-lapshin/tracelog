import numbers
from collections.abc import Mapping, Sequence
from typing import Any


_UNTRACED_TYPES = [numbers.Number, str, bytes]


try:
    import pandas
    _UNTRACED_TYPES.extend([pandas.DataFrame, pandas.Series])
except ModuleNotFoundError:
    pass


_UNTRACED_TYPES = tuple(_UNTRACED_TYPES)


def should_be_traced(obj: Any) -> bool:
    """Returns False if this type shouldn't be traced.
    Typically builtin primitive types and common third-party types would be added here
    to avoid too much noise in the log."""
    if isinstance(obj, _UNTRACED_TYPES):
        return False

    if isinstance(obj, Mapping):
        for k, v in obj.items():
            if should_be_traced(k) or should_be_traced(v):
                return True
        return False

    if isinstance(obj, Sequence):
        for v in obj:
            if should_be_traced(v):
                return True
        return False

    return True
