import threading
import time
import sys

sys.path.append('.')

from services import server_service
from services.api_client import ApiClient
from config import ServerConfig, CircuitBreakerConfig


def run_server():
    server_service.start_server(ServerConfig.SERVER_PORT)


def demo_successful_requests(api_client):
    print("\n нормальная работа")

    server_service.set_error_mode(False)
    server_service.set_error_rate(0.0)

    for i in range(3):
        result = api_client.call_service()
        print(f"Запрос {i + 1}: данные - {result['data']}")
        time.sleep(0.5)


def demo_errors_with_retry(api_client):
    print("\n ошибки, но с повторами")

    server_service.set_error_mode(True)
    server_service.set_error_rate(1.0)

    for i in range(2):
        print(f"\nЗапрос {i + 1}")
        print(f"Состояние: {api_client.get_state()}")

        try:
            result = api_client.call_service()
            print(f"Результат: {result}")
        except Exception as e:
            print(f"Результат: Ошибка - {e}")

        print(f"Состояние после: {api_client.get_state()}")
        time.sleep(1)


def demo_circuit_breaker_opens(api_client):
    print("\n размыкание")

    server_service.set_error_mode(True)
    server_service.set_error_rate(1.0)

    for i in range(5):
        print(f"\nЗапрос {i + 1}")
        print(f"Состояние: {api_client.get_state()}")

        try:
            result = api_client.call_service()
            print(f"Результат: {result}")
        except Exception as e:
            print(f"Результат: {e}")

        time.sleep(1)


def demo_circuit_breaker_recovers(api_client):
    print("\n восстановление")
    server_service.set_error_mode(True)
    server_service.set_error_rate(1.0)

    for i in range(4):
        try:
            api_client.call_service()
        except:
            pass
        time.sleep(0.5)

    print("\n2: Ждем таймаут 10 секунд")
    for i in range(10):
        time.sleep(1)
        print(f" прошло {i+1} сек", end="\r")

    print(f"\n Состояние после таймаута: {api_client.get_state()}")

    print("\n3: Пробный запрос")
    server_service.set_error_mode(False)
    server_service.set_error_rate(0.0)

    print(f" Состояние до запроса: {api_client.get_state()}")

    try:
        result = api_client.call_service()
        print(f" Успех - {result['data']}")
        print(f" Закрылся: {api_client.get_state()}")
    except Exception as e:
        print(f" Ошибка: {e}")


if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(2)

    api_client = ApiClient(
        base_url=f"http://{ServerConfig.SERVER_HOST}:{ServerConfig.SERVER_PORT}",
        retry_count=CircuitBreakerConfig.RETRY_COUNT
    )

    demo_successful_requests(api_client)
    demo_errors_with_retry(api_client)
    demo_circuit_breaker_opens(api_client)
    demo_circuit_breaker_recovers(api_client)