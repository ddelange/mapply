import logging
from functools import partial
from typing import Any, Callable, Iterable, List

import psutil
from pathos.multiprocessing import ProcessingPool
from tqdm.auto import tqdm

logger = logging.getLogger(__name__)


def _choose_n_workers(n_chunks: int, n_workers: int) -> int:
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
    return min(n_workers, n_chunks)


def sensible_cpu_count() -> int:
    """Count amount of physical CPUs, plus 1 on hyperthreading systems to prioritize."""
    return min(psutil.cpu_count(logical=False) + 1, psutil.cpu_count(logical=True))


N_CORES = sensible_cpu_count()


def multiprocessing_imap(
    function: Callable,
    iterable: Iterable[Any],
    *,
    n_workers: int = -1,
    progressbar: bool = True,
    args=(),
    **kwargs
) -> List[Any]:
    """Execute function on each element in iterable on n_workers, ensuring order.

    Args:
        function: Function to apply to each element in iterable.
        iterable: Input iterable on which to execute function.
        n_workers: Amount of workers (processes) to spawn.
        progressbar: Whether to wrap the chunks in a tqdm.auto.tqdm.
        args: Additional positional arguments to pass to function.
        kwargs: Additional keyword arguments to pass to function.

    Returns:
        Results in same order as input iterable.
    """
    iterable = list(iterable)  # exhaust if iterable is a generator
    n_chunks = len(iterable)
    function = partial(function, *args, **kwargs)

    if n_chunks == 1 or n_workers == 1:
        # no sense spawning pool
        stage = map(function, iterable)
    else:
        n_workers = _choose_n_workers(n_chunks, n_workers)

        logger.debug("Starting ProcessingPool with %d workers", n_workers)
        pool = ProcessingPool(n_workers)

        stage = pool.imap(function, iterable)

    if progressbar:
        stage = tqdm(stage, total=n_chunks)

    return list(stage)
