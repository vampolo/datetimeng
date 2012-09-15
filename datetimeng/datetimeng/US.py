from datetime import time, datetime
from datetime import tzinfo
from datetime import timedelta

from dateutil import SUNDAY, MARCH, APRIL, OCTOBER, NOVEMBER, weekday_of_month

__all__ = ['USTimeZone', 'Eastern', 'Central', 'Mountain', 'Pacific']


class DST_Rules(object):

    """Encapsulate the rules for a DST change date."""

    # Assumes that DST changes happen on Sunday mornings.

    def __init__(self, month, sunday_index):
        """
        Parameters:

        * `month`: Month of DST change (1=January, 12=December).
        * `sunday_index`: Base-0 index of Sunday (0=first, 1=second, -1=last).
        """
        self.month = month
        self.sunday_index = sunday_index
        self.dummy_date = datetime(year=1, month=month, day=1, hour=self.hour)

    def date(self, year):
        """Return the date of the change in the given `year`."""
        date = weekday_of_month(
            SUNDAY, self.dummy_date.replace(year=year), self.sunday_index)
        assert date.month == self.dummy_date.month
        return date


class DST_Start(DST_Rules):

    # DST starts at 2am (standard time):
    hour = 2


class DST_End(DST_Rules):

    # DST ends at 1am (standard time; 2am DST time):
    hour = 1


