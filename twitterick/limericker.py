# -*- coding: utf-8 -*-
from __future__ import print_function
import random


def get_lines(cursor, min_len, max_len, final_sound=None, final_word=None,
              count=1):
    q = """
select id, final_word, final_sound, syllable_count from tweets
where syllable_count between %s and %s
"""
    args = [min_len, max_len]

    if final_sound is not None:
        q += "and final_sound = %s\n"
        args += [final_sound]

    if final_word is not None:
        q += "and final_word != %s\n"
        args += [final_word]

    q += "and random >= (select random() offset 0)\n"

    if count == 1:
        q += "order by random asc limit 1"
        cursor.execute(q, args)
        return cursor.fetchone()

    q += "order by random asc limit %s"
    args += [count]
    cursor.execute(q, args)
    return cursor.fetchall()


def write(cursor, maxtries=100):
    # First, find the long lines.
    flag = False
    for i in range(maxtries):
        line1 = get_lines(cursor, 8, 13)
        if line1 is None:
            continue
        long_lines = get_lines(cursor, line1[3], line1[3]+1, count=2,
                               final_sound=line1[2], final_word=line1[1])
        if len(long_lines) == 2:
            flag = True
            break
    if not flag:
        raise RuntimeError("Exceeded maxtries")

    # Then, find the short lines for the middle.
    flag = False
    for i in range(maxtries):
        line3 = get_lines(cursor, 5, 7)
        if line3 is None:
            continue
        line4 = get_lines(cursor, 5, 7, final_sound=line3[2],
                          final_word=line3[1])
        if line4 is not None:
            flag = True
            break
    if not flag:
        raise RuntimeError("Exceeded maxtries")

    # Combine the lines.
    lines = (long_lines[0], line1, line3, line4, long_lines[1])
    cursor.execute("insert into twittericks (l1, l2, l3, l4, l5, random) "
                   "values (%s, %s, %s, %s, %s, %s) returning id",
                   [l[0] for l in lines] + [random.random()])
    return cursor.fetchone()[0]
