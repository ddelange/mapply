# mapply

[![build](https://img.shields.io/github/workflow/status/ddelange/mapply/GH/master?logo=github&cacheSeconds=86400)](https://github.com/ddelange/mapply/actions?query=branch%3Amaster)
[![codecov](https://img.shields.io/codecov/c/github/ddelange/mapply/master?logo=codecov&logoColor=white)](https://codecov.io/gh/ddelange/mapply)
[![pypi Version](https://img.shields.io/pypi/v/mapply.svg?logo=pypi&logoColor=white)](https://pypi.org/project/mapply/)
[![python](https://img.shields.io/pypi/pyversions/mapply.svg?logo=python&logoColor=white)](https://pypi.org/project/mapply/)
[![downloads](https://pepy.tech/badge/mapply)](https://pypistats.org/packages/mapply)
[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)


## Initial setup of this repo

Add this repo to Github:

- [Create a new repository](https://github.com/new) on GitHub. Only fill in `mapply` and an optional description and click `Create repository`. Do not initialize the new repository with README, license, or gitignore files.

- Now push this repo to Github (`__version__` is populated based on tags, so tag the initial commit):

```sh
cd mapply
git init .
git add .
git commit -m ':tada: Initial commit'
git tag -a "0.1.0-rc.1" -m 'Initial release candidate. Bump version on GitHub and it will be reflected on the next `git pull; pip install -e .`'
git remote add origin https://github.com/ddelange/mapply.git
git push --set-upstream origin master
```

- This repo contains GitHub Actions to to run `linting`, `tests`, `codecov`, and `PyPi` deploys for all GitHub releases.

    - This requires `$PYPI_USER` and `$PYPI_PASSWORD` and `$CODECOV_TOKEN` (found under `Repository Upload Token` at https://codecov.io/gh/ddelange/mapply/settings)

    - Add these variables to the repo's secrets here: https://github.com/ddelange/mapply/settings/secrets

- It is also recommended to make `master` a protected branch. The first two ticks should be enough (`Require branches to be up to date before merging` is also nice, and `Include administrators` will avoid accidental pushes to `master`): https://github.com/ddelange/mapply/settings/branch_protection_rules/new

- If you'd like, add a LICENSE.md file manually or via GitHub GUI (don't forget to pull afterwards), and add an appropriate keyword to [`setup()`](setup.py), e.g. `license="MIT"`, and the appropriate [classifier](https://pypi.org/classifiers/), e.g. `"License :: OSI Approved :: MIT License"`.

- You can remove this (now unnecessary) section.

## Installation

This pure-Python, OS independent package is available on [PyPI](https://pypi.org/project/mapply):

```sh
$ pip install mapply
```

## Usage

```py
# TODO
```

## Development

[![gitmoji](https://img.shields.io/badge/gitmoji-%20%F0%9F%98%9C%20%F0%9F%98%8D-ffdd67)](https://github.com/carloscuesta/gitmoji-cli)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

Run `make help` for options like installing for development, linting, testing, and building docs.
