import os
import selectors
import sys


__all__ = ["EventFD"]

if os.environ.get('EVENTFD_PUREPYTHON') or os.name == "nt":
    HAVE_C_EVENTFD = False
else:
    try:
        from eventfd._eventfd_c import eventfd
        HAVE_C_EVENTFD = True
    except ImportError:
        HAVE_C_EVENTFD = False


class BaseEventFD(object):
    """Class implementing event objects that has a fd that can be selected.

    This EventFD class implements the same functions as a regular Event but it
    has a file descriptor. The file descriptor can be accessed using the fileno function.
    This event can be passed to select, poll and it will block until the event will be set.
    """

    _DATA = None
    _read_fd_is_write_fd = False

    def __init__(self, read_fd, write_fd):
        self._read_fd = read_fd
        self._write_fd = write_fd
        self._selector = selectors.DefaultSelector()
        self._selector.register(read_fd, selectors.EVENT_READ)

    def _read(self, len):
        return os.read(self._read_fd, len)

    def _write(self, data):
        os.write(self._write_fd, data)

    def is_set(self):
        """Return true if and only if the internal flag is true."""
        return self.wait(timeout=0)

    def clear(self):
        """Reset the internal flag to false.

        Subsequently, threads calling wait() will block until set() is called to
        set the internal flag to true again.

        """
        while True:
            # Pull data from the buffer until it is empty
            try:
                b = self._read(4096)
            except BlockingIOError:
                break  # Buffer is empty (i.e. event is cleared)
            if b == b'':
                # I think we always get BlockingIOError, but it's easy to check
                # for a successful but empty read too.
                break

    def set(self):
        """Set the internal flag to true.

        All threads waiting for it to become true are awakened. Threads
        that call wait() once the flag is true will not block at all.

        """
        try:
            self._write(self._DATA)
        except BlockingIOError:
            pass  # Buffer is already full (so event is set)

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
        return bool(self._selector.select(timeout=timeout))

    def fileno(self):
        """Return a file descriptor that can be selected.

        You should not use this directly pass the EventFD object instead.
        """
        return self._read_fd

    def close(self):
        """Closes the file descriptors"""
        if self._read_fd is None:
            return  # Already closed

        self._selector.close()
        read_fd, write_fd = self._read_fd, self._write_fd
        self._read_fd = self._write_fd = None
        os.close(write_fd)
        if read_fd != write_fd:
            os.close(write_fd)

    def __del__(self):
        self.close()

if os.name != "nt":

    class PipeEventFD(BaseEventFD):

        _DATA = b"A"

        def __init__(self):
            read_fd, write_fd = os.pipe2(os.O_NONBLOCK)
            super(PipeEventFD, self).__init__(read_fd, write_fd)

    EventFD = PipeEventFD

    if HAVE_C_EVENTFD:

        class CEventFD(BaseEventFD):

            _DATA = (1).to_bytes(8, byteorder=sys.byteorder)

            def __init__(self):
                read_fd = write_fd = eventfd()
                super(CEventFD, self).__init__(read_fd, write_fd)

            def clear(self):
                """Reset the internal flag to false.

                Subsequently, threads calling wait() will block until set() is called to
                set the internal flag to true again.
                """
                try:
                    self._read(8)  # This resets the counter - no need to loop
                except BlockingIOError:
                    pass  # The counter was already 0

        EventFD = CEventFD

else:  # windows
    import socket

    class SocketEventFD(BaseEventFD):

        _DATA = b'A'

        def __init__(self):
            read_fd, write_fd = socket.socketpair()
            read_fd.setblocking(False)
            write_fd.setblocking(False)
            super(SocketEventFD, self).__init__(read_fd, write_fd)

        def _read(self, len):
            return self._read_fd.recv(len)

        def _write(self, data):
            self._write_fd.send(data)

        def fileno(self):
            return self._read_fd.fileno()

    EventFD = SocketEventFD
