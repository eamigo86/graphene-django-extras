# -*- coding: utf-8 -*-
import time as t
from datetime import date, datetime, timedelta, time

import six
from dateutil import parser, relativedelta
from django.utils import timezone
from graphql import GraphQLArgument, GraphQLString

from .base import BaseExtraGraphQLDirective
from ..base_types import CustomDateFormat

__all__ = ("DateGraphQLDirective",)


DEFAULT_DATE_FORMAT = "%d %b %Y %H:%M:%S"
FORMATS_MAP = {
    # Year
    "YYYY": "%Y",
    "YY": "%y",
    # Week of year
    "WW": "%U",
    "W": "%W",
    # Day of Month
    # 'D': '%-d',  # Platform specific
    "DD": "%d",
    # Day of Year
    # 'DDD': '%-j',  # Platform specific
    "DDDD": "%j",
    # Day of Week
    "d": "%w",
    "ddd": "%a",
    "dddd": "%A",
    # Month
    # 'M': '%-m',  # Platform specific
    "MM": "%m",
    "MMM": "%b",
    "MMMM": "%B",
    # Hour
    # 'H': '%-H',  # Platform specific
    "HH": "%H",
    # 'h': '%-I',  # Platform specific
    "hh": "%I",
    # Minute
    # 'm': '%-M',  # Platform specific
    "mm": "%M",
    # Second
    # 's': '%-S',  # Platform specific
    "ss": "%S",
    # AM/PM
    # 'a': '',
    "A": "%p",
    # Timezone
    "ZZ": "%z",
    "z": "%Z",
}


def str_in_dict_keys(s, d):
    for k in d:
        if s in k:
            return True
    return False


def _combine_date_time(d, t):
    if (d is not None) and (t is not None):
        return datetime(d.year, d.month, d.day, t.hour, t.minute, t.second)
    return None


def _parse(partial_dt):
    """
    parse a partial datetime object to a complete datetime object
    """
    dt = None
    try:
        if isinstance(partial_dt, datetime):
            dt = partial_dt
        if isinstance(partial_dt, date):
            dt = _combine_date_time(partial_dt, time(0, 0, 0))
        if isinstance(partial_dt, time):
            dt = _combine_date_time(date.today(), partial_dt)
        if isinstance(partial_dt, (int, float)):
            dt = datetime.fromtimestamp(partial_dt)
        if isinstance(partial_dt, (str, bytes)):
            dt = parser.parse(partial_dt, default=timezone.now())

        if dt is not None and timezone.is_naive(dt):
            dt = timezone.make_aware(dt)
        return dt
    except ValueError:
        return None


def _format_relativedelta(rdelta, full=False, two_days=False, original_dt=None):
    if not isinstance(rdelta, relativedelta.relativedelta):
        raise ValueError("rdelta must be a relativedelta instance")
    keys = ("years", "months", "days", "hours", "minutes", "seconds")
    result = []
    flag = None

    if two_days and original_dt:
        if rdelta.years == 0 and rdelta.months == 0:
            days = rdelta.days
            if days == 1:
                return None, "Tomorrow"
            if days == -1:
                return None, "Yesterday"
            if days == 0:
                full = False
            else:
                return None, original_dt.strftime("%b %d, %Y")
        else:
            return None, original_dt.strftime("%b %d, %Y")

    for k, v in rdelta.__dict__.items():
        if k in keys and v != 0:
            if flag is None:
                flag = True if v > 0 else False
            key = k
            abs_v = abs(v)
            if abs_v == 1:
                key = key[:-1]
            if not full:
                return flag, "{} {}".format(abs_v, key)
            else:
                result.append("{} {}".format(abs_v, key))
    if len(result) == 0:
        return None, "Now" if two_days else None, "just now"
    if len(result) > 1:
        temp = result.pop()
        result = "{} and {}".format(", ".join(result), temp)
    else:
        result = result[0]

    return flag, result


def _format_time_ago(dt, now=None, full=False, ago_in=False, two_days=False):

    if not isinstance(dt, timedelta):
        if now is None:
            now = timezone.localtime(
                timezone=timezone.get_fixed_timezone(-int(t.timezone / 60))
            )

        original_dt = dt
        dt = _parse(dt)
        now = _parse(now)

        if dt is None:
            raise ValueError(
                "The parameter `dt` should be datetime timedelta, or datetime formatted string."
            )
        if now is None:
            raise ValueError(
                "the parameter `now` should be datetime, or datetime formatted string."
            )

        result = relativedelta.relativedelta(dt, now)
        flag, result = _format_relativedelta(result, full, two_days, original_dt)
        if ago_in and flag is not None:
            result = "in {}".format(result) if flag else "{} ago".format(result)
        return result


def _format_dt(dt, format="default"):
    if not dt:
        return None

    format_lowered = format.lower()

    if format_lowered == "default":
        return dt.strftime(DEFAULT_DATE_FORMAT)

    if format_lowered == "time ago":
        return _format_time_ago(dt, full=True, ago_in=True)

    if format_lowered == "time ago 2d":
        return _format_time_ago(dt, full=True, ago_in=True, two_days=True)

    if format_lowered == "iso":
        return dt.strftime("%Y-%b-%dT%H:%M:%S")

    if format_lowered in ("js", "javascript"):
        return dt.strftime("%a %b %d %Y %H:%M:%S")

    if format in FORMATS_MAP:
        return dt.strftime(FORMATS_MAP[format])

    else:
        temp_format = ""
        translate_format_list = []
        for char in format:
            if not char.isalpha():
                if temp_format != "":
                    translate_format_list.append(FORMATS_MAP.get(temp_format, ""))
                    temp_format = ""
                translate_format_list.append(char)
            else:
                if str_in_dict_keys("{}{}".format(temp_format, char), FORMATS_MAP):
                    temp_format = "{}{}".format(temp_format, char)
                else:
                    if temp_format != "":
                        if temp_format in FORMATS_MAP:
                            translate_format_list.append(
                                FORMATS_MAP.get(temp_format, "")
                            )
                        else:
                            return None
                    if str_in_dict_keys(char, FORMATS_MAP):
                        temp_format = char
                    else:
                        return None

        if temp_format != "":
            if temp_format in FORMATS_MAP:
                translate_format_list.append(FORMATS_MAP.get(temp_format, ""))
            else:
                return None

        format_result = "".join(translate_format_list)
        if format_result:
            return dt.strftime("".join(translate_format_list))
        return None


class DateGraphQLDirective(BaseExtraGraphQLDirective):
    """
    Format the date from resolving the field by dateutil module.
    """

    @staticmethod
    def get_args():
        return {
            "format": GraphQLArgument(
                type_=GraphQLString, description="A format given by dateutil module"
            )
        }

    @staticmethod
    def resolve(value, directive, root, info, **kwargs):
        format_argument = [
            arg for arg in directive.arguments if arg.name.value == "format"
        ]
        format_argument = format_argument[0] if len(format_argument) > 0 else None

        custom_format = format_argument.value.value if format_argument else "default"
        dt = _parse(value)
        try:
            result = _format_dt(dt, custom_format)
            if isinstance(value, six.string_types):
                return result or value
            return CustomDateFormat(result or "INVALID FORMAT STRING")
        except ValueError:
            return CustomDateFormat("INVALID FORMAT STRING")
