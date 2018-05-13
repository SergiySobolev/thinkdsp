def find_index(self, t):
    """Find the index corresponding to a given time."""
    n = len(self)
    start = self.start
    end = self.end
    i = round((n - 1) * (t - start) / (end - start))
    return int(i)


def find_index_s(x, xs):
    """Find the index corresponding to a given value in an array."""
    n = len(xs)
    start = xs[0]
    end = xs[-1]
    i = round((n - 1) * (x - start) / (end - start))
    return int(i)