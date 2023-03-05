import logging
from types import MethodType
from typing import Any, Callable

from mapply.parallel import multiprocessing_imap

logger = logging.getLogger(__name__)


def run_groupwise_apply(  # noqa:CCR001
    df_or_series: Any,
    func: Callable,
    *,
    n_workers: int,
    progressbar: bool,
    args=(),
    **kwargs,
):
    """Patch GroupBy.grouper.apply, applying func to each group in parallel."""
    from pandas import __version__

    def apply(self, f, data, axis=0):
        # patching https://github.com/pandas-dev/pandas/blob/v1.5.3/pandas/core/groupby/ops.py#L823
        # with a multiprocessing_imap
        from pandas.core.groupby.ops import _is_indexed_like

        mutated = False
        splitter = self._get_splitter(data, axis=axis)
        group_keys = self.group_keys_seq
        result_values = []

        # This calls DataSplitter.__iter__
        # -
        # zipped = zip(group_keys, splitter)
        # +
        splitter = list(splitter)
        zipped = zip(
            group_keys,
            splitter,
            multiprocessing_imap(
                f, splitter, n_workers=n_workers, progressbar=progressbar
            ),
        )

        # -
        # for key, group in zipped:
        # +
        for key, group, res in zipped:
            # Pinning name is needed for
            #  test_group_apply_once_per_group,
            #  test_inconsistent_return_type, test_set_group_name,
            #  test_group_name_available_in_inference_pass,
            #  test_groupby_multi_timezone
            object.__setattr__(group, "name", key)

            # group might be modified
            group_axes = group.axes
            # -
            # res = f(group)
            if not mutated and not _is_indexed_like(res, group_axes, axis):
                mutated = True
            result_values.append(res)
        # getattr pattern for __name__ is needed for functools.partial objects
        if len(group_keys) == 0 and getattr(f, "__name__", None) in [
            "skew",
            "sum",
            "prod",
        ]:
            #  If group_keys is empty, then no function calls have been made,
            #  so we will not have raised even if this is an invalid dtype.
            #  So do one dummy call here to raise appropriate TypeError.
            f(data.iloc[:0])

        return result_values, mutated

    if __version__.split(".") < ["1", "5"]:  # <1.4.0
        logger.warning("GroupBy.mapply only works for pandas>=1.5.0. Using single CPU.")
        return df_or_series.apply(func, *args, **kwargs)
    elif hasattr(df_or_series.grouper, "apply"):  # <2.1.0
        attr = "apply"
    else:  # pragma: no cover
        # 2.1.0 is unreleased https://github.com/pandas-dev/pandas/commit/dc947a459b094ccd087557db355cfde5ed97b454
        attr = "apply_groupwise"
    # overwrite apply method and restore after execution
    original_apply = getattr(df_or_series.grouper, attr)
    setattr(df_or_series.grouper, attr, MethodType(apply, df_or_series.grouper))
    try:
        return df_or_series.apply(func, *args, **kwargs)
    finally:
        setattr(df_or_series.grouper, attr, original_apply)
