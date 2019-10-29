try:
    import fcntl
    import os

    def lock_file(f):
        fcntl.lockf(f, fcntl.LOCK_EX)

    def unlock_file(f):
        fcntl.lockf(f, fcntl.LOCK_UN)
except ModuleNotFoundError:
    import msvcrt
    import os

    def _file_size(f):
        return os.path.getsize(os.path.realpath(f.name))

    def lock_file(f):
        msvcrt.locking(f.fileno(), msvcrt.LK_RLCK, _file_size(f))

    def unlock_file(f):
        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, _file_size(f))


class Lockfile:
    """Locks a file.

    Args:
        filepath: path to the file to lock.
        mode: open mode that will choose to which mode the lock applies

    Example:
        >>> with Lockfile('/path/to/file.txt', 'w'):
        ...     # do stuff while file writing is blocked ...
        ...     pass
        ... # file is unlocked
    """

    def __init__(self, filepath: str, mode: str):
        self._fd = open(filepath, mode)

    def __enter__(self):
        lock_file(self._fd)
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        unlock_file(self._fd)
        self._fd.close()
