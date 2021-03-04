# anupyutilities/initfuncs.py
# Copyright (C) 2021 AnuPyUtilities
# <see TUTHORS file>
#
# This module is part of AnuPyUtilities and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php


import logging
import time
import inspect
import itertools

from datetime import date, timedelta, datetime
from decimal import Decimal, InvalidOperation
from tzlocal import get_localzone
import argparse
import collections


def dict_deep_merge(dct, merge_dict):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dict`` is merged into
    ``dct``.
    origin from:
        https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
    :param dct: dict onto which the merge is executed
    :param merge_dict: dct merged into dct
    :return: None
    """
    for k, v in merge_dict.iteritems():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dict[k], collections.Mapping)):
            dict_deep_merge(dct[k], merge_dict[k])
        else:
            dct[k] = merge_dict[k]


def chunks(lst, n_size):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n_size):
        yield lst[i:i + n_size]


def timing(print_args=True, *print_arg_names):
    """print how mach time spend the function called.

    @timing
    def function_to_time():
        time.sleep(1)
    Args:
        print_args (bool): the print the args or not
    """
    def decorating_function(func):
        def _wrapper(*args, **kwargs):
            start = time.time()
            original_return_val = func(*args, **kwargs)
            end = time.time()
            if print_args:
                pnames = set(print_arg_names)
                if len(pnames) == 0:
                    logging.info("%s times used: %2.4f, args: %r, kwargs: %r",
                                 func.__name__, end - start, args, kwargs)
                else:
                    args_name = inspect.getfullargspec(func).args
                    args_tuples = zip(args_name, args)

                    filtered_kwargs = dict(
                        filter(lambda x: x[0] in pnames, kwargs.items()))
                    filtered_args = dict(
                        filter(lambda x: x[0] in pnames, args_tuples))
                    logging.info("%s times used: %2.4f, args: %r, kwargs: %r",
                                 func.__name__, end - start, filtered_args,
                                 filtered_kwargs)
            else:
                logging.info("%s times used: %2.4f", func.__name__,
                             end - start)
            return original_return_val

        return _wrapper

    return decorating_function


def str_decimal_normalize(num, fmt='{:.f}'):
    '''return string that reprensent a normalized decimal.
    This function would useful for the case that represent a decimal as string, for e.g, protobuf.
    :param num: could be a number or string that could be inited by the construction function of Decimal
        if not, an empty string '' will be returned.
    '''
    try:
        num = Decimal(num).normalize()
        return fmt.format(num)
    except:
        logging.error('can not convert to a Decimal object: {}, type: {}'.format(num, type(num)))
        return ''