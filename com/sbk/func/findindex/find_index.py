def find_index(self, t):
    """Find the index corresponding to a given time."""
    n = len(self)
    start = self.start
    end = self.end
    i = round((n - 1) * (t - start) / (end - start))
    return int(i)