#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

__all__ = []

import re
import psycopg2
from nltk.corpus import cmudict

from db_utils import redis_db


pron_dict = cmudict.dict()
digits = "0123456789"


def get_syllables(s):
    # Sanitize and split the words.
    s = s.lower()
    words = re.sub("[^a-zA-Z'_ ]", "", s).split()
    if len(words) < 2:
        return [], None, None

    # Build the syllable list.
    syllables = []
    for w in words:
        try:
            syllables += pron_dict[w][0]
        except (IndexError, KeyError):
            return [], None, None

    # Count the syllables.
    count = sum([sy[-1] in digits for sy in syllables])
    return syllables, count, words[-1]


if __name__ == "__main__":
    # Postgres setup.
    pg_db = psycopg2.connect("dbname=twitterbot")
    cursor = pg_db.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS lines
            (id SERIAL, tweet_id TEXT, screen_name TEXT,
             count INTEGER, body TEXT, last_word TEXT,
             s1 TEXT, s2 TEXT, s3 TEXT, s4 TEXT)
            """)
    pg_db.commit()

    # Connect to redis PubSub.
    pubsub = redis_db.pubsub()
    pubsub.subscribe("twitterbot")

    # Listen to the PubSub.
    for msg in pubsub.listen():
        if msg["type"] == "message":
            msg = msg["data"].decode("utf-8")
            ind = msg.index(":")
            (nm, id_str), msg = msg[:ind].split(), msg[ind + 2:]
            s, count, lw = get_syllables(msg)
            if 5 <= count <= 13:
                syls = [sy.strip(digits) for sy in s[-4:]]
                cursor = pg_db.cursor()
                cursor.execute("""INSERT INTO lines
                        (tweet_id,screen_name,count,body,last_word,s1,s2,s3,s4)
                        VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, [id_str, nm, count, msg, lw] + syls)
                pg_db.commit()
