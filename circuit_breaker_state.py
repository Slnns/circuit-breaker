from enum import Enum

class CircuitBreakerState(Enum):
    CLOSED = "closed"       # Нормальное состояние
    OPEN = "open"           # Цепь разомкнута, запросы блокируются
    HALF_OPEN = "half_open" # Проверочное состояние