# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import psycopg2
from urllib.parse import urlparse

def get_connection():
    url = urlparse(os.environ["DATABASE_URL"])
    return psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
