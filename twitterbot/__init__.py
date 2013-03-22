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


@app.before_request
def before():
    flask.g.pg_db = psycopg2.connect("dbname=twitterbot")


@app.route("/new")
def new_poem():
    ids = [l["id"] for l in get_limerick()]
    cursor = flask.g.pg_db.cursor()
    cursor.execute("""INSERT INTO poems (l1,l2,l3,l4,l5)
            VALUES (%s,%s,%s,%s,%s) RETURNING id
            """, ids)
    flask.g.pg_db.commit()
    new_id = cursor.fetchone()[0]
    return flask.redirect(flask.url_for("poem", poem_id=new_id))


@app.route("/")
@app.route("/<int:poem_id>")
def poem(poem_id=None):
    cursor = flask.g.pg_db.cursor()

    if poem_id is None:
        cursor.execute("""SELECT id FROM poems
                OFFSET RANDOM() * (SELECT COUNT(*) FROM poems) LIMIT 1""")
        result = cursor.fetchone()
        if result is None or len(result) == 0:
            return poem()
        poem_id = int(result[0])

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
