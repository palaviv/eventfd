import os
import select


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

    def __init__(self):
        self._flag = False
        self._read_fd = None
        self._write_fd = None

    def _read(self, len):
        return os.read(self._read_fd, len)

    def _write(self, data):
        os.write(self._write_fd, data)

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
            assert self._read(len(self._DATA)) == self._DATA

    def set(self):
        """Set the internal flag to true.

        All threads waiting for it to become true are awakened. Threads
        that call wait() once the flag is true will not block at all.

        """
        if not self._flag:
            self._flag = True
            self._write(self._DATA)

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

if os.name != "nt":

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

else:  # windows
    import socket

    class SocketEventFD(BaseEventFD):

        _DATA = b'A'

        def __init__(self):
            super(SocketEventFD, self).__init__()
            temp_fd = socket.socket()
            temp_fd.bind(("127.0.0.1", 0))
            temp_fd.listen(1)
            self._read_fd = socket.create_connection(temp_fd.getsockname())
            self._write_fd, _ = temp_fd.accept()
            temp_fd.close()

        def _read(self, len):
            return self._read_fd.recv(len)

        def _write(self, data):
            self._write_fd.send(data)

        def fileno(self):
            return self._read_fd.fileno()

        def __del__(self):
            self._read_fd.close()
            self._write_fd.close()

    EventFD = SocketEventFD