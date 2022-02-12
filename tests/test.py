from io import StringIO
import unittest

from .context import tracelog
from tracelog import traced


@traced
def squared(x):
    return x*x

@traced
def squared_plus_one(x):
    return squared(x) + 1

@traced
class Foo:
    x = None
    def __init__(self, x):
        self.x = x

    def __repr__(self):
        return f'Foo({self.x})'

    def trippled(self):
        return self.x * 3

    def trippled_plus_one(self):
        return self.trippled() + 1

@traced
class Bar(Foo):
    def __init__(self, x, y):
        super().__init__(x + y)

    def __repr__(self):
        return f'Bar'

    def trippled_plus_two(self):
        return self.trippled_plus_one() + 1


class UFoo:
    x = None
    def __init__(self, x):
        self.x = x

    def __repr__(self):
        return f'UFoo({self.x})'

    def trippled(self):
        return self.x * 3

    def trippled_plus_one(self):
        return self.trippled() + 1


@traced
class UBar(UFoo):
    def __init__(self, x, y):
        super().__init__(x + y)

    def __repr__(self):
        return f'UBar'

    def trippled_plus_two(self):
        return self.trippled_plus_one() + 1


@traced
def foo(x):
    bar(x)

@traced
def bar(x):
    pass


class TraceLogTest(unittest.TestCase):
    def testA(self):
        foo(42)
        self.assertLog('''\
''')

    def setUp(self):
        print('~'*78)
        self._log_stream = StringIO()
        tracelog.setup_log(lambda msg: print(msg, file=self._log_stream), print_stack=False)
        self.maxDiff = None

    def assertLog(self, expected):
        self.assertEqual(expected, self._log_stream.getvalue())

    def test_func(self):
        squared(3)
        self.assertLog('''\
squared(3)
return 9
''')

    def test_func_indirect(self):
        squared_plus_one(2)
        self.assertLog('''\
squared_plus_one(2)
  squared(2)
  return 4
return 5
''')

    def test_method_indirect(self):
        foo = Foo(5)
        foo.trippled_plus_one()
        self.assertLog('''\
Foo.__init__(Foo(None), 5)
Foo.trippled_plus_one(Foo(5))
  Foo.trippled(Foo(5))
  return 15
return 16
''')


    def test_inherited_from_traced(self):
        foo = Bar(5, 2)
        foo.trippled_plus_two()
        self.assertLog('''\
Bar.__init__(Bar, 5, 2)
  Foo.__init__(Bar, 7)
Bar.trippled_plus_two(Bar)
  Foo.trippled_plus_one(Bar)
    Foo.trippled(Bar)
    return 21
  return 22
return 23
''')

    def test_inherited_from_untraced(self):
        foo = UBar(5, 2)
        foo.trippled_plus_two()
        self.assertLog('''\
UBar.__init__(UBar, 5, 2)
UBar.trippled_plus_two(UBar)
  UFoo.trippled_plus_one(UBar)
    UFoo.trippled(UBar)
    return 21
  return 22
return 23
''')


if __name__ == '__main__':
    unittest.main()
