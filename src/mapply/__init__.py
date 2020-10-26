from functools import partialmethod

from mapply._version import version as __version__  # noqa:F401
from mapply.mapply import mapply as _mapply


def init(
    *,
    n_workers: int = -1,
    chunk_size: int = 100,
    max_chunks_per_worker: int = 20,
    progressbar: bool = True,
    apply_name: str = "mapply",
    map_name: str = "mmap",
    applymap_name: str = "mapplymap",
):
    """Initialize and patch PandasObject.

    Args:
        n_workers: Amount of workers (processes) to spawn.
        chunk_size: Minimum amount of items per chunk. Determines upper limit for n_chunks.
        max_chunks_per_worker: Upper limit on amount of chunks per worker. Will lower
            n_chunks determined by chunk_size if necessary. Set to 0 to skip this check.
        progressbar: Whether to wrap the chunks in a tqdm.auto.tqdm.
        apply_name: Attribute name for the patched apply function.
        map_name: Attribute name for the patched map function.
        applymap_name: Attribute name for the patched applymap function.
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
