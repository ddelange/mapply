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
import logging
from collections.abc import Callable
from typing import Any

from mapply.parallel import multiprocessing_imap, tqdm

logger = logging.getLogger(__name__)


def run_window_groupby_apply(
    window_groupby: Any,
    func: Callable,
    *,
    n_workers: int,
    progressbar: bool,
    args: tuple[Any, ...] = (),
    **kwargs: Any,
):
    """Apply func to each group's window in parallel using multiprocessing_imap."""
    from pandas import concat
    from pandas.core.window.expanding import ExpandingGroupby
    from pandas.core.window.rolling import RollingGroupby

    if isinstance(window_groupby, ExpandingGroupby):
        window_kwargs = {
            "min_periods": window_groupby.min_periods,
        }
        window_method = "expanding"
    elif isinstance(window_groupby, RollingGroupby):
        window_kwargs = {
            "window": window_groupby.window,
            "min_periods": window_groupby.min_periods,
            "center": window_groupby.center,
            "on": window_groupby.on,
            "closed": window_groupby.closed,
        }
        window_method = "rolling"
    else:
        msg = f"Unsupported window groupby type: {type(window_groupby).__name__}"
        raise TypeError(msg)

    grouper = window_groupby._grouper  # noqa: SLF001
    indices = grouper.indices
    result_index = grouper.result_index
    obj = window_groupby.obj
    as_index = window_groupby._as_index  # noqa: SLF001
    groupby_names = grouper.names

    # lazy generator: yield (key, group_slice) without materializing all groups
    def _group_iter():
        for key in result_index:
            yield key, obj.iloc[indices[key]]

    def _process_group(key_and_data):
        key, group_data = key_and_data
        window_obj = getattr(group_data, window_method)(**window_kwargs)
        result = window_obj.apply(func, args=args, **kwargs)
        return key, result

    # generator with length defined (for progressbar)
    groups = tqdm(_group_iter(), disable=True, total=len(result_index))
    processed = multiprocessing_imap(
        _process_group,
        groups,
        n_workers=n_workers,
        progressbar=progressbar,
    )

    # consume lazily from the multiprocessing_imap generator
    keys = []
    parts = []
    for key, part in processed:
        keys.append(key)
        parts.append(part)

    if not parts:
        # delegate to native pandas for the empty case to preserve index dtypes
        return window_groupby.apply(func, args=args, **kwargs)

    result = concat(parts, keys=keys, names=groupby_names + list(obj.index.names))

    if not as_index:
        result = result.reset_index(level=list(range(len(groupby_names))))

    return result
