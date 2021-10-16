# future-map

future-map is a Python library to use together with the official `concurrent.futures` module.

## Why future-map?

Because it's difficult to deal with an infinite or huge input with `concurrent.future.ThreadPoolExecutor` and `concurrent.future.ProcessPoolExecutor`. See the following example.

```python
from concurrent.futures import ThreadPoolExecutor

def make_input(length):
    return range(length)

def make_infinite_input():
    count = 0
    while True:
        yield count
        count += 1

def process(value):
    return value * 2

if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Works well
        for value in executor.map(process, make_input(10)):
            print('Doubled value:', value)

        # This freezes the process and memory usage keeps growing
        for value in executor.map(process, make_infinite_input()):
            print('Doubled value:', value)
```

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install `future-map`.

    $ pip install future-map

## Usage

This library provides `FutureMap`. See the following example.

```python
from future_map import FutureMap
from concurrent.futures import ThreadPoolExecutor

def make_infinite_input():
    count = 0
    while True:
        yield count
        count += 1

def process(value):
    return value * 2

if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=3) as executor:
        fm = FutureMap(
            lambda value: executor.submit(process, value),
            make_infinite_input(), buffersize=5
        )
        for value in fm:
            print('Doubled value:', value)
```

For more complicated use case:


```python
import time
from concurrent.futures import ThreadPoolExecutor

from future_map import FutureMap

class APIClient:
    def __init__(self, max_connections):
        self.__max_connections = max_connections
        self.__executor = None

    def __enter__(self):
        self.__executor = ThreadPoolExecutor(max_workers=self.__max_connections)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__executor.shutdown()
        self.__executor = None

    def call(self, url):
        time.sleep(1)
        return "Response from {}".format(url)

    def call_async(self, url):
        if self.__executor is None:
            raise Exception("call_async needs to be called in the runtime context with this APIClient")
        return self.__executor.submit(self.call, url)


def make_urls():
    for i in range(100):
        yield "https://example.com/api/resources/{}".format(i)

if __name__ == '__main__':
    with APIClient(max_connections=3) as api_client:
        for response in FutureMap(api_client.call_async, make_urls(), buffersize=5):
            print(response)
```

### API

#### `FutureMap(fn, iterable, buffersize)`

Constructor of `FutureMap`.

`FutureMap` is an iterable object that maps an iterable object (`iterable` argument) to a function (`fn` argument), waits until each future object is done, and yields each result.

Please note that this object will yield unordered results.

- Arguments
  - `fn`: Callable object that takes an argument from iterable, and return a `concurrent.futures.Future`.
  - `iterable`: Iterable object.
  - `buffersize`: Maximum size of internal buffer. Each `concurrent.futures.Future` object is stored in the buffer until it's done. If the buffer is fulfilled, `FutureMap` stops reading values from `iterable`.
- Return
  - `FutureMap` instance

#### `future_map(fn, iterable, buffersize)`

Alias of `FutureMap`. You can use this function if you prefer a similar syntax with the `map` function.

For more details, please refer to `FutureMap(fn, iterable, buffersize)`.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
