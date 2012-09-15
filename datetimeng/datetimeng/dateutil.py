# These all take dt arguments of type date or datetime, and those that
# return a date-like result return one of the same type as the input dt.

import datetime

MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY = range(7)

(JANUARY, FEBRUARY, MARCH, APRIL, MAY, JUNE,
 JULY, AUGUST, SEPTEMBER, OCTOBER, NOVEMBER, DECEMBER) = range(1, 13)

_DAY = datetime.timedelta(1)


def is_leap_year(dt):
    """True if date in a leap year, False if not.

    >>> for year in 1900, 2000, 2100, 2001, 2002, 2003, 2004:
    ...     print year, is_leap_year(datetime.date(year, 1, 1))
    1900 False
    2000 True
    2100 False
    2001 False
    2002 False
    2003 False
    2004 True
    """

    return (datetime.date(dt.year, 2, 28) + _DAY).month == 2

def days_in_month(dt):
    """Total number of days in date's month.

    >>> for y in 2000, 2001:
    ...     print y,
    ...     for m in range(1, 13):
    ...         print "%d:%d" % (m, days_in_month(datetime.date(y, m, 1))),
    ...     print
    2000 1:31 2:29 3:31 4:30 5:31 6:30 7:31 8:31 9:30 10:31 11:30 12:31
    2001 1:31 2:28 3:31 4:30 5:31 6:30 7:31 8:31 9:30 10:31 11:30 12:31
    """

    if dt.month == 12:
        return 31
    else:
        next = datetime.date(dt.year, dt.month+1, 1)
        return next.toordinal() - dt.replace(day=1).toordinal()

def first_weekday_on_or_after(weekday, dt):
    """First day of kind MONDAY .. SUNDAY on or after date.

    The time and tzinfo members (if any) aren't changed.

    >>> base = datetime.date(2002, 12, 28)  # a Saturday
    >>> base.ctime()
    'Sat Dec 28 00:00:00 2002'
    >>> first_weekday_on_or_after(SATURDAY, base).ctime()
    'Sat Dec 28 00:00:00 2002'
    >>> first_weekday_on_or_after(SUNDAY, base).ctime()
    'Sun Dec 29 00:00:00 2002'
    >>> first_weekday_on_or_after(TUESDAY, base).ctime()
    'Tue Dec 31 00:00:00 2002'
    >>> first_weekday_on_or_after(FRIDAY, base).ctime()
    'Fri Jan  3 00:00:00 2003'
    """

    days_to_go = (weekday - dt.weekday()) % 7
    if days_to_go:
        dt += datetime.timedelta(days_to_go)
    return dt

def first_weekday_on_or_before(weekday, dt):
    """First day of kind MONDAY .. SUNDAY on or before date.

    The time and tzinfo members (if any) aren't changed.

    >>> base = datetime.date(2003, 1, 3)  # a Friday
    >>> base.ctime()
    'Fri Jan  3 00:00:00 2003'
    >>> first_weekday_on_or_before(FRIDAY, base).ctime()
    'Fri Jan  3 00:00:00 2003'
    >>> first_weekday_on_or_before(TUESDAY, base).ctime()
    'Tue Dec 31 00:00:00 2002'
    >>> first_weekday_on_or_before(SUNDAY, base).ctime()
    'Sun Dec 29 00:00:00 2002'
    >>> first_weekday_on_or_before(SATURDAY, base).ctime()
    'Sat Dec 28 00:00:00 2002'
    """

    days_to_go = (dt.weekday() - weekday) % 7
    if days_to_go:
        dt -= datetime.timedelta(days_to_go)
    return dt

def weekday_of_month(weekday, dt, index):
    """Return the index'th day of kind weekday in date's month.

    All the days of kind weekday (MONDAY .. SUNDAY) are viewed as if a
    Python list, where index 0 is the first day of that kind in dt's month,
    and index -1 is the last day of that kind in dt's month.  Everything
    follows from that.  The time and tzinfo members (if any) aren't changed.

    Example:  Sundays in November.  The day part of the date is irrelevant.
    Note that a "too large" index simply spills over to the next month.

    >>> base = datetime.datetime(2002, 11, 25, 13, 22, 44)
    >>> for index in range(5):
    ...     print index, weekday_of_month(SUNDAY, base, index).ctime()
    0 Sun Nov  3 13:22:44 2002
    1 Sun Nov 10 13:22:44 2002
    2 Sun Nov 17 13:22:44 2002
    3 Sun Nov 24 13:22:44 2002
    4 Sun Dec  1 13:22:44 2002

    Start from the end of the month instead:
    >>> for index in range(-1, -6, -1):
    ...     print index, weekday_of_month(SUNDAY, base, index).ctime()
    -1 Sun Nov 24 13:22:44 2002
    -2 Sun Nov 17 13:22:44 2002
    -3 Sun Nov 10 13:22:44 2002
    -4 Sun Nov  3 13:22:44 2002
    -5 Sun Oct 27 13:22:44 2002
    """

    if index >= 0:
        base = first_weekday_on_or_after(weekday, dt.replace(day=1))
        return base + datetime.timedelta(weeks=index)
    else:
        base = first_weekday_on_or_before(weekday,
                                          dt.replace(day=days_in_month(dt)))
        return base + datetime.timedelta(weeks=1+index)

def _test():
    # In 2.3, doctest infers the module by magic.  This doesn't work in 2.2.
    import doctest
    return doctest.testmod()

if __name__ == '__main__':
    _test()
