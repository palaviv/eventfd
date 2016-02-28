#include <Python.h>
#include <sys/eventfd.h>


static PyObject * _eventfd(PyObject *self) {
    int result;

    Py_BEGIN_ALLOW_THREADS
    result = eventfd(0, 0);
    Py_END_ALLOW_THREADS
    if (result == -1)
    {
        return PyErr_SetFromErrno(PyExc_OSError);
    }

    return PyLong_FromLong(result);
};

static PyMethodDef EventFDMethods[] =
{
     {"eventfd", _eventfd, METH_NOARGS, "return new eventfd"},
     {NULL, NULL, 0, NULL}
};

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef eventfdmodule = {
   PyModuleDef_HEAD_INIT,
   "_eventfd_c",   /* name of module */
   NULL, /* module documentation, may be NULL */
   -1,       /* size of per-interpreter state of the module,
                or -1 if the module keeps state in global variables. */
   EventFDMethods
};


PyMODINIT_FUNC
PyInit__eventfd_c(void)
#else
PyMODINIT_FUNC init_eventfd_c(void)
#endif
{
#if PY_MAJOR_VERSION >= 3
    return PyModule_Create(&eventfdmodule);
#else
    Py_InitModule("_eventfd_c",EventFDMethods);
#endif
}
