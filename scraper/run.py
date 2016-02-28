#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tweepy

from scraper.lang import parse_sentence

__all__ = ["TwitterickListener"]


class TwitterickListener(tweepy.StreamListener):

    def on_status(self, status):
        # Only select English tweets.
        if status.lang != "en":
            return

        # Ignore tweets with URLs.
        if len(status.entities["urls"]):
            return

        # Ignore quotes and retweets.
        if hasattr(status, "retweeted_status"):
            return
        if hasattr(status, "quoted_status"):
            return

        try:
            print(parse_sentence(status.text))
        except KeyError:
            return
        print(status.text)

    def on_error(self, status_code):
        print(status_code)
        if status_code == 420:
            # returning False in on_data disconnects the stream
            return False


if __name__ == "__main__":
    auth = tweepy.OAuthHandler(
        os.environ["TW_CLIENT_KEY"],
        os.environ["TW_CLIENT_SECRET"],
    )
    auth.set_access_token(
        os.environ["TW_USER_KEY"],
        os.environ["TW_USER_SECRET"],
    )

    listener = TwitterickListener()
    stream = tweepy.Stream(auth=auth, listener=listener)
    stream.sample()
    assert 0
