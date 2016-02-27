import os
import select


__all__ = ["EventFD"]


try:
    from eventfd._eventfd_c import eventfd
    HAVE_C_EVENTFD = True
except ImportError:
    HAVE_C_EVENTFD = False


class BaseEventFD:
    """Class implementing event objects that has a fd that can be selected.

    This EventFD class implements the same functions as a regular Event but it
    has a file descriptor. The file descriptor can be accessed using the fileno function.
    This event can be passed to select, poll and it will block until the event will be set.
    """

    _DATA = None

    def __init__(self):
        self._flag = False
        self._read_fd = None
        self._write_fd = None

    def is_set(self):
        """Return true if and only if the internal flag is true."""
        return self._flag

    def clear(self):
        """Reset the internal flag to false.

        Subsequently, threads calling wait() will block until set() is called to
        set the internal flag to true again.

        """
        if self._flag:
            self._flag = False
            assert os.read(self._read_fd, len(self._DATA)) == self._DATA

    def set(self):
        """Set the internal flag to true.

        All threads waiting for it to become true are awakened. Threads
        that call wait() once the flag is true will not block at all.

        """
        if not self._flag:
            self._flag = True
            os.write(self._write_fd, self._DATA)

    def wait(self, timeout=None):
        """Block until the internal flag is true.

        If the internal flag is true on entry, return immediately. Otherwise,
        block until another thread calls set() to set the flag to true, or until
        the optional timeout occurs.

        When the timeout argument is present and not None, it should be a
        floating point number specifying a timeout for the operation in seconds
        (or fractions thereof).

        This method returns the internal flag on exit, so it will always return
        True except if a timeout is given and the operation times out.

        """
        if not self._flag:
            ret = select.select([self], [], [], timeout)
            assert ret[0] in [[self], []]
        return self._flag

    def fileno(self):
        """Return a file descriptor that can be selected.

        You should not use this directly pass the EventFD object instead.
        """
        return self._read_fd

    def __del__(self):
        """Closes the file descriptors"""
        raise NotImplementedError


class PipeEventFD(BaseEventFD):

    _DATA = b"A"

    def __init__(self):
        super(PipeEventFD, self).__init__()
        self._read_fd, self._write_fd = os.pipe()

    def __del__(self):
        os.close(self._read_fd)
        os.close(self._write_fd)

EventFD = PipeEventFD

if HAVE_C_EVENTFD:

    class CEventFD(BaseEventFD):

        _DATA = b'\x00\x00\x00\x00\x00\x00\x00\x01'

        def __init__(self):
            super(CEventFD, self).__init__()
            self._write_fd = self._read_fd = eventfd()

        def __del__(self):
            os.close(self._write_fd)

    EventFD = CEventFD





