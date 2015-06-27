import argparse
import bisect
from collections import Counter, OrderedDict
import logging


CSV_DELIMITER = ','
FLOAT_DELIMITER = '.'

EVENTS = {
    'web': 1.0,
    'email': 1.2,
    'social': 1.5,
    'webinar': 2.0,
}

SCALE = OrderedDict({
    25: 'bronze',
    50: 'silver',
    75: 'gold',
    100: 'platinum',
})


def score_reader(line):
    validators = (
        lambda value: value.isdigit(),
        lambda value: value in EVENTS,
        lambda value: value.replace(FLOAT_DELIMITER, '').isdigit()
    )

    try:
        contact_id, event, score = line.replace(' ', '').split(CSV_DELIMITER)
    except ValueError:
        logging.warning('Line `%s` was ignored because of wrong format' % line)
        return

    for valid, value in zip(validators, (contact_id, event, score)):
        if not valid(value):
            logging.warning('Line `%s` was ignored because of invalid value(s)' % line)
            return

    return long(contact_id), float(score) * EVENTS[event]


def read_records(filepath, line_reader=None):
    try:
        with open(filepath, 'rb') as file_handler:
            for line in file_handler:
                record = line_reader(line.strip()) if line_reader else line.strip()
                if record:
                    yield record
    except IOError:
        logging.error('Can not open file %s' % filepath)


def normalize(score, top, bottom):
    normalized_score = (score - bottom) / (top - bottom) * 100
    position = bisect.bisect_right(SCALE.keys(), normalized_score)

    if position == len(SCALE):
        return SCALE[next(reversed(SCALE))], round(normalized_score)

    return SCALE.values()[position], round(normalized_score)


def calculate_score(filepath):
    counter = Counter()

    for contact_id, score in read_records(filepath, score_reader):
        counter[contact_id] += score

    if len(counter) > 1:
        top, bottom = max(counter.itervalues()), min(counter.itervalues())
        for contact_id in sorted(counter):
            yield (contact_id, ) + normalize(counter[contact_id], top, bottom)
    else:
        logging.warning('Not enough records found. Must be at least 2 for normalization')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='path to the csv file with score records')

    for contact_score in calculate_score(parser.parse_args().filepath):
        print '%d, %s, %d' % contact_score
