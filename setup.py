#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name="twitterbot",
    packages=["twitterbot"],
    package_data={"twitterbot": ["templates/*"]},
    include_package_data=True,
)
