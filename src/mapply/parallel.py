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
"""Submodule containing code to distribute computation over multiple processes using :class:`pathos.pools.ProcessPool`.

Standalone usage:
::

    from mapply.parallel import multiprocessing_imap

    def some_heavy_computation(x, power):
        return pow(x, power)

    multicore_list = list(
        multiprocessing_imap(
            some_heavy_computation,
            range(100),
            power=2.5,
            progressbar=False,
            n_workers=-1,
        )
    )
"""

from __future__ import annotations

import logging
import os
from collections.abc import Iterable, Iterator
from functools import partial
from typing import Any, Callable

import multiprocess
import psutil
from pathos.pools import ProcessPool
from tqdm.auto import tqdm as _tqdm

logger = logging.getLogger(__name__)

tqdm = partial(_tqdm, dynamic_ncols=True, smoothing=0.042, mininterval=0.42)


def sensible_cpu_count() -> int:
    """Count amount of physical CPUs (+1 on hyperthreading systems to prioritize the workers over e.g. system processes)."""
    return min(psutil.cpu_count(logical=False) + 1, psutil.cpu_count(logical=True))


N_CORES = sensible_cpu_count()
MAX_TASKS_PER_CHILD = int(os.environ.get("MAPPLY_MAX_TASKS_PER_CHILD", 4))
CONTEXT = multiprocess.get_context(os.environ.get("MAPPLY_START_METHOD"))
POOL_CLASS = ProcessPool


def _choose_n_workers(n_chunks: int | None, n_workers: int) -> int:
    """Choose final amount of workers to be spawned for received input."""
    if n_workers < 1:
        n_workers = N_CORES
    elif n_workers > N_CORES:
        logger.warning(
            "Using more workers (%d) than is sensible (%d). For CPU-bound operations, consider lowering n_workers to avoid bottlenecks on the physical CPUs",
            n_workers,
            N_CORES,
        )

    # no sense having more workers than chunks
    if n_chunks is not None:
        n_workers = min(n_workers, n_chunks)

    return n_workers


def multiprocessing_imap(
    func: Callable,
    iterable: Iterable[Any],
    *,
    n_workers: int = -1,
    progressbar: bool = True,
    args: tuple[Any, ...] = (),
    **kwargs: Any,
) -> Iterator[Any]:
    """Execute func on each element in iterable on n_workers, ensuring order.

    Args:
        func: Function to apply to each element in iterable.
        iterable: Input iterable on which to execute func.
        n_workers: Amount of workers (processes) to spawn.
        progressbar: Whether to wrap the chunks in a tqdm.auto.tqdm.
        args: Additional positional arguments to pass to func.
        **kwargs: Additional keyword arguments to pass to func.

    Yields:
        Results in same order as input iterable.

    Raises:
        Exception: Any error occurred during computation (will terminate the pool early).
        KeyboardInterrupt: Any KeyboardInterrupt sent by the user (will terminate the pool early).
    """
    n_chunks: int | None = tqdm(iterable, disable=True).__len__()  # doesn't exhaust
    func = partial(func, *args, **kwargs)

    n_workers = _choose_n_workers(n_chunks, n_workers)

    if n_workers <= 1:
        # no sense spawning pool
        pool = None
        stage = map(func, iterable)
    else:
        pool_kwargs = (
            # allow changing pool: import mapply, pathos; mapply.parallel.POOL_CLASS = pathos.pools.ThreadPool
            {"maxtasksperchild": MAX_TASKS_PER_CHILD, "context": CONTEXT}
            if ProcessPool == POOL_CLASS
            else {}
        )
        logger.debug("Starting ProcessPool with %d workers", n_workers)
        pool = POOL_CLASS(n_workers, **pool_kwargs)

        stage = pool.imap(func, iterable)

    if progressbar:
        stage = tqdm(stage, total=n_chunks)

    try:
        yield from stage
    except (Exception, KeyboardInterrupt):
        if pool:
            logger.debug("Terminating pool")
            pool.terminate()
        raise
    finally:
        if pool:
            logger.debug("Closing pool")
            pool.clear()
