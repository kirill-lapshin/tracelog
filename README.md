# Tracelog — trace and log every function call

This is meant to be simple `strace`-like tool for Python. In current form
it doesn't trace really everything. One has to selectively opt-in certain
methods, classes, or modules.

         from tracelog import traced, setup_log

         setup_log(print, print_stack=False) # not necessary; config it to be more terse


         @traced
         def foo(x):
             bar(x)

         @traced
         def bar(x):
             pass

         foo(42)

Prints out on stdout:

       foo(42)
         bar(42)

You can also trace whole classes:

    @traced
    class Foo:
        def do_stuff(): pass
        def poke(): pass
