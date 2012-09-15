"""A tzinfo object mirroring local time."""

import time as _time

from datetime import date, time, timedelta, datetime, tzinfo

STDOFFSET = timedelta(seconds = -_time.timezone)
if _time.daylight:
    DSTOFFSET = timedelta(seconds = -_time.altzone)
else:
    DSTOFFSET = STDOFFSET

ZERO = timedelta()
DSTDIFF = DSTOFFSET - STDOFFSET

class LocalTimezone(tzinfo):

    def utcoffset(self, dt):
        if self._isdst(dt):
            return DSTOFFSET
        else:
            return STDOFFSET

    def dst(self, dt):
        if self._isdst(dt):
            return DSTDIFF
        else:
            return ZERO

    def tzname(self, dt):
        return _time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, -1)
        stamp = _time.mktime(tt)
        tt = _time.localtime(stamp)
        return tt[8] > 0

Local = LocalTimezone()

demo = """
*** This test only works in US/Eastern ***

Pick a time in standard time.

>>> dt = datetime(2003, 1, 2, 18, 05, 49)
>>> dt.isoformat()
'2003-01-02T18:05:49'
>>> dt = dt.replace(tzinfo=Local)
>>> dt.isoformat()
'2003-01-02T18:05:49-05:00'

Pick a time in DST.

>>> dt = datetime(2003, 7, 2, 18, 05, 49)
>>> dt.isoformat()
'2003-07-02T18:05:49'
>>> dt = dt.replace(tzinfo=Local)
>>> dt.isoformat()
'2003-07-02T18:05:49-04:00'
"""
__test__ = {'demo': demo}

def _test():
    import doctest, Local
    return doctest.testmod(Local)

if __name__ == "__main__":
    _test()
