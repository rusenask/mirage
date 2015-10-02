"""
    stubo.ext
    ~~~~~~~~~
    
    Interface to user extensions (Exits)
     
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
from datetime import date, datetime, timedelta
import logging
from lxml import etree
from .parse_date import parse_date_string

log = logging.getLogger(__name__)

eye_catcher = "'***'"


def strip_encoding(xml):
    return xml.replace('encoding="UTF-8"',
                       '').replace('encoding="utf-8"', '').lstrip()


def parse_xml(xml):
    try:
        xml = xml.lstrip()
        doc = etree.fromstring(xml)
    except ValueError, err:
        # unicode strings with encoding declaration are not supported.
        utf8_bytes = xml.encode('utf-8')
        doc = etree.fromstring(utf8_bytes)
    return doc


def today_str(fmt="%d%m%y"):
    return date.today().strftime(fmt)


def roll_date(date_str, recorded, played):
    """ 
    Roll date part only based on the following:
    delta = ``recorded`` - parse_date(``date_str``)
    rolled_date = ``played`` - delta
    add time part from date_str to rolled_date
    return rolled_date as a string in the same format as ``date_str`` 
    """
    log.debug("roll '{0}', recorded={1}, played={2}".format(date_str, recorded,
                                                            played))
    day_first = False
    year_first = True

    parsed_date, date_format = parse_date_string(date_str, day_first, year_first)
    log.debug('parsed_date={0}, format={1}'.format(parsed_date, date_format))
    if not all((parsed_date, date_format)):
        return date_str

    delta = recorded - parsed_date.date()
    log.debug('delta={0} days'.format(delta))
    rolled_date = played - delta
    # add time back on
    rolled_date = datetime.combine(rolled_date, parsed_date.time())
    log.debug('rolled date={0}'.format(rolled_date))
    return rolled_date.strftime(date_format)
