"""Submodule containing code to run PandasObject.apply() in parallel.

Standalone usage (without init):
::

    import pandas as pd
    from mapply.mapply import mapply

    df = pd.DataFrame({"a": list(range(100))})

    df["squared"] = mapply(df, lambda x: x ** 2, progressbar=False)
"""
from functools import partial
from typing import Any, Callable, Union

from mapply.parallel import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_MAX_CHUNKS_PER_WORKER,
    N_CORES,
    multiprocessing_imap,
)


def _choose_n_chunks(
    df_or_series: Any,
    n_workers: int,
    chunk_size: int,
    max_chunks_per_worker: int,
):
    """Choose final amount of chunks to be sent to the ProcessPool."""
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
    func: Callable,
    axis: Union[int, str] = 0,
    *,
    n_workers: int = -1,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    max_chunks_per_worker: int = DEFAULT_MAX_CHUNKS_PER_WORKER,
    progressbar: bool = True,
    args=(),
    **kwargs
) -> Any:
    """Run apply on n_workers. Split in chunks if sensible, gather results, and concat.

    When using :meth:`mapply.init`, the signature of this method will behave the same as
    :meth:`pandas.DataFrame.apply` or :meth:`pandas.Series.apply`.

    Args:
        df_or_series: Argument reserved to the class instance, a.k.a. 'self'.
        func: func to apply to each column or row.
        axis: Axis along which func is applied.
        n_workers: Amount of workers (processes) to spawn.
        chunk_size: Minimum amount of items per chunk. Determines upper limit for n_chunks.
        max_chunks_per_worker: Upper limit on amount of chunks per worker. Will lower
            n_chunks determined by chunk_size if necessary. Set to 0 to skip this check.
        progressbar: Whether to wrap the chunks in a :meth:`tqdm.auto.tqdm`.
        args: Additional positional arguments to pass to func.
        kwargs: Additional keyword arguments to pass to apply/func.

    Returns:
        Series or DataFrame resulting from applying func along given axis.
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
        axis = ["index", "columns"].index(axis.lower())

    if axis == 1:
        # axis argument pre-processing
        df_or_series = df_or_series.T

    dfs = array_split(df_or_series, n_chunks, axis=axis)

    def run_apply(func, df, args=(), **kwargs):
        # axis argument is handled such that always axis=0 here
        return df.apply(func, args=args, **kwargs)  # pragma: no cover

    results = multiprocessing_imap(
        partial(run_apply, func, args=args, **kwargs),
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
        return concat(results, axis=1).apply(func, axis=1, args=args, **kwargs)

    if axis == 1:
        # axis argument pre-processing
        results = (df.T for df in results)  # type: ignore
    return concat(results)
