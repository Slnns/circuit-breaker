# Circuit Breaker Pattern Implementation

Реализация паттерна Circuit Breaker на Python для защиты распределенных систем от каскадных отказов.

## Описание

Проект демонстрирует работу паттерна Circuit Breaker на примере двух сервисов:
- Клиентский сервис (HTTP клиент с Circuit Breaker)
- Серверный сервис (Cервер)

## Способ использования
- Запустить server_service.py и api_client.py
- При остановке сервера, проверить работоспособнось Circuit Breaker через запросы