"""Defines a file reader that updates the percentage read."""
import io
import os


class PercentReader(io.BufferedReader):
    """Computes the percent read of a file.

    Args:
        file_path: file to read.
        pointer (optionnal): a list object to access the percent at read time
        verbose (optionnal): wether to print the percentage on stdout

    Example:

        Using this example, the upload advancement will be stored in the `ptr`
        list. You can then use it in another coroutine.

        >>> ptr = []
        >>> with PercentReader('./my_file.txt', ptr) as file:
        ...     async with aiohttp.ClientSession() as session:
        ...         data = {'file': file}
        ...         res = await session.post('http://0.0.0.0:3000', data = data)

        To print a smooth percent advancement:

        >>> with PercentReader(filepath, verbose=1) as f:
        ...     while len(f.read(100)):
        ...         continue
    """

    def __init__(self, filepath: str, pointer: list = None, verbose: int = 0):
        super().__init__(open(filepath, "rb"))
        self.filepath = filepath
        self.verbose = verbose
        self.pointer = pointer
        self.percent = 0.0
        if pointer is not None:
            self.pointer.clear()
            self.pointer.append(0.0)
        self.total = os.path.getsize(filepath)

    def __enter__(self):
        """Entrypoint of `with`."""
        return self

    def __exit__(self, *arg):
        """Exit point of `with`."""
        del arg
        if self.verbose > 0:
            print()
        self.close()

    def read(self, *args, **kwargs):
        """Returns a chunk of read bytes and updates advancement percent."""
        chunk = super().read(*args, **kwargs)
        self.percent += len(chunk) / self.total * 100
        if self.pointer is not None:
            self.pointer[0] = self.percent
        if self.verbose > 0:
            print(f'\r\033[K{self.filepath}:{self.percent:.2f}%',
                  end='', flush=True)
        return chunk
