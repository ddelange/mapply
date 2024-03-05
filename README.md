# mapply

[![build](https://img.shields.io/github/actions/workflow/status/ddelange/mapply/CI.yml?branch=master&logo=github&cacheSeconds=86400)](https://github.com/ddelange/mapply/actions?query=branch%3Amaster)
[![codecov](https://img.shields.io/codecov/c/github/ddelange/mapply/master?logo=codecov&logoColor=white)](https://codecov.io/gh/ddelange/mapply)
[![pypi Version](https://img.shields.io/pypi/v/mapply.svg?logo=pypi&logoColor=white)](https://pypi.org/project/mapply/)
[![python](https://img.shields.io/pypi/pyversions/mapply.svg?logo=python&logoColor=white)](https://pypi.org/project/mapply/)
[![downloads](https://static.pepy.tech/badge/mapply)](https://pypistats.org/packages/mapply)

[`mapply`](https://github.com/ddelange/mapply) provides a sensible multi-core apply function for Pandas.

### mapply vs. pandarallel vs. swifter

Where [`pandarallel`](https://pypi.org/project/pandarallel) relies on in-house multiprocessing and progressbars, and hard-codes 1 chunk per worker (which will cause idle CPUs when one chunk happens to be more expensive than the others), [`swifter`](https://pypi.org/project/swifter) relies on the heavy [`dask`](https://pypi.org/project/dask) framework for multiprocessing (converting to Dask DataFrames and back). In an attempt to find the golden mean, `mapply` is highly customizable and remains lightweight, using [`tqdm`](https://pypi.org/project/tqdm) for progressbars and leveraging the powerful [`pathos`](https://pypi.org/project/pathos) framework, which shadows Python's built-in multiprocessing module using [`dill`](https://pypi.org/project/dill) for universal pickling. Chunks of work are assigned to worker processes "just in time" from a shared queue, allowing irregular workloads to finish faster.


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
    progressbar=False,
)

df = pd.DataFrame({"A": list(range(100))})

# avoid unnecessary multiprocessing:
# due to chunk_size=100, this will act as regular apply.
# set chunk_size=1 to skip this check and let max_chunks_per_worker decide.
df["squared"] = df.A.mapply(lambda x: x**2)
```


## Development

[![gitmoji](https://img.shields.io/badge/gitmoji-%20%F0%9F%98%9C%20%F0%9F%98%8D-ffdd67)](https://github.com/carloscuesta/gitmoji-cli)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Run `make help` for options like installing for development, linting, testing, and building docs.

-----

BSD 3-Clause License

Copyright (c) 2024, ddelange, <ddelange@delange.dev>

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

SPDX-License-Identifier: BSD-3-Clause
