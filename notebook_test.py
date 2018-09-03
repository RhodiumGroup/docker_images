import dask.distributed as dd
import fiona as fiona_notebook


def remote_fiona_import(*args):
    import fiona as fiona_worker
    return str(fiona_worker.__version__) + str(args)


def square(x):
    return x**2


def test_square():
    client = dd.Client("127.0.0.1:8786")
    futures = client.map(lambda x: x**2, range(10))
    total = client.gather(client.submit(sum, futures))
    assert total == 285, total


def test_imports():
    client = dd.Client("127.0.0.1:8786")
    futures = client.map(remote_fiona_import, range(10))
    total = client.gather(futures)


def main():
    test_square()
    test_imports()


if __name__ == "__main__":
    main()
    print('ran all tests successfully')
