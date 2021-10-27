""" cache for an hour """
# Source: http://code.activestate.com/recipes/325905-memoize-decorator-with-timeout/#c1
import time
from functools import wraps
from typing import Any
from typing import Callable
from typing import Dict
from typing import Tuple


class TimedCache:
    """ Memoize With Timeout """

    _caches: Dict[
        Callable,  # function as a key
        Dict[
            tuple,  # key build from args and kwargs
            Tuple[Any, int],  # result and last invoke time
        ],
    ] = {}

    def __init__(self, timeout=2):
        self.timeout = timeout

    def flush(self, *args, **kwargs):
        """Clear cache of results which have timed out"""
        # args and kwargs need for calling it in job_queue
        request_time = time.time()

        for func in self._caches:  # iterate functions
            cache = {}

            for func_key in self._caches[func]:  # iterate results
                # skip old results
                if (request_time - self._caches[func][func_key][1]) < self.timeout:
                    cache[func_key] = self._caches[func][func_key]

            # replace old cahce with filtered one
            self._caches[func] = cache

    def __call__(self, func):
        # initializes functions on script start
        cache = self._caches[func] = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            """ called straight as the function triggered """

            key_words = sorted(kwargs.items())
            func_key = (args, tuple(key_words))
            request_time = time.time()

            try:
                value = cache[func_key]
                if (request_time - value[1]) > self.timeout:
                    raise KeyError
            except KeyError:
                value = cache[func_key] = func(*args, **kwargs), request_time

            return value[0]

        return wrapper


cached = TimedCache(timeout=60 * 30)  # 30 minutes timeout
