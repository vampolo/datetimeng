"""A tzinfo object implementing the European DST rules.

See http://webexhibits.org/daylightsaving/g.html

Start: last Sunday in March at 1am UTC
End: last Sunday in October at 1am UTC

Note the subtle difference with the US: all European countries switch
to and from DST *at the same instant*, where in the US states in
different timezones switch at the same local time, which means that
while Eastern time is already on DST, Pacific time will be on normal
time three more hours.  (These are the EU rules; Russia switches at
2am local time.)  Another difference with the US is that the US
switches on the first Sunday in April.  Cuba switches on April
1st. :-)  All switch back on the same date.

"""

from datetime import date, time, timedelta, datetime, tzinfo
from dateutil import MARCH, OCTOBER, SUNDAY, weekday_of_month

HOUR = timedelta(hours=1)
ZERO = timedelta()

# The switches are at 1AM UTC on the last Sundays in March and
# October.
_dston = datetime(1, MARCH, 1, 1)
_dstoff = datetime(1, OCTOBER, 1, 1)

class Fixed(tzinfo):

    def __init__(self, offset, name):
        self.offset = offset
        self.name = name

    def tzname(self, dt):
        return self.name

    def utcoffset(self, dt):
        return self.offset

    def dst(self, dt):
        return ZERO

class Europe(tzinfo):

    def __init__(self, offset, stdname, dstname):
        self.offset = offset
        self.stdname = stdname
        self.dstname = dstname

    def tzname(self, dt):
        if self.dst(dt):
            return self.dstname
        else:
            return self.stdname

    def utcoffset(self, dt):
        return self.offset + self.dst(dt)

    def dst(self, dt):
        if dt is None or dt.tzinfo is None:
            return ZERO
        assert dt.tzinfo is self
        dston = _dston.replace(year=dt.year)
        dstoff = _dstoff.replace(year=dt.year)
        dston = weekday_of_month(SUNDAY, dston,  -1)
        dstoff = weekday_of_month(SUNDAY, dstoff, -1)
        # Convert dt to a naive UTC too (we have to strip the tzinfo member
        # in order to compare to the naive dston and dstoff).
        dt -= self.offset
        if dston <= dt.replace(tzinfo=None) < dstoff:
            return HOUR
        else:
            return ZERO

UTC = Fixed(ZERO, "UTC")
WesternEU = Europe(ZERO, "WET", "WEST")
CentralEU = Europe(HOUR, "CET", "CEST")
EasternEU = Europe(HOUR + HOUR, "EET", "EEST")
London = WesternEU
Amsterdam = CentralEU
Berlin = CentralEU

demo = """
We start easy, Saturday noon in Amsterdam on the last day of DST:

>>> dt = datetime(2002, 10, 26, 12, 0, 0, tzinfo=Amsterdam)
>>> dt.ctime()
'Sat Oct 26 12:00:00 2002'

The UTC offset is 2 hours:

>>> dt.utcoffset().seconds
7200

Now add one day, getting Sunday noon on the first day of standard time:

>>> dt += timedelta(days=1)
>>> dt.ctime()
'Sun Oct 27 12:00:00 2002'

The UTC offset is 1 hour:

>>> dt.utcoffset().seconds
3600

Even easier (but taking a different path through the code), the last
Wednesday before DST ends:

>>> dt = datetime(2002, 10, 23, 12, 0, 0, tzinfo=Amsterdam)
>>> dt.ctime()
'Wed Oct 23 12:00:00 2002'
>>> dt.utcoffset().seconds
7200

And a week later:

>>> dt += timedelta(days=7)
>>> dt.ctime()
'Wed Oct 30 12:00:00 2002'
>>> dt.utcoffset().seconds
3600

Now let's get real close to the end of DST -- in fact, one second
before it ends:

>>> dt = datetime(2002, 10, 27, 1, 59, 59, tzinfo=Amsterdam)
>>> dt.ctime() + ' ' + dt.tzname()
'Sun Oct 27 01:59:59 2002 MDT'
>>> dt.astimezone(UTC).ctime() + ' UTC'
'Sat Oct 26 23:59:59 2002 UTC'

Hey, that was actually an hour before it ended!  That's because the
last hour of DST is unrepresentable -- at 3am, the clock jumps back to
2am; but times between 2am and 3am are (arbitrarily) assumed to be
standard time.  Let's see what time it is in London at the same moment:

>>> dt1 = dt.astimezone(London)
>>> dt1.ctime() + ' ' + dt1.tzname()
'Sun Oct 27 00:59:59 2002 WDT'

Yes, in London it's also still DST, but the clock shows an hour
earlier (they are always an hour behind Amsterdam).

Now add one second, getting to 2am.

>>> dt += timedelta(seconds=1)

This lands us in standard time:

>>> dt.ctime() + ' ' + dt.tzname()
'Sun Oct 27 02:00:00 2002 MET'

Now it's 1am in UTC:

>>> dt.astimezone(UTC).ctime() + ' UTC'
'Sun Oct 27 01:00:00 2002 UTC'

And also 1am in London:

>>> dt1 = dt.astimezone(London)
>>> dt1.ctime() + ' ' + dt1.tzname()
'Sun Oct 27 01:00:00 2002 WET'

Paradox: did we lose an hour or gain an hour?  That depends on your
point of view.  (See also the discussion of the lost days on the
calendar in Thomas Pynchon's Mason & Dixon.)


1. Amsterdam standard time is UTC + 1:00; Amsterdam DST is UTC + 2:00.

2. The DST switch in Amsterdam happens at 1:00:00 UTC == 2:00:00
   standard time == 3:00:00 DST.

3. The unspellable hour is the last hour of DST.

4. So the unspellable hour is 0:HH:MM UTC.

5. Expressed in local time, the unspellable hour is 2:HH:MM DST, which
   is indeed the last hour of DST.

5. This is indeed unspellable; the Amsterdam tzinfo object calls
   2:HH:MM standard time.

6. So at 0:HH:MM UTC, clocks in Amsterdam show 2:HH:MM DST.

>>> print datetime(2002, 10, 26, 23, 0, 0, tzinfo=UTC).astimezone(Amsterdam)
2002-10-27 01:00:00+02:00
>>> print datetime(2002, 10, 27, 0, 0, 0, tzinfo=UTC).astimezone(Amsterdam)
2002-10-27 02:00:00+01:00
>>> print datetime(2002, 10, 27, 1, 0, 0, tzinfo=UTC).astimezone(Amsterdam)
2002-10-27 02:00:00+01:00
>>>

"""
__test__ = {'demo': demo}

def _test():
    import doctest, EU
    return doctest.testmod(EU)

if __name__ == "__main__":
    _test()
