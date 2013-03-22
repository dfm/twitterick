#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

__all__ = ["app"]

import flask
import psycopg2

from twitterbot.write_limerick import get_limerick


app = flask.Flask(__name__)
app.config.from_object("twitterbot.config")


@app.route("/")
def index():
    return "Coming soon."
    # lines = [{"id": l["tweet_id"], "body": l["body"].decode("utf-8"),
    #           "screen_name": l["screen_name"]}
    #          for l in get_limerick()]
    # return flask.render_template("index.html", lines=lines)


@app.route("/new")
def new_poem():
    ids = [l["id"] for l in get_limerick()]
    pg_db = psycopg2.connect("dbname=twitterbot")
    cursor = pg_db.cursor()
    cursor.execute("""INSERT INTO poems (l1,l2,l3,l4,l5)
            VALUES (%s,%s,%s,%s,%s) RETURNING id
            """, ids)
    pg_db.commit()
    new_id = cursor.fetchone()[0]
    return flask.redirect(flask.url_for("poem", poem_id=new_id))


@app.route("/<int:poem_id>")
def poem(poem_id):
    pg_db = psycopg2.connect("dbname=twitterbot")
    cursor = pg_db.cursor()
    cursor.execute("""WITH poem AS ( SELECT * FROM poems WHERE id=%s )
            SELECT l1,l2,l3,l4,l5,lines.id,tweet_id,screen_name,body FROM
            lines,poem WHERE lines.id IN (l1,l2,l3,l4,l5)
            """, (poem_id, ))
    results = cursor.fetchall()
    if len(results) != 5:
        flask.abort(404)

    order = [results[0][k] for k in range(5)]
    lines = sorted(results, key=lambda o: order.index(o[5]))
    lines = [{"id": l[6], "body": l[8].decode("utf-8"), "screen_name": l[7]}
             for l in lines]

    return flask.render_template("index.html", lines=lines)
