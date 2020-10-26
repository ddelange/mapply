# mapply

[![build](https://img.shields.io/github/workflow/status/ddelange/mapply/CI/master?logo=github&cacheSeconds=86400)](https://github.com/ddelange/mapply/actions?query=branch%3Amaster)
[![readthedocs](https://readthedocs.org/projects/mapply/badge/?version=latest)](https://mapply.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://img.shields.io/codecov/c/github/ddelange/mapply/master?logo=codecov&logoColor=white)](https://codecov.io/gh/ddelange/mapply)
[![pypi Version](https://img.shields.io/pypi/v/mapply.svg?logo=pypi&logoColor=white)](https://pypi.org/project/mapply/)
[![python](https://img.shields.io/pypi/pyversions/mapply.svg?logo=python&logoColor=white)](https://pypi.org/project/mapply/)
[![downloads](https://pepy.tech/badge/mapply)](https://pypistats.org/packages/mapply)
[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

[`mapply`](https://github.com/ddelange/mapply) provides sensible multi-core apply/map/applymap functions for Pandas.

### mapply vs. pandarallel vs. swifter

Where [`pandarallel`](https://github.com/nalepae/pandarallel) only requires [`dill`](https://github.com/uqfoundation/dill) (and therefore has to rely on in-house multiprocessing and progressbars), [`swifter`](https://github.com/jmcarpenter2/swifter) relies on the heavy [`dask`](https://github.com/dask/dask) framework, converting to Dask DataFrames and back. In an attempt to find the golden mean, `mapply` is highly customizable and remains lightweight, leveraging the powerful [`pathos`](https://github.com/uqfoundation/pathos) framework, which shadows Python's built-in multiprocessing module using `dill` for universal pickling.


## Installation

This pure-Python, OS independent package is available on [PyPI](https://pypi.org/project/mapply):

```sh
$ pip install mapply
```

## Usage

For documentation, see [mapply.readthedocs.io](https://mapply.readthedocs.io/en/latest).

```py
import pandas as pd
import mapply

mapply.init(
    n_workers=-1,
    chunk_size=100,
    max_chunks_per_worker=10,
    progressbar=False
)

df = pd.DataFrame({"a": list(range(100))})

df["squared"] = df.mapply(lambda x: x ** 2)
```

## Development

[![gitmoji](https://img.shields.io/badge/gitmoji-%20%F0%9F%98%9C%20%F0%9F%98%8D-ffdd67)](https://github.com/carloscuesta/gitmoji-cli)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

Run `make help` for options like installing for development, linting, testing, and building docs.
