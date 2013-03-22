#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

__all__ = ["redis_db"]

import os
import redis


# Redis setup.
e = os.environ
redis_host = e.get("TW_REDIS_HOST", "localhost")
redis_port = e.get("TW_REDIS_PORT", 6379)
redis_db = redis.Redis(host=redis_host, port=redis_port)
