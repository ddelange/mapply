import numpy as np
import pandas as pd

import mapply


def test_mapply():
    mapply.init(progressbar=False)

    np.random.seed(1)
    df = pd.DataFrame(
        pd.np.random.randint(0, 300, size=(int(2000), 4)), columns=list("ABCD")
    )

    # axis as positional arg
    df["totals"] = df.mapply(lambda x: x.A + x.B, "columns")
    df.mapply(lambda x: x ** 2)
    pd.testing.assert_series_equal(
        df.mapply(sum, max_chunks_per_worker=10),
        df.mapply(np.sum, raw=True),
    )

    fn = lambda x: [x.A, x.B]  # noqa:E731
    pd.testing.assert_frame_equal(
        df.mapply(fn, axis=1, result_type="expand"),
        df.apply(fn, axis=1, result_type="expand"),
    )

    mapply.init(progressbar=False, max_chunks_per_worker=0)
    df.mapply(lambda x: x ** 2)

    mapply.init(progressbar=False, n_workers=1)
    df.mapply(lambda x: x ** 2)
