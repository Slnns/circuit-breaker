class CircuitBreakerConfig:
    FAILURE_THRESHOLD = 3      # Количество ошибок для размыкания
    TIMEOUT_SECONDS = 10       # Время ожидания перед полуоткрытым состоянием
    RETRY_COUNT = 2            # Количество повторных попыток

class ServerConfig:
    SERVER_HOST = "localhost"
    SERVER_PORT = 8080         # Порт реального сервера с данными

class ClientConfig:
    CLIENT_HOST = "localhost"
    CLIENT_PORT = 8081         # Порт клиентского сервиса (API gateway)