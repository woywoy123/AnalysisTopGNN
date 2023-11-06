from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.map cimport map
from libcpp cimport bool

from cytypes cimport meta_t

cdef extern from "metadata.h" namespace "SampleTracer":
    cdef cppclass CyMetaData:
        CyMetaData() except +

        void Hash() except +
        void addsamples(int index, int _range, string sample) except +
        void addconfig(string key, string val) except +
        void processkeys(vector[string], unsigned int num) except +
        void FindMissingKeys() except +

        meta_t Export() except +
        void Import(meta_t) except +

        map[string, vector[string]] MakeGetter() except +
        map[string, int] GetLength() except +
        string IndexToSample(int index) except +
        string DatasetName() except +
        vector[string] DAODList() except+

        string hash
        int event_index

        meta_t container

