import pytest

from mapply.parallel import multiprocessing_imap


def foo(x, power):
    if not isinstance(power, float):
        raise ValueError("To check we reraise errors from subprocesses")
    return pow(x, power)


def test_multiprocessing_imap(size=100, power=1.1):
    multicore_list1 = list(
        multiprocessing_imap(
            foo, range(size), power=power, progressbar=False, n_workers=size
        )
    )
    multicore_list2 = list(
        multiprocessing_imap(
            foo, range(size), power=power, progressbar=True, n_workers=1
        )
    )
    multicore_list3 = list(
        multiprocessing_imap(  # generator with unknown length
            foo, (i for i in range(size)), power=power, progressbar=False, n_workers=2
        )
    )

    assert multicore_list1 == multicore_list2
    assert multicore_list1 == multicore_list3
    assert multicore_list1 == [foo(x, power=power) for x in range(size)]
    with pytest.raises(ValueError, match="reraise"):
        # hit with ProcessPool
        list(
            multiprocessing_imap(
                foo, range(size), power=None, progressbar=False, n_workers=2
            )
        )
    with pytest.raises(ValueError, match="reraise"):
        # hit without ProcessPool
        list(
            multiprocessing_imap(
                foo, range(size), power=None, progressbar=False, n_workers=1
            )
        )
