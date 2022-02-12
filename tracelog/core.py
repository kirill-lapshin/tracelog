import inspect
import traceback
from io import StringIO

from .types import should_be_traced


_DEFAULT_LOG_INDENT = 2
_PRINT_STACKTRACE = True


class IndentedLog:
    def __init__(self, log, *, indent):
        self._reinit(log, indent=indent)

    def _reinit(self, log, *, indent):
        self._log = log
        self._indent_str = ' ' * indent
        self._level = 0

    def indent(self):
        self._level += 1

    def dedent(self):
        assert self._level > 0
        self._level -= 1

    def on_func_call_log(self):
        if self._level == 0 and _PRINT_STACKTRACE:
            # dropping last two frames chich are this frame (indent) and trace_wrapper
            for line in traceback.format_stack()[:-2]:
                self._log(line)

    def __call__(self, msg):
        self._log(f'{self._indent_str * self._level}{msg}')


# KISS for now. Not considering multithreading/multiprocessing yet.
_global_log = IndentedLog(print, indent=_DEFAULT_LOG_INDENT)


def setup_log(log, *, indent=_DEFAULT_LOG_INDENT, print_stack=_PRINT_STACKTRACE):
    _global_log._reinit(log, indent=indent)
    global _PRINT_STACKTRACE
    _PRINT_STACKTRACE = print_stack


def _traced_func(func, log: IndentedLog):
    assert isinstance(log, IndentedLog)

    if hasattr(func, '_already_tracelogged'):
        return func

    def trace_wrapper(*args, **kwargs):
        log(f'{func.__qualname__}({_fmt_arglist(*args, **kwargs)})')
        log.on_func_call_log() # give it a chance to print traceback
        log.indent()
        try:
            result = func(*args, **kwargs)
        finally:
            log.dedent()
        if result is not None:
            log(f'return {result}')
        return result

    trace_wrapper._already_tracelogged = True

    return trace_wrapper


def _traced(obj, log: IndentedLog):
    assert isinstance(log, IndentedLog)
    if not should_be_traced(obj):
        return obj

    if inspect.ismethod(obj) or inspect.isfunction(obj):
        return _traced_func(obj, log)

    if inspect.isclass(obj):
        for name, method in inspect.getmembers(obj, inspect.isfunction):
            if name != '__repr__': # to avoid endless recursion -- wrapped repr calls repr to log, which calls repr
                setattr(obj, name, _traced_func(method, log))
        return obj

    raise ValueError(f'Unexpected type to trace {type(obj)}, obj={obj}')


def _deduce_name(obj):
    return getattr(obj, '__qualname__', None) or getattr(obj, '__name__', None) or obj.__class__.__name__


def _fmt_arglist(*args, **kwargs):
    s = StringIO()
    n = 0
    for a in args:
        if n:
            s.write(', ')
        s.write(repr(a))
        n += 1
    for k, v in kwargs.items():
        if n:
            s.write(', ')
        s.write(f'k={repr(v)}')
        n += 1

    return s.getvalue()


def traced(obj):
    return _traced(obj, _global_log)
