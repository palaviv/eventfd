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

.. warning::
   EventFD currently does not support the Windows operating system


Event Objects
-------------

.. autoclass:: EventFD
   :members:


EXAMPLES
========

we will implement :py:class:`socketserver.TCPServer` without polling using :class:`EventFD`:

   .. literalinclude:: ../server.py


Development and Support
=======================

eventfd is developed and maintained on Github_.

Problems and suggested improvements can be posted to the `issue tracker`_.

.. _Github: https://github.com/palaviv/eventfd
.. _issue tracker: https://github.com/palaviv/eventfd/issues


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

