from logging import Logger


def exception_handler(logger: Logger=None, default=None):
    '''Функция для обработки и логгирования исключений. Если произошло исключение, то возвращает `deafult`'''
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except BaseException as error:
                if logger:
                    if '.' in func.__qualname__:
                        args = args[1::]
                    log = f"{error}; In {func.__qualname__} with {args} {kwargs}"
                    logger.exception(log)
                return default
        return wrapper
    return decorator

