"""Submodule containing code to run PandasObject.apply() in parallel.

Standalone usage (without init):
::

    import pandas as pd
    from mapply.mapply import mapply

    df = pd.DataFrame({"A": list(range(100))})

    df["squared"] = mapply(df.A, lambda x: x ** 2, progressbar=False)
"""
from functools import partial
from typing import Any, Callable, Tuple, Union

from mapply.parallel import N_CORES, multiprocessing_imap

DEFAULT_CHUNK_SIZE = 100
DEFAULT_MAX_CHUNKS_PER_WORKER = 8


def _choose_n_chunks(
    shape: Tuple[int, ...],
    axis: int,
    n_workers: int,
    chunk_size: int,
    max_chunks_per_worker: int,
):
    """Choose final amount of chunks to be sent to the ProcessPool."""
    # no sense running parallel if data is too small
    n_chunks = int(shape[axis] / chunk_size)

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
        n_workers: Maximum amount of workers (processes) to spawn. Might be lowered
            depending on chunk_size and max_chunks_per_worker. Will throw a warning if
            set higher than is sensible (see :meth:`mapply.parallel.sensible_cpu_count`).
        chunk_size: Minimum amount of columns/rows per chunk. Higher value means a higher
            threshold to go multi-core. Set to 1 to let max_chunks_per_worker decide.
        max_chunks_per_worker: Upper limit on amount of chunks per worker. Will lower
            n_chunks determined by chunk_size if necessary. Set to 0 to skip this check.
        progressbar: Whether to wrap the chunks in a :meth:`tqdm.auto.tqdm`.
        args: Additional positional arguments to pass to func.
        kwargs: Additional keyword arguments to pass to apply/func.

    Returns:
        Series or DataFrame resulting from applying func along given axis.

    Raises:
        ValueError: if a Series is passed in combination with axis=1
    """
    from numpy import array_split
    from pandas import Series, concat

    if isinstance(axis, str):
        axis = ["index", "columns"].index(axis)

    isseries = int(isinstance(df_or_series, Series))

    if isseries and axis == 1:
        raise ValueError("Passing axis=1 is not allowed for Series")

    opposite_axis = 1 - (isseries or axis)

    n_chunks = _choose_n_chunks(
        df_or_series.shape,
        opposite_axis,
        n_workers,
        chunk_size,
        max_chunks_per_worker,
    )

    dfs = array_split(df_or_series, n_chunks, axis=opposite_axis)

    def run_apply(func, df_or_series, args=(), **kwargs):
        return df_or_series.apply(func, args=args, **kwargs)

    if not isseries:
        kwargs["axis"] = axis

    results = list(
        multiprocessing_imap(
            partial(run_apply, func, args=args, **kwargs),
            dfs,
            n_workers=n_workers,
            progressbar=progressbar,
        )
    )

    if (
        not isseries
        and len(results) > 1
        and results[0].index.equals(df_or_series.index)
    ):
        return concat(results, axis=1, copy=False)

    return concat(results, copy=False)
