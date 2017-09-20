# -*- coding: utf-8 -*-

all_lookups = ('isnull', 'exact', 'iexact', 'contains', 'icontains', 'startswith', 'istartswith', 'endswith',
               'iendswith', 'in', 'gt', 'gte', 'lt', 'lte', 'range', 'year', 'month', 'day', 'week_day', 'hour',
               'minute', 'second', )


filter_dict = {
    'all': all_lookups,
    'common': all_lookups[0:10],
    'number': all_lookups[9:15],
    'datetime': all_lookups[9:],
    'date':  all_lookups[9:19],
    'time': all_lookups[9:15] + all_lookups[19:]
}
