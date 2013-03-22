#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

__all__ = []

import random
import psycopg2


pg_db = psycopg2.connect("dbname=twitterbot")


def get_op(shrt):
    return "<=6" if shrt else ">=10"


def get_random_line(shrt=False):
    cursor = pg_db.cursor()
    cursor.execute(("SELECT id,tweet_id,screen_name,body,last_word,s3,s4 "
                    "FROM lines WHERE count{0} OFFSET RANDOM()"
                    " * (SELECT COUNT(*) FROM lines WHERE count{0}) LIMIT 1")
                   .format(get_op(shrt)))
    result = cursor.fetchone()
    if result is None or len(result) == 0:
        return get_random_line(shrt=shrt)
    return dict(zip(["id", "tweet_id", "screen_name", "body",
                     "last_word", "s3", "s4"], result))


def get_rhymes(id_, s3, s4, lw, shrt=False, limit=2):
    cursor = pg_db.cursor()
    cursor.execute(("SELECT id,tweet_id,screen_name,body FROM lines "
                    "WHERE id!=%s AND last_word!=%s AND count{0} "
                    "AND s3=%s AND s4=%s ORDER BY RANDOM() LIMIT %s")
                   .format(get_op(shrt)), (id_, lw, s3, s4, limit))
    results = cursor.fetchall()
    return [dict(zip(["id", "tweet_id", "screen_name", "body"], r))
            for r in results]


def get_limerick():
    while 1:
        lng_line = get_random_line()
        lng_rhymes = get_rhymes(lng_line["id"], lng_line["s3"], lng_line["s4"],
                                lng_line["last_word"])
        if len(lng_rhymes) >= 2:
            break

    while 1:
        srt_line = get_random_line(shrt=True)
        srt_rhymes = get_rhymes(srt_line["id"], srt_line["s3"], srt_line["s4"],
                                srt_line["last_word"], shrt=True, limit=1)
        if len(srt_rhymes) >= 1:
            break

    lng_rhymes += [lng_line]
    random.shuffle(lng_rhymes)

    srt_rhymes += [srt_line]
    random.shuffle(srt_rhymes)

    return lng_rhymes[:2] + srt_rhymes + [lng_rhymes[2]]


if __name__ == "__main__":
    for l in get_limerick():
        print(l["body"])
