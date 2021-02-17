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
from functools import partialmethod

from mapply._version import version as __version__  # noqa:F401
from mapply.mapply import DEFAULT_CHUNK_SIZE, DEFAULT_MAX_CHUNKS_PER_WORKER
from mapply.mapply import mapply as _mapply


def init(
    *,
    n_workers: int = -1,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    max_chunks_per_worker: int = DEFAULT_MAX_CHUNKS_PER_WORKER,
    progressbar: bool = True,
    apply_name: str = "mapply",
    map_name: str = "mmap",
    applymap_name: str = "mapplymap",
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
        map_name: Method name for the patched map function.
        applymap_name: Method name for the patched applymap function.
    """
    from pandas.core.base import PandasObject

    setattr(
        PandasObject,
        apply_name,
        partialmethod(
            _mapply,
            n_workers=n_workers,
            chunk_size=chunk_size,
            max_chunks_per_worker=max_chunks_per_worker,
            progressbar=progressbar,
        ),
    )
