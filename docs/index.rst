EventFD
=======

.. module:: eventfd
   :synopsis: threading.Event like class that has a file descriptor and can be used in select/poll

.. moduleauthor:: Aviv Palivoda <palaviv@gmail.com>

.. toctree::
   :maxdepth: 2


The python standard library :py:class:`threading.Event` class provides a simple
mechanisms for communication between threads: one thread signals an
event and other threads wait for it. In many cases you would like to signal
a thread that is currently waiting on a other events to happen using select/poll.
The :class:`EventFD` class provides a extension to the :py:class:`threading.Event` class
and can be used to stop the select/poll when signaled.

.. note::
   EventFD support the windows operating system but it is not tested in the CI.

.. note::
   EventFD use the linux eventfd but is not a python binding for eventfd.
   You might want to try:

   * https://pypi.python.org/pypi/linuxfd/
   * https://pypi.python.org/pypi/butter/


Event Objects
-------------

The :class:`EventFD` class is currently implemented with linux eventfd or :py:meth:`os.pipe`.
the :class:`EventFD` class inherits from the :class:`eventfd._eventfd.BaseEventFD` class.


.. autoclass:: eventfd._eventfd.BaseEventFD
   :members:


EXAMPLES
========

We will implement :py:class:`socketserver.TCPServer` without polling using :class:`EventFD`:

   .. literalinclude:: ../server.py


Obtaining the Module
====================

This module can be installed directly from the `Python Package Index`_ with
pip_::

    pip install eventfd

Alternatively, you can download and unpack it manually from the `eventfd
PyPI page`_.

.. _Python Package Index: http://pypi.python.org
.. _pip: http://www.pip-installer.org
.. _eventfd pypi page: http://pypi.python.org/pypi/eventfd


Development and Support
=======================

eventfd is developed and maintained on Github_.

Problems and suggested improvements can be posted to the `issue tracker`_.

.. _Github: https://github.com/palaviv/eventfd
.. _issue tracker: https://github.com/palaviv/eventfd/issues


Release History
---------------

0.2 (01-03-2016)
~~~~~~~~~~~~~~~~

* Using linux eventfd where eventfd is avaiable.
* Travis CI using tox.
* Support for windows using socket (only sockets can be selected in windows).


0.1 (27-02-2016)
~~~~~~~~~~~~~~~~

* EventFD using pipe.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

