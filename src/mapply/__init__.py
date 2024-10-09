# BSD 3-Clause License
#
# Copyright (c) 2024, ddelange, <ddelange@delange.dev>
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# SPDX-License-Identifier: BSD-3-Clause
"""Top-level package containing init to patch Pandas.

Example usage:
::

    import pandas as pd
    import mapply

    mapply.init(
        n_workers=-1,
        chunk_size=100,
        max_chunks_per_worker=10,
        progressbar=False
    )

    df = pd.DataFrame({"A": list(range(100))})

    df["squared"] = df.A.mapply(lambda x: x ** 2)
"""

import contextlib
from functools import partialmethod
from importlib.metadata import PackageNotFoundError, version

from mapply.mapply import DEFAULT_CHUNK_SIZE, DEFAULT_MAX_CHUNKS_PER_WORKER
from mapply.mapply import mapply as _mapply

with contextlib.suppress(PackageNotFoundError):
    __version__ = version("mapply")


def init(
    *,
    n_workers: int = -1,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    max_chunks_per_worker: int = DEFAULT_MAX_CHUNKS_PER_WORKER,
    progressbar: bool = True,
    apply_name: str = "mapply",
):
    """Patch Pandas, adding multi-core methods to PandasObject.

    Subsequent calls to this function will create/overwrite methods with new settings.

    Args:
        n_workers: Maximum amount of workers (processes) to spawn. Might be lowered
            depending on chunk_size and max_chunks_per_worker. Will throw a warning if
            set higher than is sensible (see :meth:`mapply.parallel.sensible_cpu_count`).
        chunk_size: Minimum amount of columns/rows per chunk. Higher value means a higher
            threshold to go multi-core. Set to 1 to let max_chunks_per_worker decide.
        max_chunks_per_worker: Upper limit on amount of chunks per worker. Will lower
            n_chunks determined by chunk_size if necessary. Set to 0 to skip this check.
        progressbar: Whether to wrap the chunks in a :meth:`tqdm.auto.tqdm`.
        apply_name: Method name for the patched apply function.
    """
    from pandas.core.base import PandasObject

    apply = partialmethod(
        _mapply,
        n_workers=n_workers,
        chunk_size=chunk_size,
        max_chunks_per_worker=max_chunks_per_worker,
        progressbar=progressbar,
    )

    setattr(PandasObject, apply_name, apply)
