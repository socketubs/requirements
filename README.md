# Requirements

*☛ Python requirements for Humans ™*

[![Coverage Status](https://coveralls.io/repos/github/socketubs/requirements/badge.svg?branch=master)](https://coveralls.io/github/socketubs/requirements?branch=master)
[![Build Status](https://travis-ci.org/socketubs/requirements.svg?branch=master)](https://travis-ci.org/socketubs/requirements)

Write your adorable `requirements.txt` once and forget `setup.py` hassles.

```python
from setuptools import setup
from requirements import r

setup(
    name='your-package',
    version='0.0.1',
    **r.requirements)
```

### Features

* Requirements discovery
* Manage `dependency_links` and `tests_require`
* Just drop `requirements.py` in your package directory
* Works well with [pip-tools](https://github.com/nvie/pip-tools)
* Configurable for different requirements layout
* Python `2.7`, `3.3`, `3.4`, `3.5`
* Very light, well tested, no dependencies and more!


### Usage

* Download latest `requirements.py` release in your package root directory
* Import it in your `setup.py`, like in previous example

Some variables are configurable like that:

```python
from requirements import r

r.requirements_path = 'reqs.txt'
r.tests_requirements_path = 'reqs-tests.txt'
```

License is `MIT`.
