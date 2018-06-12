
import re
import datetime
import pytz

CURRENT_VERSION = None
NEXT_VERSION = None

with open('.travis.yml', 'r') as travis:
    lines = travis.readlines()

newlines = []

for l in lines:
    matcher = re.match(r'(?P<pre>.*TAG=)(?P<date>\d{4}-\d{2}-\d{2})\.(?P<ver>\d{2})?(?P<post>[.\s]*)$', l, re.I)
    if matcher:
        timestamp = datetime.datetime(
            *map(int, matcher.group('date').split('-')), tzinfo=pytz.utc)

        date = datetime.date(timestamp.year, timestamp.month, timestamp.day)

        now = datetime.datetime.utcnow()
        today = datetime.date(now.year, now.month, now.day)

        if (date == today):
            if matcher.group('ver') is None:
                ver = 1
            else:
                ver = int(matcher.group('ver')) + 1
        else:
            ver = 1

        newlines.append(
            matcher.group('pre')
            + '{:>04}-{:>02}-{:>02}.{:>02}'
                    .format(now.year, now.month, now.day, ver)
            + matcher.group('post'))

    else:
        newlines.append(l)

with open('.travis.yml', 'w+') as travis:
    for l in newlines:
        travis.write(l)