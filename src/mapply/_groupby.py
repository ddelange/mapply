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
# ruff: noqa: ERA001
import logging
from types import MethodType
from typing import Any, Callable

from pandas.core.groupby.ops import _is_indexed_like

from mapply.parallel import multiprocessing_imap, tqdm

logger = logging.getLogger(__name__)


def run_groupwise_apply(
    df_or_series: Any,
    func: Callable,
    *,
    n_workers: int,
    progressbar: bool,
    args: tuple[Any, ...] = (),
    **kwargs: Any,
):
    """Patch GroupBy.grouper.apply, applying func to each group in parallel."""

    def apply(self, f, data, axis=0):
        # patching https://github.com/pandas-dev/pandas/blob/v2.1.4/pandas/core/groupby/ops.py#L890
        # with a multiprocessing_imap
        mutated = False
        splitter = self._get_splitter(data, axis=axis)
        group_keys = self.group_keys_seq
        result_values = []

        # This calls DataSplitter.__iter__
        zipped = zip(group_keys, splitter)

        # rewrite the original for-loop into an imap
        def _run_apply(args):
            key, group = args
            # Pinning name is needed for
            #  test_group_apply_once_per_group,
            #  test_inconsistent_return_type, test_set_group_name,
            #  test_group_name_available_in_inference_pass,
            #  test_groupby_multi_timezone
            object.__setattr__(group, "name", key)

            # group might be modified
            group_axes = group.axes
            res = f(group)
            return res, group_axes

        # generator with length defined (for progressbar)
        zipped = tqdm(zipped, disable=True, total=splitter.ngroups)
        zipped = multiprocessing_imap(
            _run_apply,
            zipped,
            n_workers=n_workers,
            progressbar=progressbar,
        )

        # original for-loop leftover
        for res, group_axes in zipped:
            # no changes made below this line
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

    # overwrite apply method and restore after execution
    attr = "apply_groupwise"
    original_apply = getattr(df_or_series.grouper, attr)
    setattr(df_or_series.grouper, attr, MethodType(apply, df_or_series.grouper))
    try:
        return df_or_series.apply(func, *args, **kwargs)
    finally:
        setattr(df_or_series.grouper, attr, original_apply)
