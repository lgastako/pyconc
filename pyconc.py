def identity(x):
    return x


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
        # TODO: No test case for this yet.
        # if right is None:
        #     right = Empty
        self.right = right

    def __len__(self):
        return len(self.left) + len(self.right)

    def to_list(self):
        return self.left.to_list() + self.right.to_list()


class SingleThreadedMultiplexor(object):

    def map_reduce(self, clist, mapf, reducef, initial=None):
        if isinstance(clist, Empty):
            return self._map_reduce_empty(clist, initial)
        if isinstance(clist, Singleton):
            return self._map_reduce_singleton(clist, mapf, reducef, initial)
        if isinstance(clist, Concat):
            return self._map_reduce_concat(clist, mapf, reducef, initial)
        raise TypeError("Unexpected clist type: %s" % clist.__class__.__name__)

    def _map_reduce_empty(self, clist, initial):
        if initial is not None:
            return initial
        raise TypeError("map_reduce() of empty sequence with no initial value")

    def _map_reduce_singleton(self, clist, mapf, reducef, initial):
        if mapf is None:
            mapf = identity
        result = mapf(clist.value)
        if initial:
            result = reducef(initial, result)
        return result

    def _map_reduce_concat(self, clist, mapf, reducef, initial):

        def sub_map_reduce(target, x_initial=None):
            return self.map_reduce(target, mapf, reducef, initial=x_initial)

        if clist.left and clist.right:
            result = reducef(sub_map_reduce(clist.left, x_initial=initial),
                             sub_map_reduce(clist.right))
        elif clist.left:
            result = sub_map_reduce(clist.left, x_initial=initial)
        elif clist.right:
            result = sub_map_reduce(clist.right, x_initial=initial)
        return result
