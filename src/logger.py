import sys
import asyncio

from loguru import logger
from functools import wraps

# Logging
logger.add(
    sys.stderr,
    colorize=True,
    format='<blue>{time}</blue> <green>{level}</green> <red>{message}</red>',
    filter='my_module',
    level='INFO',
)
logger.add(f'./logs/file_1.log', rotation='100 MB', compression='zip')

# Decorator
def decorate_logging(fn):
    """
        Decorator for logging
    """
    if asyncio.iscoroutinefunction(fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            try:
                return await fn(*args, **kwargs)
            except Exception as exc:
                logger.patch(lambda r: r.update(function=fn.__name__)).error(f'({fn.__doc__}) - {exc}')
        return wrapper
    else:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                logger.patch(lambda r: r.update(function=fn.__name__, message=exc)).error(f'({fn.__doc__}) - {exc}')
        return wrapper
