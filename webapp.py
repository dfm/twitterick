#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import psycopg2

import tornado.web
import tornado.ioloop
import tornado.httpserver
from tornado.escape import json_encode
from tornado.options import define, options, parse_command_line

from twitterick import emoji
from twitterick.limericker import write

define("port", default=3058, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")
define("xheaders", default=True, help="use X-headers")
define("cookie_secret", default="secret key", help="secure key")

define("postgres_user", default=None, help="Postgres username")
define("postgres_pass", default=None, help="Postgres password")
define("postgres_db", default="twitterick", help="Postgres database name")


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r"/", RecentHandler),
            (r"/new", NewHandler),
            (r"/recent", RecentHandler),
            (r"/popular", PopularHandler),
            (r"/([0-9]+)", TwitterickHandler),
            (r"/like/([0-9]+)", LikeHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            xheaders=options.xheaders,
            cookie_secret=options.cookie_secret,
            debug=options.debug,
        )
        super(Application, self).__init__(handlers, ui_methods=emoji,
                                          **settings)

        dsn = "dbname={0}".format(options.postgres_db)
        if options.postgres_user is not None:
            dsn += " user={0}".format(options.postgres_user)
        if options.postgres_pass is not None:
            dsn += " password={0}".format(options.postgres_pass)
        self._db = psycopg2.connect(dsn)

    @property
    def db(self):
        return self._db


class BaseHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        return self.application.db

    def get_poems(self, poem_id=None, page=0, per_page=20, popular=False):
        q = """
select
    twittericks.id, twittericks.votes,
    t1.tweet_id, t1.username, t1.body,
    t2.tweet_id, t2.username, t2.body,
    t3.tweet_id, t3.username, t3.body,
    t4.tweet_id, t4.username, t4.body,
    t5.tweet_id, t5.username, t5.body
from twittericks
    join tweets as t1 on l1=t1.id
    join tweets as t2 on l2=t2.id
    join tweets as t3 on l3=t3.id
    join tweets as t4 on l4=t4.id
    join tweets as t5 on l5=t5.id
"""
        args = []

        if poem_id is not None:
            q += "where twittericks.id=%s limit 1\n"
            args += [poem_id]
        else:
            if popular:
                q += "where votes > 0 order by votes desc, id desc"
            else:
                q += "order by id desc"
            q += " offset %s limit %s"
            args += [page * per_page, per_page]

        with self.db as conn:
            c = conn.cursor()
            c.execute(q, args)
            results = c.fetchall()

        return [dict(poem_id=r[0], votes=r[1],
                     lines=[dict(tweet_id=r[2+i*3], username=r[3+i*3],
                                 body=r[4+i*3]) for i in range(5)])
                for r in results]


class NewHandler(BaseHandler):

    def get(self):
        with self.db as conn:
            poem_id = write(conn.cursor())
        self.redirect("/{0}".format(poem_id))


class RecentHandler(BaseHandler):

    def get(self):
        # Pagination.
        page = self.get_argument("page", 0)
        page = max([0, int(page)])

        poems = self.get_poems(page=page)

        # Get the result of the query.
        if not len(poems):
            self.render("noresults.html")

        # Parse the poem and display the results.
        self.render("poems.html", title="Recent Twittericks", poems=poems,
                    next_page=page+1, prev_page=page-1)


class PopularHandler(BaseHandler):

    def get(self):
        # Pagination.
        page = self.get_argument("page", 0)
        page = max([0, int(page)])

        poems = self.get_poems(page=page, popular=True)

        # Get the result of the query.
        if not len(poems):
            self.render("noresults.html")

        # Parse the poem and display the results.
        self.render("poems.html", title="Popular Twittericks", poems=poems,
                    next_page=page+1, prev_page=page-1)


class TwitterickHandler(BaseHandler):

    def get(self, poem_id):
        poems = self.get_poems(poem_id=poem_id)

        # Get the result of the query.
        if not len(poems):
            self.render("noresults.html")

        # Parse the poem and display the results.
        self.render("poem.html", title="Twitterick #{0}".format(poem_id),
                    poem=poems[0])


class LikeHandler(BaseHandler):

    def get(self, poem_id):
        with self.db as conn:
            c = conn.cursor()
            c.execute("update twittericks set votes=votes+1 where id=%s "
                      "returning votes",
                      (poem_id, ))
            votes = c.fetchone()

        self.set_header("Content-Type", "application/json")
        if votes is None:
            self.set_status(404)
            self.write(json_encode(dict(message="Failure", votes=0)))
            self.finish()
        self.write(json_encode(dict(message="Success", votes=votes[0])))


def main():
    parse_command_line()

    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port, address="127.0.0.1")
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
