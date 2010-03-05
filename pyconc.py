import unittest

from copy import copy


class Empty(object):

    def __len__(self):
        return 0

    def to_list(self):
        return []


class Singleton(object):

    def __init__(self, value):
        self.value = value

    def __len__(self):
        return 1

    def to_list(self):
        return [self.value]


class Concat(object):

    def __init__(self, left, right=None):
        self.left = left
        # if right is None:
        #     right = Empty
        self.right = right

    def __len__(self):
        return len(self.left) + len(self.right)

    def to_list(self):
        return self.left.to_list() + self.right.to_list()


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


if __name__ == '__main__':
    unittest.main()
