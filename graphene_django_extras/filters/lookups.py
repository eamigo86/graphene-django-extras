# -*- coding: utf-8 -*-
__all__ = (
    "ALL_LOOKUPS",
    "BASIC_LOOKUPS",
    "COMMON_LOOKUPS",
    "NUMBER_LOOKUPS",
    "DATETIME_LOOKUPS",
    "DATE_LOOKUPS",
    "TIME_LOOKUPS",
)


_all_lookups = (
    "isnull",
    "exact",
    "iexact",
    "contains",
    "icontains",
    "startswith",
    "istartswith",
    "endswith",
    "iendswith",
    "in",
    "gt",
    "gte",
    "lt",
    "lte",
    "range",
    "year",
    "month",
    "day",
    "week_day",
    "hour",
    "minute",
    "second",
)


ALL_LOOKUPS = _all_lookups
BASIC_LOOKUPS = _all_lookups[2:3] + _all_lookups[4:5]
COMMON_LOOKUPS = _all_lookups[0:10]
NUMBER_LOOKUPS = _all_lookups[9:15]
DATETIME_LOOKUPS = _all_lookups[9:]
DATE_LOOKUPS = _all_lookups[9:19]
TIME_LOOKUPS = _all_lookups[9:15] + _all_lookups[19:]
