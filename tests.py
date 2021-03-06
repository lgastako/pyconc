import unittest
import operator

from copy import copy

from pyconc import Empty
from pyconc import Singleton
from pyconc import Concat
from pyconc import identity

from pyconc import SingleThreadedMultiplexor


class ConcTests(unittest.TestCase):

    def setUp(self):
        self.empty = Empty()
        self.single = Singleton(42)
        self.left_only = Concat(self.single, self.empty)
        self.right_only = Concat(self.empty, self.single)
        self.double = Concat(self.single, self.single)
        self.two_by_two = Concat(self.double, self.double)
        self.one_234 = Concat(Concat(Singleton(1), Singleton(2)),
                              Concat(Singleton(3), Singleton(4)))
        self.st_multiplexor = SingleThreadedMultiplexor()

    def test_identity(self):
        for thing in [None, 5, "foo", object(), Empty(), [1, 2, 3],
                      (3, 4, 5), False, True]:
            self.assertEquals(thing, identity(thing))

    def test_length_of_empty_list_is_zero(self):
        clist = self.empty
        self.assertEquals(0, len(clist))

    def test_length_of_singleton_list_is_one(self):
        clist = self.single
        self.assertEquals(1, len(clist))

    def test_length_of_concat_is_length_of_left_plus_right(self):
        self.assertEquals(1, len(self.left_only))
        self.assertEquals(1, len(self.right_only))
        self.assertEquals(2, len(self.double))
        self.assertEquals(4, len(self.two_by_two))

    def test_as_list_simple(self):
        self.assertEquals([], self.empty.to_list())
        self.assertEquals([42], self.single.to_list())
        self.assertEquals([42], self.left_only.to_list())
        self.assertEquals([42], self.right_only.to_list())
        self.assertEquals([42, 42], self.double.to_list())
        self.assertEquals([42, 42, 42, 42], self.two_by_two.to_list())
        self.assertEquals([1, 2, 3, 4], self.one_234.to_list())

    def test_singlethreaded_mapreduce_empty_no_initial_value(self):
        f = lambda: self.st_multiplexor.map_reduce(self.empty,
                                                   None, operator.__add__)
        self.assertRaises(TypeError, f)

    def test_singlethreaded_mapreduce_empty_with_initial_value(self):
        self.assertEquals(10, self.st_multiplexor.map_reduce(self.empty,
                                                             None,
                                                             operator.__add__,
                                                             initial=10))

    def test_singlethreaded_mapreduce_singleton__no_initial_value(self):
        self.assertEquals(42, self.st_multiplexor.map_reduce(self.single,
                                                             None,
                                                             operator.__add__))

    def test_singlethreaded_mapreduce_singleton_with_initial_value(self):
        self.assertEquals(52, self.st_multiplexor.map_reduce(self.single,
                                                             None,
                                                             operator.__add__,
                                                             initial=10))

    def test_singlethreaded_mapreduce_concat_no_initial_value(self):
        self.assertEquals(10, self.st_multiplexor.map_reduce(self.one_234,
                                                             None,
                                                             operator.__add__))

    def test_singlethreaded_mapreduce_concat_with_initial_value(self):
        self.assertEquals(20, self.st_multiplexor.map_reduce(self.one_234,
                                                             None,
                                                             operator.__add__,
                                                             initial=10))


if __name__ == '__main__':
    unittest.main()
