# -*- coding: utf-8 -*-
from __future__ import print_function

import psycopg2
from itertools import product
from twitterick.twitter import monitor
from twitterick.lang import parse_sentence

allowed_lengths = set(range(5, 14))

with psycopg2.connect("dbname=twitterick") as conn:
    c = conn.cursor()
    c.execute("drop table tweets")
    c.execute("""
        create table if not exists tweets (
            id serial,
            tweet_id text,
            username text,
            body text,
            syllable_count integer,
            final_word text,
            final_sound text
        )
    """)
    c.execute("create index on tweets "
              "(syllable_count, final_sound, final_word)")

for tweet in monitor():
    # Get the id of the tweet.
    tweet_id = tweet.get("id_str", None)
    if tweet_id is None:
        continue

    # Get the user info.
    user = tweet.get("user", None)
    if user is None:
        continue

    # Get the user's username.
    username = user.get("screen_name", None)
    if username is None:
        continue

    # Get the content of the tweet.
    text = tweet.get("text", None)
    if text is None:
        continue

    # Parse the contents of the tweet.
    try:
        info = parse_sentence(text)
    except KeyError:
        continue
    except Exception as e:
        print("Failed with exception:")
        print(e)
        continue

    # Check to make sure that the parse didn't fail.
    if info is None or not info[0] & allowed_lengths:
        continue

    print(username, info[0], info[0] & allowed_lengths)
    with psycopg2.connect("dbname=twitterick") as conn:
        c = conn.cursor()
        for n, s, w in product(*info):
            c.execute("""
                insert into tweets(tweet_id, username, body, syllable_count,
                                   final_word, final_sound)
                values (%s, %s, %s, %s, %s, %s)
            """, (tweet_id, username, text, n, w, s))
