import logging


class ExceptionHandler:
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger

    def handle_exeption(self, default=None):
        '''Функция для обработки и логгирования исключений. Если произошло исключение, то возвращает `deafult`'''
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except BaseException as error:
                    if self.logger:
                        log = f"{error}; In {func.__name__} with {args} {kwargs}"
                        self.logger.exception(log)
                    return default
            return wrapper
        return decorator