class USTimeZone(tzinfo):
    """
    A class capturing the pre- and post-2007 daylight saving time (DST)
    rules for United States time zones.
    """
    # Note that in 2007 the rules changed.  The comment below refers to
    # the old rules.  See USTimeZone.dst_rules for specific dates.

    # A seemingly intractable problem:  when DST ends, there's a one-hour
    # slice that repeats in "naive time".  That is, when the naive clock
    # hits 2am on the last Sunday in October, it magically goes back an
    # hour and starts over at 1am.  A naive time simply can't know whether
    # range(1:00:00, 2:00:00) on that day *intends* to refer to standard
    # or daylight time, and adding a tzinfo object modeling both DST and
    # standard time doesn't improve that.
    #
    #        DST   1am  2am  3am ...
    #   standard        1am  2am ...
    #
    # There isn't a good solution to deciding what 1:MM:SS means then.  If
    # you say it's DST, then there's no way to spell a time in the 1-hour
    # span starting when DST ends:  1:MM:SS would be taken as DST, 2:MM:SS
    # as standard, and in UTC there's a one-hour gap between 1:59:59 DST
    # and 2:00:00 standard.  The UTC times in that gap can't be named.
    #
    # OTOH, if you say 1:MM:SS is standard time then, there's no way to
    # spell the hour preceding 1:00:00:.  12:59:59 must be taken as DST,
    # and by hypothesis 1:00:00 is taken as standard, and again there's a
    # one-hour gap between those in UTC.
    #
    # The implementation can't win, so we decided to call 1:MM:SS standard
    # time.  A# consequence of the "missing hour" (under either choice) is
    # that UTC -> this timezone -> UTC can't always be an identity (some
    # one-hour range of UTC times simply can't be spelled in this timezone).
    #
    # On the other end, when DST starts at 2am on the first Sunday in April,
    # the naive clock magically jumps from 1:59:59 to 3:00:00.  A naive time
    # of 2:MM:SS on that day doesn't make sense.  We arbitrarily decide it
    # intends DST then, making it a redundant spelling of 1:MM:SS standard
    # on that day.  A consequence of the redundant spelling is that
    # this timezone -> UTC -> this timezone can't always be an identity on
    # this end of the scale.

    dstoff = timedelta(hours=1)
    zero = timedelta(0)

    # [(first year, start rule, end rule), ...]
    dst_rules = [
        (2007,
         DST_Start(month=MARCH, sunday_index=1),
         DST_End(month=NOVEMBER, sunday_index=0)),
        (1987,
         DST_Start(month=APRIL, sunday_index=0),
         DST_End(month=OCTOBER, sunday_index=-1)),
        ]
    # Ensure that the rules are in reverse chronological order:
    dst_rules.sort(reverse=True)

    def __init__(self, stdhours, stdname, dstname):
        self.stdoff = timedelta(hours=stdhours)
        self.stdname = stdname
        self.dstname = dstname

    def utcoffset(self, dt):
        return self.stdoff + self.dst(dt)

    def tzname(self, dt):
        if self.dst(dt):
            return self.dstname
        else:
            return self.stdname

    def dst(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception instead may be sensible here, in one or more of
            # the cases.
            return self.zero

        assert dt.tzinfo is self

        for (first_year, dst_start, dst_end) in self.dst_rules:
            if dt.year >= first_year:
                break
        else:
            # As above, an exception instead may be sensible here.
            return self.zero

        start = dst_start.date(dt.year)
        assert start.weekday() == 6
        if dt.year >= 2007:
            #import pdb ; pdb.set_trace()
            assert 8 <= start.day <= 14
        else:
            assert start.day <= 7

        end = dst_end.date(dt.year)
        assert end.weekday() == 6
        if dt.year >= 2007:
            assert end.day <= 7
        else:
            assert end.day >= 25

        # Can't compare naive to aware objects, so strip the timezone from
        # dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return self.dstoff
        else:
            return self.zero


Eastern  = USTimeZone(-5, "EST", "EDT")
Central  = USTimeZone(-6, "CST", "CDT")
Mountain = USTimeZone(-7, "MST", "MDT")
Pacific  = USTimeZone(-8, "PST", "PDT")


brainbuster_test = """
>>> def printstuff(d):
...     print d
...     print d.tzname()
...     print d.timetuple()
...     print d.ctime()

Right before DST starts.
>>> before = datetime(2002, 4, 7, 1, 59, 59, tzinfo=Eastern)
>>> printstuff(before)
2002-04-07 01:59:59-05:00
EST
(2002, 4, 7, 1, 59, 59, 6, 97, 0)
Sun Apr  7 01:59:59 2002

Right when DST starts -- although this doesn't work very well.
>>> after = before + timedelta(seconds=1)
>>> printstuff(after)
2002-04-07 02:00:00-04:00
EDT
(2002, 4, 7, 2, 0, 0, 6, 97, 1)
Sun Apr  7 02:00:00 2002

2:00:00 doesn't exist on the naive clock (the naive clock leaps from 1:59:59
to 3:00:00), and is taken to be in DST, as a redundant spelling of 1:00:00
standard time.  So we actually expect b to be about an hour *before* a.
However, subtraction of two objects with the same tzinfo member is "naive",
so comes out to 1 second:

>>> print after - before
0:00:01

Converting to UTC and subtracting, we get the "about an hour":

>>> ZERO = timedelta(0)
>>> class UTC(tzinfo):
...     def utcoffset(self, dt):
...         return ZERO
...     dst = utcoffset
...     def tzname(self, dt):
...         return "utc"

>>> utc = UTC()
>>> utcdiff = after.astimezone(utc) - before.astimezone(utc)
>>> print -utcdiff
0:59:59

Converting 'after' to UTC and back again isn't an identity, because, as
above, 2 is taken as being in DST, a synonym for 1 in standard time:

>>> printstuff(after.astimezone(utc).astimezone(Eastern)) # 1:00 standard
2002-04-07 01:00:00-05:00
EST
(2002, 4, 7, 1, 0, 0, 6, 97, 0)
Sun Apr  7 01:00:00 2002

To get the start of DST in a robust way, we have to give the "naive clock"
time of 3:

>>> after = after.replace(hour=3)
>>> printstuff(after)
2002-04-07 03:00:00-04:00
EDT
(2002, 4, 7, 3, 0, 0, 6, 97, 1)
Sun Apr  7 03:00:00 2002
>>> printstuff(after.astimezone(utc).astimezone(Eastern))  # now an identity
2002-04-07 03:00:00-04:00
EDT
(2002, 4, 7, 3, 0, 0, 6, 97, 1)
Sun Apr  7 03:00:00 2002
>>> print after.astimezone(utc) - before.astimezone(utc)
0:00:01

Now right before DST ends.
>>> before = datetime(2002, 10, 27, 0, 59, 59, tzinfo=Eastern)
>>> printstuff(before)
2002-10-27 00:59:59-04:00
EDT
(2002, 10, 27, 0, 59, 59, 6, 300, 1)
Sun Oct 27 00:59:59 2002

And right when DST ends.
>>> after = before + timedelta(seconds=1)
>>> printstuff(after)
2002-10-27 01:00:00-05:00
EST
(2002, 10, 27, 1, 0, 0, 6, 300, 0)
Sun Oct 27 01:00:00 2002

The naive clock repeats the times in 1:HH:MM, so 1:00:00 was actually
ambiguous, and resolved as being in EST, and is actually about an hour later.
Again, because these have the same tzinfo member, the utcoffsets are ignored
by straight subtraction, but revealed by converting to UTC first:

>>> print after - before
0:00:01
>>> print after.astimezone(utc) - before.astimezone(utc)
1:00:01

One more glitch:  that one-hour gap contains times that can't be represented
in Eastern (all times of the form 5:MM:SS UTC on this day).  Here's one of
them:

>>> phantom = before.astimezone(utc) + timedelta(seconds=1)
>>> printstuff(phantom)
2002-10-27 05:00:00+00:00
utc
(2002, 10, 27, 5, 0, 0, 6, 300, 0)
Sun Oct 27 05:00:00 2002

What happens when we convert that to Eastern?  astimezone detects the
impossibilty of the task, and mimics the local clock's "repeat the 1:MM
hour" behavior:

>>> paradox = phantom.astimezone(Eastern)
>>> printstuff(paradox)
2002-10-27 01:00:00-05:00
EST
(2002, 10, 27, 1, 0, 0, 6, 300, 0)
Sun Oct 27 01:00:00 2002

The UTC hour after also converts to 1:00 Eastern.  The one above is really
1:00 EDT, and the one below really 1:00 EST, but Eastern can't tell the
difference:

>>> phantom += timedelta(hours=1)
>>> printstuff(phantom)
2002-10-27 06:00:00+00:00
utc
(2002, 10, 27, 6, 0, 0, 6, 300, 0)
Sun Oct 27 06:00:00 2002
>>> printstuff(phantom.astimezone(Eastern))
2002-10-27 01:00:00-05:00
EST
(2002, 10, 27, 1, 0, 0, 6, 300, 0)
Sun Oct 27 01:00:00 2002

Post-2007 rules:

Right before DST starts.
>>> before = datetime(2007, 3, 11, 1, 59, 59, tzinfo=Eastern)
>>> printstuff(before)
2007-03-11 01:59:59-05:00
EST
(2007, 3, 11, 1, 59, 59, 6, 70, 0)
Sun Mar 11 01:59:59 2007

Right when DST starts.
>>> after = before + timedelta(seconds=1)
>>> printstuff(after)
2007-03-11 02:00:00-04:00
EDT
(2007, 3, 11, 2, 0, 0, 6, 70, 1)
Sun Mar 11 02:00:00 2007
 """

__test__ = {'brainbuster': brainbuster_test}

def _test():
    import doctest, US
    return doctest.testmod(US)

if __name__ == "__main__":
    _test()
