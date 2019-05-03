
class ThreadModel:

    def __init__(
            self,name=None, target=None, args=None,
            status=None, type=None, start_time=0, stop_time=0, thread_referance=''):
        self.name = name
        self.target = target
        self.args = args
        self.status = status
        self.type = type
        self._start_time = start_time
        self.stop_time = stop_time
        self._thread_referance = thread_referance

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, start_time):
        self._start_time = start_time

    @property
    def thread_referance(self):
        return self._thread_referance

    @thread_referance.setter
    def thread_referance(self, thread_referance):
        self._thread_referance= thread_referance
