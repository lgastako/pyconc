import threading


def identity(x):
    return x


class Empty(object):

    def __len__(self):
        return 0

    def to_list(self):
        return []

    def __repr__(self):
        return "Empty()"


class Singleton(object):

    def __init__(self, value):
        self.value = value

    def __len__(self):
        return 1

    def to_list(self):
        return [self.value]

    def __repr__(self):
        return "Singleton(%s)" % repr(self.value)


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

    def __repr__(self):
        return "Concat(%s, %s)" % (repr(self.left), repr(self.right))


class SingleThreadedMultiplexor(object):

    def map_reduce(self, clist, mapf, reducef, initial=None):
        if isinstance(clist, Empty):
            print "using empty map reducer"
            result = self._map_reduce_empty(clist, initial)
            print "returning result from empty: %s" % str(result)
            return result
        if isinstance(clist, Singleton):
            print "using singleton map reducer"
            result = self._map_reduce_singleton(clist, mapf, reducef, initial)
            print "returning result from singleton: %s" % str(result)
            return result
        if isinstance(clist, Concat):
            print "using concat map reducer"
            result = self._map_reduce_concat(clist, mapf, reducef, initial)
            print "returning result from concat: %s" % str(result)
            return result
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


class MassiveMultiThreadedMultiplexor(SingleThreadedMultiplexor):
    """You would pretty much never want to use this in production, but
    here we go for a quick test.

    """

    @staticmethod
    def _check_and_reduce_results(results, reducef):
        if "left_exception" in results:
            print "Left exception: %s" % results["left_exception"]
        if "right_exception" in results:
            print "Right exception: %s" % results["right_exception"]
        print "results: %s" % repr(results)
        result = reducef(results["left"], results["right"])
        print "Reduced result: %s" % str(result)
        return result

    def _map_reduce_concat(self, clist, mapf, reducef, initial):

        def sub_map_reduce(target, x_initial=None):
            return self.map_reduce(target, mapf, reducef, initial=x_initial)

        if clist.left and clist.right:
            results = {}

            def do_side(results, name, item, x_initial):
                print "do_side...item: %s" % repr(item)
                try:
                    results[name] = sub_map_reduce(item, x_initial=x_initial)
                except Exception, ex:
                    results[name + "_exception"] = ex
                print "returning results: %s" % repr(results)

            left_t = threading.Thread(target=do_side, args=(results,
                                                            "left",
                                                            clist.left,
                                                            initial))
            right_t = threading.Thread(target=do_side, args=(results,
                                                             "right",
                                                             clist.right,
                                                             None))
            threads = (left_t, right_t)
            for t in threads:
                t.start()
            for t in threads:
                if t.isAlive():
                    print "Waiting for t..."
                    t.join()

            return self._check_and_reduce_results(results, reducef)
        elif clist.left:
            result = sub_map_reduce(clist.left, x_initial=initial)
        elif clist.right:
            result = sub_map_reduce(clist.right, x_initial=initial)
        return result
