from mapply.parallel import multiprocessing_imap


def foo(x, power):
    return pow(x, power)


def test_multiprocessing_imap(size=100, power=1.1):
    multicore_list1 = multiprocessing_imap(
        foo, range(size), power=power, progressbar=False, n_workers=size
    )
    multicore_list2 = multiprocessing_imap(
        foo, range(size), power=power, progressbar=True, n_workers=1
    )
    multicore_list3 = multiprocessing_imap(  # generator with unknown length
        foo, (i for i in range(size)), power=power, progressbar=False, n_workers=2
    )

    assert multicore_list1 == multicore_list2
    assert multicore_list1 == multicore_list3
    assert multicore_list1 == [foo(x, power=power) for x in range(size)]
