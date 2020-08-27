from threading import Timer
import logging

logger = logging.getLogger("root")


class RepeatTimer(Timer):
    """
    The RepeatTimer is a special type of timer thread that can be run indefinitely and executes a given function
    each time a specified interval has passed.

    .. note::

       Example of usage:

          .. code-block:: python

             def dummyfn(msg="foo"):
                 print(msg)

             timer = RepeatTimer(interval=1, function=dummyfn)
             timer.start()
             time.sleep(5)  # During which 5 calls of dummyfn will happen.
             timer.cancel()
          """

    def run(self) -> None:
        """
        Method representing the thread’s activity.

        Overrides `Timer.run` such that we have a repeated timer.
        """
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)
