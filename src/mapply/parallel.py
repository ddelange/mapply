"""Submodule containing code to distribute computation over multiple processes using :class:`pathos.multiprocessing.ProcessPool`.

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
import logging
from functools import partial
from typing import Any, Callable, Iterable, Optional

import psutil
from pathos.multiprocessing import ProcessPool
from tqdm.auto import tqdm as _tqdm

logger = logging.getLogger(__name__)

tqdm = partial(_tqdm, dynamic_ncols=True)


def sensible_cpu_count() -> int:
    """Count amount of physical CPUs (+1 on hyperthreading systems to prioritize the workers over e.g. system processes)."""
    return min(psutil.cpu_count(logical=False) + 1, psutil.cpu_count(logical=True))


N_CORES = sensible_cpu_count()


def _choose_n_workers(n_chunks: Optional[int], n_workers: int) -> int:
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
    args=(),
    **kwargs
) -> Iterable[Any]:
    """Execute func on each element in iterable on n_workers, ensuring order.

    Args:
        func: Function to apply to each element in iterable.
        iterable: Input iterable on which to execute func.
        n_workers: Amount of workers (processes) to spawn.
        progressbar: Whether to wrap the chunks in a tqdm.auto.tqdm.
        args: Additional positional arguments to pass to func.
        kwargs: Additional keyword arguments to pass to func.

    Yields:
        Results in same order as input iterable.

    Raises:
        Exception: Any error occurred during computation (will terminate the pool early).
        KeyboardInterrupt: Any KeyboardInterrupt sent by the user (will terminate the pool early).
    """
    n_chunks: Optional[int] = tqdm(iterable, disable=True).__len__()  # doesn't exhaust
    func = partial(func, *args, **kwargs)

    n_workers = _choose_n_workers(n_chunks, n_workers)

    if n_workers <= 1:
        # no sense spawning pool
        pool = None
        stage = map(func, iterable)
    else:
        logger.debug("Starting ProcessPool with %d workers", n_workers)
        pool = ProcessPool(n_workers)

        stage = pool.imap(func, iterable)

    if progressbar:
        stage = tqdm(stage, total=n_chunks)

    try:
        yield from stage
    except (Exception, KeyboardInterrupt):
        if pool:
            logger.debug("Terminating ProcessPool")
            pool.terminate()
        raise
    finally:
        if pool:
            logger.debug("Closing ProcessPool")
            pool.clear()
