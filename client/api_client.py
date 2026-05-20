from flask import Flask, jsonify
import requests
import time
from circuit_breaker import CircuitBreaker
from circuit_breaker_state import CircuitBreakerState

app = Flask(__name__)

SERVER_URL = "http://localhost:8080"

class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            timeout_seconds=10
        )
        self.retry_count = 2

    def call_service(self, endpoint):
        def make_request():
            url = f"{self.base_url}{endpoint}"
            print(f"  [RETRY] Вызов сервера: {url}")
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
                    time.sleep(0.5)
                    continue
        raise last_exception

    def get_state(self):
        return self.circuit_breaker.state.value


server_client = ApiClient(SERVER_URL)

@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        result = server_client.call_service("/api/data")
        return jsonify({"data": result.get("data")}), 200
    except Exception as e:
        return jsonify({
            "error": str(e),
            "circuit_state": server_client.get_state()
        }), 503

@app.route('/admin/state', methods=['GET'])
def get_state():
    return jsonify({
        "circuit_breaker_state": server_client.get_state()
    }), 200

if __name__ == "__main__":
    app.run(host='localhost', port=8081, debug=False)