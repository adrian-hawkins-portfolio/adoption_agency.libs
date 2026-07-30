from functools import wraps
from typing import Type, Callable
import inspect

from adoption_agency_common.saga_manager.saga_node import message_handlers


def handle(message_to_handle: Type = None):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper._is_registered = True
        assert message_to_handle is not None
        wrapper.message_to_handle = message_to_handle
        return wrapper
    return decorator


def saga(cls: Type):
    for attr_name, attr_value in cls.__dict__.items():
        if hasattr(attr_value, "_is_registered"):
            unwrapped_func = inspect.unwrap(attr_value)
            message_handlers[attr_value.message_to_handle.get_message_name(attr_value.message_to_handle)] = {
                'cls': cls,
                'message_class': attr_value.message_to_handle,
                'method': attr_name,
                'is_async': inspect.iscoroutinefunction(unwrapped_func)
            }

    return cls