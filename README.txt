eventfd offer the EventFD class in python. The class implement all the functions as the threading.Event class. In addition to that the EventFD has the fileno method and thus can be used to in select/poll.

Online documentation can be found at http://eventfd.readthedocs.org/.

Please see the example in server.py for a use case of this class.

