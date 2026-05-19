import threading
import time
import sys
import requests

sys.path.append('.')

from services import server_service, set_error_mode, set_error_rate
from services.api_client import start_client_api_service
from config import ServerConfig, ClientConfig, CircuitBreakerConfig


def run_server():
    server_service.start_server(ServerConfig.SERVER_PORT)


def run_client():
    start_client_api_service()


def demo_successful_requests():
    print("\nНОРМАЛЬНАЯ РАБОТА")

    set_error_mode(False)
    set_error_rate(0.0)

    client_url = f"http://{ClientConfig.CLIENT_HOST}:{ClientConfig.CLIENT_PORT}"

    for i in range(3):
        response = requests.get(f"{client_url}/api/data")
        result = response.json()
        print(f"Запрос {i + 1}: {result['data']}")
        time.sleep(5)


def demo_errors_with_retry():
    print("\nОШИБКИ С ПОВТОРАМИ")

    set_error_mode(True)
    set_error_rate(1.0)

    client_url = f"http://{ClientConfig.CLIENT_HOST}:{ClientConfig.CLIENT_PORT}"

    for i in range(2):
        print(f"\nЗапрос {i + 1}")

        response = requests.get(f"{client_url}/api/data")
        result = response.json()

        if 'error' in result:
            print(f"Результат: Ошибка - {result['error']}")
            print(f"Состояние CB: {result.get('circuit_state', 'unknown')}")
        else:
            print(f"Результат: {result['data']}")

        time.sleep(3)


def demo_circuit_breaker_opens():
    print("\nРАЗМЫКАНИЕ CIRCUIT BREAKER")

    set_error_mode(True)
    set_error_rate(1.0)

    client_url = f"http://{ClientConfig.CLIENT_HOST}:{ClientConfig.CLIENT_PORT}"

    for i in range(5):
        print(f"\nЗапрос {i + 1}")

        response = requests.get(f"{client_url}/api/data")
        result = response.json()

        if 'error' in result:
            print(f"Ошибка: {result['error']}")
            print(f"Состояние CB: {result.get('circuit_state', 'unknown')}")
        else:
            print(f"Успех: {result['data']}")

        time.sleep(3)


def demo_circuit_breaker_recovers():
    print("\nВОССТАНОВЛЕНИЕ")

    client_url = f"http://{ClientConfig.CLIENT_HOST}:{ClientConfig.CLIENT_PORT}"

    print("\n1. Ждем таймаут...")
    time.sleep(CircuitBreakerConfig.TIMEOUT_SECONDS + 2)

    print("\n2. Пробный запрос")
    set_error_mode(False)
    set_error_rate(0.0)

    response = requests.get(f"{client_url}/api/data")
    result = response.json()

    if 'error' not in result:
        print(f"   Успех: {result['data']}")
    else:
        print(f"   Ошибка: {result['error']}")

    response = requests.get(f"{client_url}/admin/state")
    state = response.json()
    print(f"   Состояние CB: {state.get('circuit_breaker_state', 'unknown')}")


if __name__ == "__main__":
    print("Запуск сервера (порт 8080)...")
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(2)

    print("Запуск клиентского сервиса (порт 8081)...")
    client_thread = threading.Thread(target=run_client, daemon=True)
    client_thread.start()
    time.sleep(2)

    print(f"Сервер: http://localhost:{ServerConfig.SERVER_PORT}")
    print(f"Клиент: http://localhost:{ClientConfig.CLIENT_PORT}")

    demo_successful_requests()
    demo_errors_with_retry()
    demo_circuit_breaker_opens()
    demo_circuit_breaker_recovers()