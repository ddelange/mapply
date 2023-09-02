# mapply

[![build](https://img.shields.io/github/actions/workflow/status/ddelange/mapply/CI.yml?branch=master&logo=github&cacheSeconds=86400)](https://github.com/ddelange/mapply/actions?query=branch%3Amaster)
[![codecov](https://img.shields.io/codecov/c/github/ddelange/mapply/master?logo=codecov&logoColor=white)](https://codecov.io/gh/ddelange/mapply)
[![pypi Version](https://img.shields.io/pypi/v/mapply.svg?logo=pypi&logoColor=white)](https://pypi.org/project/mapply/)
[![python](https://img.shields.io/pypi/pyversions/mapply.svg?logo=python&logoColor=white)](https://pypi.org/project/mapply/)
[![downloads](https://static.pepy.tech/badge/mapply)](https://pypistats.org/packages/mapply)
[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

[`mapply`](https://github.com/ddelange/mapply) provides a sensible multi-core apply function for Pandas.

### mapply vs. pandarallel vs. swifter

Where [`pandarallel`](https://pypi.org/project/pandarallel) relies on in-house multiprocessing and progressbars, and hard-codes 1 chunk per worker (which will cause idle CPUs when one chunk happens to be more expensive than the others), [`swifter`](https://pypi.org/project/swifter) relies on the heavy [`dask`](https://pypi.org/project/dask) framework for multiprocessing (converting to Dask DataFrames and back). In an attempt to find the golden mean, `mapply` is highly customizable and remains lightweight, using [`tqdm`](https://pypi.org/project/tqdm) for progressbars and leveraging the powerful [`pathos`](https://pypi.org/project/pathos) framework, which shadows Python's built-in multiprocessing module using [`dill`](https://pypi.org/project/dill) for universal pickling.


## Installation

This pure-Python, OS independent package is available on [PyPI](https://pypi.org/project/mapply):

```sh
$ pip install mapply
```


## Usage

[![readthedocs](https://readthedocs.org/projects/mapply/badge/?version=latest)](https://mapply.readthedocs.io)

For documentation, see [mapply.readthedocs.io](https://mapply.readthedocs.io/en/stable/_code_reference/mapply.html).

```py
import pandas as pd
import mapply

mapply.init(
    n_workers=-1,
    chunk_size=100,
    max_chunks_per_worker=8,
    progressbar=False
)

df = pd.DataFrame({"A": list(range(100))})

# avoid unnecessary multiprocessing:
# due to chunk_size=100, this will act as regular apply.
# set chunk_size=1 to skip this check and let max_chunks_per_worker decide.
df["squared"] = df.A.mapply(lambda x: x ** 2)
```


## Development

[![gitmoji](https://img.shields.io/badge/gitmoji-%20%F0%9F%98%9C%20%F0%9F%98%8D-ffdd67)](https://github.com/carloscuesta/gitmoji-cli)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

Run `make help` for options like installing for development, linting, testing, and building docs.
