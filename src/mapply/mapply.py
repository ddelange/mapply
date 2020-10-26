from functools import partial
from typing import Any, Callable, Union

from mapply.parallel import N_CORES, multiprocessing_imap


def _choose_n_chunks(
    df_or_series: Any,
    n_workers: int,
    chunk_size: int,
    max_chunks_per_worker: int,
):
    """Choose final amount of chunks to be sent to the ProcessingPool."""
    # no sense running parallel if data is too small
    n_chunks = int(len(df_or_series) / chunk_size)

    if max_chunks_per_worker:
        # no sense making too many chunks
        n_chunks = min(n_chunks, max_chunks_per_worker * N_CORES)
    if n_chunks < 1 or n_workers == 1 or N_CORES == 1:
        # no sense running parallel
        n_chunks = 1

    return n_chunks


def mapply(
    df_or_series: Any,
    function: Callable,
    axis: Union[int, str] = 0,
    *,
    n_workers: int = -1,
    chunk_size: int = 100,
    max_chunks_per_worker: int = 20,
    progressbar: bool = True,
    args=(),
    **kwargs
) -> Any:
    """Run apply on n_workers. Split in chunks, gather results, and concat them.

    Args:
        df_or_series: Argument reserved to the class instance, a.k.a. 'self'.
        function: Function to apply to each column or row.
        axis: Axis along which the function is applied.
        n_workers: Amount of workers (processes) to spawn.
        chunk_size: Minimum amount of items per chunk. Determines upper limit for n_chunks.
        max_chunks_per_worker: Upper limit on amount of chunks per worker. Will lower
            n_chunks determined by chunk_size if necessary. Set to 0 to skip this check.
        progressbar: Whether to wrap the chunks in a tqdm.auto.tqdm.
        args: Additional positional arguments to pass to function.
        kwargs: Additional keyword arguments to pass to function.

    Returns:
        Series or DataFrame resulting from applying function along given axis.
    """
    from numpy import array_split
    from pandas import Series, concat

    n_chunks = _choose_n_chunks(
        df_or_series,
        n_workers,
        chunk_size,
        max_chunks_per_worker,
    )

    if isinstance(axis, str):
        axis = ["index", "columns"].index(axis)

    if axis == 1:
        # axis argument pre-processing
        df_or_series = df_or_series.T

    dfs = array_split(df_or_series, n_chunks, axis=axis)

    def run_apply(function, df, args=(), **kwargs):
        # axis argument is handled such that always axis=0 here
        return df.apply(function, args=args, **kwargs)  # pragma: no cover

    results = multiprocessing_imap(
        partial(run_apply, function, args=args, **kwargs),
        dfs,
        n_workers=n_workers,
        progressbar=progressbar,
    )

    if (
        len(results) > 1
        and isinstance(results[0], Series)
        and results[0].index.equals(results[1].index)
    ):
        # one more aggregation needed for final df, e.g. df.parallel_apply(sum)
        return concat(results, axis=1).apply(function, axis=1, args=args, **kwargs)

    if axis == 1:
        # axis argument pre-processing
        results = (df.T for df in results)  # type: ignore
    return concat(results)
