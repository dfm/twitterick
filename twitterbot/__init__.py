#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

__all__ = ["app"]

import flask

from twitterbot.write_limerick import get_limerick


app = flask.Flask(__name__)
app.config.from_object("twitterbot.config")


@app.route("/")
def index():
    try:
        lines = [{"id": l["tweet_id"], "body": l["body"].decode("utf-8"),
                  "screen_name": l["screen_name"]}
                 for l in get_limerick()]
    except Exception as e:
        return str(e)
    return flask.render_template("index.html", lines=lines)
