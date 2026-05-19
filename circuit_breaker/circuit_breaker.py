import time
from datetime import datetime
from .circuit_breaker_state import CircuitBreakerState

class CircuitBreaker:
    def __init__(self, failure_threshold=3, timeout_seconds=10):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None

    def call(self, func, *args, **kwargs):
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                print(f"  [DEBUG] Переход из OPEN в HALF_OPEN")
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise Exception("Circuit Breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        if self.state == CircuitBreakerState.HALF_OPEN:
            self._reset()
        elif self.state == CircuitBreakerState.CLOSED:
            self.failure_count = 0

    def _on_failure(self):
        if self.state == CircuitBreakerState.HALF_OPEN:
            self._transition_to_open()
        elif self.state == CircuitBreakerState.CLOSED:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self._transition_to_open()

    def _transition_to_open(self):
        if self.state != CircuitBreakerState.OPEN:
            self.state = CircuitBreakerState.OPEN
            self.last_failure_time = datetime.now()

    def _reset(self):
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None

    def _should_attempt_reset(self):
        if self.last_failure_time is None:
            return True
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.timeout_seconds