"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
# adapted from https://github.com/pydata/pandas/blob/master/pandas/tseries/tools.py
from datetime import datetime, timedelta
import re
import sys
from StringIO import StringIO
import logging

import dateutil
from dateutil.parser import parse, DEFAULTPARSER

log = logging.getLogger(__name__)

# raise exception if dateutil 2.0 install on 2.x platform
if (sys.version_info[0] == 2 and
            dateutil.__version__ == '2.0'):  # pragma: no cover
    raise Exception('dateutil 2.0 incompatible with Python 2.x, you must '
                    'install version 1.5 or 2.1+!')
# otherwise a 2nd import won't show the message

_DATEUTIL_LEXER_SPLIT = None
try:
    # Since these are private methods from dateutil, it is safely imported
    # here so in case this interface changes, pandas will just fallback
    # to not using the functionality
    from dateutil.parser import _timelex

    if hasattr(_timelex, 'split'):
        def _lexer_split_from_str(dt_str):
            # The StringIO(str(_)) is for dateutil 2.2 compatibility
            return _timelex.split(StringIO(str(dt_str)))

        _DATEUTIL_LEXER_SPLIT = _lexer_split_from_str
except (ImportError, AttributeError):
    pass


def _guess_datetime_format(dt_str, parsed_datetime, dayfirst,
                           dt_str_split=_DATEUTIL_LEXER_SPLIT):
    """
    Guess the datetime format of a given datetime string.

    Parameters
    ----------
    dt_str : string, datetime string to guess the format of
    parsed_datetime : result of dateutil.parser.parse
    dayfirst : boolean, default True
        If True parses dates with the day first, eg 20/01/2005
        Warning: dayfirst=True is not strict, but will prefer to parse
        with day first (this is a known bug).
    dt_str_split : function, defaults to `_DATEUTIL_LEXER_SPLIT` (dateutil)
        This function should take in a datetime string and return
        a list of strings, the guess of the various specific parts
        e.g. '2011/12/30' -> ['2011', '/', '12', '/', '30']

    Returns
    -------
    ret : datetime format string (for `strftime` or `strptime`)
    """
    log.debug('_guess_datetime_format, dt_str={0}'.format(dt_str))
    if dt_str_split is None:
        return None

    if not isinstance(dt_str, basestring):
        return None

    day_attribute_and_format = (('day',), '%d')

    datetime_attrs_to_format = [
        (('year', 'month', 'day'), '%Y%m%d'),
        (('year',), '%Y'),
        (('month',), '%B'),
        (('month',), '%b'),
        (('month',), '%m'),
        day_attribute_and_format,
        (('hour',), '%H'),
        (('minute',), '%M'),
        (('second',), '%S'),
        (('microsecond',), '%f'),
        (('second', 'microsecond'), '%S.%f'),
    ]

    if dayfirst:
        datetime_attrs_to_format.remove(day_attribute_and_format)
        datetime_attrs_to_format.insert(0, day_attribute_and_format)

    if parsed_datetime is None:
        return None

    try:
        log.debug('dt_str_split(dt_str)')
        tokens = dt_str_split(dt_str)
    except:
        # In case the datetime string can't be split, its format cannot
        # be guessed
        return None
    log.debug('split tokens={0}'.format(tokens))
    format_guess = [None] * len(tokens)
    found_attrs = set()

    for attrs, attr_format in datetime_attrs_to_format:
        # If a given attribute has been placed in the format string, skip
        # over other formats for that same underlying attribute (IE, month
        # can be represented in multiple different ways)
        if set(attrs) & found_attrs:
            continue

        if all(getattr(parsed_datetime, attr) is not None for attr in attrs):
            for i, token_format in enumerate(format_guess):
                if (token_format is None and
                            tokens[i] == parsed_datetime.strftime(attr_format)):
                    format_guess[i] = attr_format
                    found_attrs.update(attrs)
                    break
    log.debug('found_attrs={0}'.format(found_attrs))
    log.debug('format_guess={0}'.format(format_guess))
    # Only consider it a valid guess if we have a year, month and day
    if len(set(['year', 'month', 'day']) & found_attrs) != 3:
        return None

    output_format = []
    for i, guess in enumerate(format_guess):
        if guess is not None:
            # Either fill in the format placeholder (like %Y)
            output_format.append(guess)
        else:
            # Or just the token separate (IE, the dashes in "01-01-2013")
            try:
                # If the token is numeric, then we likely didn't parse it
                # properly, so our guess is wrong
                if float(tokens[i]) != 0.0:
                    return None
            except ValueError:
                pass

            output_format.append(tokens[i])

    guessed_format = ''.join(output_format)

    if parsed_datetime.strftime(guessed_format) == dt_str:
        return guessed_format


has_time = re.compile('(.+)([\s]|T)+(.+)')


def parse_date_string(date_str, dayfirst=False, yearfirst=True):
    """
    Try hard to parse datetime string, leveraging dateutil plus some extras

    Parameters
    ----------
    arg : date string
    dayfirst : bool, 
    yearfirst : bool

    Returns
    -------
    datetime, datetime format string (for `strftime` or `strptime`)
    or None if unable parse date str
    """

    if not isinstance(date_str, basestring):
        return None

    arg = date_str.upper()

    parse_info = DEFAULTPARSER.info
    if len(arg) in (7, 8):
        mresult = _attempt_monthly(arg)
        log.debug('mresult={0}'.format(mresult))
        if mresult:
            return mresult

    parsed_datetime = DEFAULTPARSER.parse(StringIO(str(arg)), dayfirst=dayfirst,
                                          yearfirst=yearfirst, fuzzy=True)
    log.debug('parsed_datetime={0}'.format(parsed_datetime))
    if parsed_datetime:
        date_format = _guess_datetime_format(date_str, parsed_datetime,
                                             dayfirst=dayfirst)
    return parsed_datetime, date_format


def _attempt_monthly(val):
    pats = ['%Y-%m', '%m-%Y', '%b %Y', '%b-%Y']
    for pat in pats:
        try:
            ret = datetime.strptime(val, pat)
            return ret, pat
        except Exception:
            pass
