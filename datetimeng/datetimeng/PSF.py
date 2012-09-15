#! /usr/bin/env python

"""PSF year [timezone] ...

Display the start times of PSF Board meetings for the given year, in the
given timezones.  The Eastern time is always shown.
"""

from datetime import datetime
from dateutil import MONDAY, weekday_of_month

from US import Eastern, Central, Mountain, Pacific
from EU import UTC, WesternEU, CentralEU, EasternEU, London, Amsterdam, Berlin

alltzs = {'Eastern': Eastern,
          'Central': Central,
          'Mountain': Mountain,
          'Pacific': Pacific,
          'UTC': UTC,
          'London': London,
          'Amsterdam': Amsterdam,
          'Berlin': Berlin,
          'WesternEU': WesternEU,
          'CentralEU': CentralEU,
          'EasternEU': EasternEU,
         }

# A vector of 12 datetimes, all in Eastern.
def psf_times_for_a_year(year):
    # Until March 2008: 1pm Eastern on the second Monday of the month.
    base = datetime(year, 1, 1, 13, tzinfo=Eastern)
    if year >= 2008:
        # From April 2008: 12pm (noon) Eastern.
        base = base.replace(hour=12)
    times = [weekday_of_month(MONDAY, base.replace(month=i), 1)
             for i in range(1, 13)]
    if year == 2008:
        # Adjust the hour of the first 3 months:
        times[:3] = [time.replace(hour=13) for time in times[:3]]
    return times

# Eastern is always displayed first.
def display_psf_times_for_a_year(year, tzs):
    tzs = list(tzs)
    if Eastern in tzs:
        tzs.remove(Eastern)
    print "PSF Board meeting times for", year
    print
    raw = psf_times_for_a_year(year)
    # Note that the use of strftime limits us to years no earlier than
    # 1900.  This may be a problem for Guido on extended time trips.
    for date in raw:
        print date.strftime("%a %b-%d %H:%M %Z%z "),
        for tz in tzs:
            local = date.astimezone(tz)
            if local.date() == date.date():
                print local.strftime("%H:%M %Z%z "),
            else:
                # It's on a different day for them.
                local.strftime("%a %b-%d %H:%M %Z%z "),
        print

def main():
    import sys
    if len(sys.argv) < 2:
        print >> sys.stderr, "need a year argument"
        sys.exit(-1)
    year = int(sys.argv[1])
    tznames = sys.argv[2:]
    tzs = [alltzs.get(name, None) for name in tznames]
    if None in tzs:
        print >> sys.stderr, "Sorry, the only timezone names I know are", \
                             alltzs.keys()
        sys.exit(-1)
    display_psf_times_for_a_year(year, tzs)

if __name__ == '__main__':
    main()
