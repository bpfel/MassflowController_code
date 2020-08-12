from threading import Timer
import logging

logger = logging.getLogger("root")


class RepeatTimer(Timer):
    """
    This class allows to run a timer repeatedly.

    Usage:

        def dummyfn(msg="foo"):
            print(msg)

        timer = RepeatTimer(1, dummyfn)
        timer.start()
        time.sleep(5)
        timer.cancel()
    """

    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)
