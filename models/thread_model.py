
class ThreadModel:

    def __init__(
            self,name=None, target=None, args=None,
            status=None, type=None, start_time=0, stop_time=0):
        self.name = name
        self.target = target
        self.args = args
        self.status = status
        self.type = type
        self._start_time = start_time
        self.stop_time = stop_time

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, start_time):
        self._start_time = start_time

