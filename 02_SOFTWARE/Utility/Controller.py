from collections import deque
from threading import RLock


class p_controller:
    def __init__(self, k_p, upper_limit=None, lower_limit=None):
        self.k_p = k_p
        self._upper_limit = upper_limit
        self._lower_limit = lower_limit
        self._val_buf = None
        self._lock = RLock()

    def assign_buffers(self, value_buffer):
        self._val_buf = value_buffer

    def update(self, target_value=0):
        u = self.k_p * (target_value - self._val_buf[-1])

        # hard limits on u
        if self._lower_limit is not None and u < self._lower_limit:
            u = self._lower_limit
        elif self._upper_limit is not None and u > self._upper_limit:
            u = self._upper_limit

        return u

    def set_k_p(self, value):
        value = float(value)
        if value < 0:
            raise ValueError('K_p has to be larger zero.')
        with self._lock:
            self.k_p = value

    def set_k_i(self, value):
        pass

    def set_k_d(self, value):
        pass


class pid_controller:
    def __init__(self, k_p, k_i, k_d, tau, t_s, upper_limit=None, lower_limit=None):

        # switch sign of d part to correct for sign error
        self.k_p = k_p
        self.k_i = k_i
        self.k_d = -k_d
        self.tau = tau
        self.t_s = t_s
        self._b0_a0 = 0
        self._b1_a0 = 0
        self._b2_a0 = 0
        self._a1_a0 = 0
        self._a2_a0 = 0
        self._lock = RLock()
        self.calculate_coefficients()

        self._val_buf = None
        self._u = deque([0, 0], maxlen=2)
        self._e_val_buf = deque([0, 0, 0], maxlen=3)
        self._lower_limit = lower_limit
        self._upper_limit = upper_limit

    def calculate_coefficients(self):
        with self._lock:
            self._b0_a0 = (self.k_p * (1 + self.tau * self.t_s) +
                           self.k_i * self.t_s * (1 + self.tau * self.t_s) +
                           self.k_d * self.tau
                           ) / (1 + self.tau * self.t_s)
            self._b1_a0 = -(self.k_p * (2 + self.tau * self.t_s) +
                            self.k_i * self.t_s + 2 * self.k_d * self.tau
                            ) / (1 + self.tau * self.t_s)
            self._b2_a0 = (self.k_p + self.k_d * self.tau) / (1 + self.tau * self.t_s)
            self._a1_a0 = -(2 + self.tau * self.t_s) / (1 + self.tau * self.t_s)
            self._a2_a0 = 1 / (1 + self.tau * self.t_s)

    def assign_buffers(self, value_buffer):
        self._val_buf = value_buffer

    def update(self, target_value=0):
        # Update coefficients
        self.calculate_coefficients()

        # Update errors:
        self._e_val_buf.appendleft(target_value - self._val_buf[-1])

        u = -self._a1_a0 * self._u[0] - self._a2_a0 * self._u[1] \
            + self._b0_a0 * self._e_val_buf[0] + self._b1_a0 * self._e_val_buf[1] \
            + self._b2_a0 * self._e_val_buf[2]

        # hard limits on u
        if self._lower_limit is not None and u < self._lower_limit:
            u = self._lower_limit
        elif self._upper_limit is not None and u > self._upper_limit:
            u = self._upper_limit

        self._u.appendleft(u)

        return u

    def set_k_p(self, value):
        value = float(value)
        if value < 0:
            raise ValueError('K_p has to be larger zero.')
        with self._lock:
            self.k_p = value

    def set_k_i(self, value):
        value = float(value)
        if value < 0:
            raise ValueError('K_i has to be larger zero.')
        with self._lock:
            self.k_i = value

    def set_k_d(self, value):
        value = -float(value)
        # Inverted sign
        if value > 0:
            raise ValueError('K_d has to be larger zero.')
        with self._lock:
            self.k_d = value
