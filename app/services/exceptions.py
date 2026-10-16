# Базовая ошибка клиента Deribit. Сборщик ловит именно её ему всё равно упала сеть
# или биржа вернула мусор, в обоих случаях тикер пропускается
# Подклассы нужны для логов и тестов
class DeribitError(Exception):
    pass


# Не удалось получить ответ: сеть, таймаут, не-200 статус
class DeribitTransportError(DeribitError):
    pass


# Биржа ответила JSON-RPC ошибкой: {"error": {"code": ..., "message": ...}}
class DeribitApiError(DeribitError):
    def __init__(self, method: str, code: int | None, message: str):
        super().__init__(f"{method}: [{code}] {message}")
        self.method = method
        self.code = code
        self.message = message


# Ответ 200 но поля result.index_price в нём нет
class DeribitResponseError(DeribitError):
    pass
