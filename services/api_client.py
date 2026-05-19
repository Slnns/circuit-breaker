# api_client.py
from flask import Flask, jsonify
import requests
import time
from circuit_breaker import CircuitBreaker
from config import ServerConfig, ClientConfig, CircuitBreakerConfig

app = Flask(__name__)



class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=CircuitBreakerConfig.FAILURE_THRESHOLD,
            timeout_seconds=CircuitBreakerConfig.TIMEOUT_SECONDS
        )
        self.retry_count = CircuitBreakerConfig.RETRY_COUNT

    def call_service(self, endpoint):
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
                    time.sleep(0.5)
                    continue

        raise last_exception

    def get_state(self):
        return self.circuit_breaker.state.value


# Создаем экземпляр клиента для вызова сервера
server_client = ApiClient(
    base_url=f"http://{ServerConfig.SERVER_HOST}:{ServerConfig.SERVER_PORT}"
)


@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        result = server_client.call_service("/api/data")
        return jsonify({
            "source": "client_service",
            "data": result
        }), 200
    except Exception as e:
        return jsonify({
            "source": "client_service",
            "error": str(e),
            "circuit_state": server_client.get_state()
        }), 503

@app.route('/admin/state', methods=['GET'])
def get_state():
    return jsonify({
        "circuit_breaker_state": server_client.get_state(),
        "failure_threshold": CircuitBreakerConfig.FAILURE_THRESHOLD,
        "timeout_seconds": CircuitBreakerConfig.TIMEOUT_SECONDS,
        "retry_count": CircuitBreakerConfig.RETRY_COUNT
    }), 200


def start_client_api_service():
    app.run(
        host=ClientConfig.CLIENT_HOST,
        port=ClientConfig.CLIENT_PORT,
        debug=False,
        use_reloader=False
    )


if __name__ == "__main__":
    start_client_api_service()