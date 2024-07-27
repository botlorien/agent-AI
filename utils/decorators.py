import logging
import time
from functools import wraps


class TimeoutException(Exception):
    pass


def time_out(time_out: int = 20, raise_exception: bool = True,show_exception:bool=False,delay:int=1,**kwargsv):
    """
    Decorator that makes a function repeat its execution until a given timeout limit
    is reached, if necessary. If the function runs without raising exceptions before
    the timeout, it is not repeated.

    :param time_out: Time limit until the function is stopped, defaults to 20
    :type time_out: int, optional
    :param raise_exception: Whether to raise an exception after timeout, defaults to False
    :type raise_exception: bool, optional
    """
    def wrapper(func):
        def inner_wrapper(*args, **kwargs):
            contador_time_out = 0
            ret = False
            error = None
            while contador_time_out < time_out:
                if 'verbose' in kwargsv:
                    print('#' * 20, func.__name__, '#' * 20)
                    print('_' * 20, 'args', '_' * 20)
                    print(args)
                    print('_' * 20, 'kwargs', '_' * 20)
                    print(kwargs)
                try:
                    ret = func(*args, **kwargs)
                    break
                except Exception as e:
                    error = e
                    if show_exception:
                        logging.exception(error)
                    time.sleep(delay)
                contador_time_out += 1

                if contador_time_out >= time_out and raise_exception:
                    raise error
            return ret

        return inner_wrapper

    return wrapper

def timeit(number_times: int = 1):
    def wrapper(func):
        def inner_wrapper(*args, **kwargs):
            ret = False
            start_time = time.perf_counter()
            for _ in range(number_times):
                ret = func(*args, **kwargs)
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
            print(f"The function took {elapsed_time} seconds to complete.")
            return ret

        return inner_wrapper

    return wrapper

def try_params_if_error(**kwargsv):
    def wrapper(func):
        def inner_wrapper(*args, **kwargs):
            ret = False
            error = False
            for key in kwargsv:
                if any(isinstance(kwargsv[key],var) for var in (set,list,tuple,dict)):
                    for value in kwargsv[key]:
                        try:
                            kwargs[key]=value
                            ret = func(*args, **kwargs)
                            break
                        except Exception as e:
                            error = e
                    if ret:
                        break
                if isinstance(kwargsv[key],str):
                    try:
                        kwargs[key] = kwargsv[key]
                        ret = func(*args, **kwargs)
                        break
                    except Exception as e:
                        error = e
            if error:
                 raise error
            return ret

        return inner_wrapper

    return wrapper