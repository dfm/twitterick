# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

__all__ = []

import re
import string
from functools import partial
from itertools import product, izip, imap

from nltk.corpus import cmudict
from .syllabifier import English, syllabify

# Emoji regular expression from:
# http://stackoverflow.com/questions/13729638/
#  how-can-i-filter-emoji-characters-from-my-input-so-i-can-save-in-mysql-5-5
try:
    emoji = re.compile(u'[\U00010000-\U0010ffff]')
except re.error as e:
    emoji = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')

# Conversions between numbers and the textual representation.
substitutions = [
    (1, "one"),
    (2, "two"),
    (3, "three"),
    (4, "four"),
    (5, "five"),
    (6, "six"),
    (7, "seven"),
    (8, "eight"),
    (9, "nine"),
    (10, "ten"),
    (20, "twenty"),
    (50, "fifty"),
    (99, "ninety nine"),
    (100, "one hundred"),
    (101, "one hundred and one"),
    (1000, "one thousand"),
]
num_re = [(re.compile(r"(\b){0}\b".format(num)),
           r"{0}\g<1>".format(name)) for num, name in substitutions]


def replace_numbers(word):
    for p, r in num_re:
        word = p.sub(r, word)
    return word


def preprocess(word, punct=string.punctuation):
    # Remove emoji.
    word = emoji.sub("", word.lower())

    # Replace common numbers by the word.
    word = replace_numbers(word)

    # Remove trailing punctuation.
    word = word.strip(punct)

    return word


def parse_sentence(sent, syl=partial(syllabify, English),
                   pron_dict=cmudict.dict()):
    sent = sent.strip()
    if not len(sent):
        return
    tokens = filter(len, imap(preprocess, sent.split()))
    phonemes = (map(syl, pron_dict[t]) for t in tokens)

    nsyllables = set()
    final_sounds = set()
    for words in product(*phonemes):
        if not len(words):
            return

        # Count the number of syllables and extract the stress pattern.
        stress, syllables = izip(*((s[0], s[1:]) for w in words for s in w))

        # Compute the final sound.
        final_syllable = syllables[-1]
        if len(final_syllable[2]):
            final_sound = "_".join(imap("_".join, final_syllable[1:]))
        elif len(final_syllable[0]):
            final_sound = "{0}_{1}".format(final_syllable[0][-1],
                                           "_".join(final_syllable[1]))
        else:
            final_sound = "_".join(final_syllable[1])

        # Update the possible versions for this sentence.
        nsyllables.add(len(stress))
        final_sounds.add(final_sound + "_{0}".format(int(stress[-1] > 0)))

    return nsyllables, final_sounds, [tokens[-1]]
