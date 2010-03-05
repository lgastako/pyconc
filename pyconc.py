import unittest
import operator

from copy import copy


def identity(x):
    return x


class Empty(object):

    def __len__(self):
        return 0

    def to_list(self):
        return []

    def map_reduce(self, _mapf, _reducef, initial=None):
        if initial is not None:
            return initial
        raise TypeError("map_reduce() of empty sequence with no initial value")


class Singleton(object):

    def __init__(self, value):
        self.value = value

    def __len__(self):
        return 1

    def to_list(self):
        return [self.value]

    def map(self, mapf):
        if mapf is None:
            mapf = identity
        return mapf(self.value)

    def map_reduce(self, mapf, reducef, initial=None):
        result = self.map(mapf)
        if initial:
            result = reducef(initial, result)
        return result


class Concat(object):

    def __init__(self, left, right=None):
        self.left = left
        # TODO: No test case for this yet.
        # if right is None:
        #     right = Empty
        self.right = right

    def __len__(self):
        return len(self.left) + len(self.right)

    def to_list(self):
        return self.left.to_list() + self.right.to_list()

    def map_reduce(self, mapf, reducef, initial=None):

        def sub_map_reduce(target, x_initial=None):
            return target.map_reduce(mapf, reducef, initial=x_initial)

        if self.left and self.right:
            result = reducef(sub_map_reduce(self.left, x_initial=initial),
                             sub_map_reduce(self.right))
        elif self.left:
            result = sub_map_reduce(self.left, x_initial=initial)
        elif self.right:
            result = sub_map_reduce(self.right, x_initial=initial)
        return result


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
        f = lambda: self.empty.map_reduce(None, operator.__add__)
        self.assertRaises(TypeError, f)

    def test_singlethreaded_mapreduce_empty_with_initial_value(self):
        self.assertEquals(10, self.empty.map_reduce(None, operator.__add__,
                                                    initial=10))

    def test_singlethreaded_mapreduce_singleton__no_initial_value(self):
        self.assertEquals(42, self.single.map_reduce(None, operator.__add__))

    def test_singlethreaded_mapreduce_singleton_with_initial_value(self):
        self.assertEquals(52, self.single.map_reduce(None, operator.__add__,
                                                     initial=10))

    def test_singlethreaded_mapreduce_concat_no_initial_value(self):
        self.assertEquals(10, self.one_234.map_reduce(None, operator.__add__))

    def test_singlethreaded_mapreduce_concat_with_initial_value(self):
        self.assertEquals(20, self.one_234.map_reduce(None, operator.__add__,
                                                      initial=10))


if __name__ == '__main__':
    unittest.main()
