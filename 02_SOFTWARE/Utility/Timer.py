from threading import Timer
import logging

logger = logging.getLogger("root")


class RepeatTimer(Timer):
    """
    RepeatTimer allows to run a timer repeatedly.

    .. note::

       The RepeatTimer can be used as follows:

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
