
import re
import datetime
import pytz

SEARCH_PATTERNS = [
    ('.travis.yml', r'(?P<pre>.*TAG=)(?P<date>\d{4}-\d{2}-\d{2})\.?(?P<ver>\d{2})?(?P<post>[.\s]*)$'),
    ('notebook/worker-template.yml', r'(?P<pre>.*image: rhodium/worker:)(?P<date>\d{4}-\d{2}-\d{2})\.?(?P<ver>\d{2})?(?P<post>[.\s]*)$'),
    ('jupyter-config.yml', r'(?P<pre>.*tag: )(?P<date>\d{4}-\d{2}-\d{2})\.?(?P<ver>\d{2})?(?P<post>[.\s]*)$')]


def bump_file(fname, pattern):

    current_version = None
    new_version = None

    with open(fname, 'r') as f:
        lines = f.readlines()

    newlines = []

    for l in lines:
        matcher = re.match(pattern, l, re.I)
        if matcher:

            if current_version is not None:
                raise ValueError(
                    'version declared twice in file {}'.format(fname))

            current_version = (matcher.group('date'), matcher.group('ver'))

            timestamp = datetime.datetime(
                *map(int, matcher.group('date').split('-')), tzinfo=pytz.utc)

            date = datetime.date(
                timestamp.year, timestamp.month, timestamp.day)

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

            new_version = (
                '{:>04}-{:>02}-{:>02}'.format(now.year, now.month, now.day),
                '{:>02}'.format(ver))

        else:
            newlines.append(l)

    return (current_version, new_version, ''.join(newlines))


def main():
    cv = None
    nv = None

    contents = []

    for fname, pattern in SEARCH_PATTERNS:
        this_cv, this_nv, this_contents = bump_file(fname, pattern)


        if cv is None:
            cv = this_cv
            nv = this_nv

        if cv != this_cv:
            raise ValueError(
                'Version mismatch in {}: {} != {}'
                .format(fname, cv, this_cv))

        if nv != this_nv:
            raise ValueError(
                'New version mismatch in {}: {} != {}'
                .format(fname, nv, this_nv))

        contents.append((fname, this_contents))

    for fname, c in contents:
        with open(fname, 'w+') as f:
            f.write(c)


if __name__ == '__main__':
    main()

