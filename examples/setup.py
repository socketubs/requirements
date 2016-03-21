#!/usr/bin/env python
from setuptools import setup
from requirements import r

setup(
    name='example',
    version='0.0.1',
    **r.requirements)
