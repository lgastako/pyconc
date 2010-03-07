def identity(x):
    return x


class Empty(object):

    def __len__(self):
        return 0

    def to_list(self):
        return []

    def map_reduce(self, _mapf, _reducef, initial=None, multiplexor=None):
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

    def map_reduce(self, mapf, reducef, initial=None, multiplexor=None):
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
