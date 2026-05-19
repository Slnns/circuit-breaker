import requests
from circuit_breaker import CircuitBreaker


class ApiClient:
    def __init__(self, base_url, retry_count=2):
        self.base_url = base_url
        self.retry_count = retry_count
        self.circuit_breaker = CircuitBreaker(timeout_seconds=10)

    def call_service(self, endpoint="/api/data"):
        def make_request():
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, timeout=5)

            if response.status_code >= 500:
                raise Exception(f"Server error: {response.status_code}")

            return response.json()

        last_exception = None

        for attempt in range(self.retry_count + 1):
            try:
                result = self.circuit_breaker.call(make_request)
                return result
            except Exception as e:
                last_exception = e
                if attempt < self.retry_count:
                    continue

        raise last_exception

    def get_state(self):
        return self.circuit_breaker.state.value