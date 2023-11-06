.. _code-types:

Code Tracing
************

This module is used to preserve the state of a passed object without requiring the original source code.
Unlike `pickle`, this module doesn't store the attributes of the object, but rather the code which is needed to instantiate the object. 
The downside of relying only on `pickle` is that when the original source code is lost or modified, the reconstruction (or `unpickling`) process fails. 
This is because `pickle` only preserves the objects **attributes** rather than it's source code definition.
The `Code` module scans and traces the given object, and attempts to save it's definition such that the object is always available. 
Naturally, this module can be used in tandem with `pickle`, where the module is used to reconstruct the object definition and `pickle` reconstruct the object state.


.. py:class:: Code(instance input = None)

    :params instance input: An instance of the object to target.

    .. py:method:: is_self(other)

        Returns a boolean value indicating whether the input object is also a code object.

    .. py:method:: AddDependency(list[code_t] inpt)

        Expects a list of **code_t** dictionary like content (see :ref:`data-types`.)

    :ivar Object InstantiateObject: 

        Returns a wrapped code type object of the original instance.
        During the instantiation process, if the instance is a class, then an additional attribute is added to the object called **code**.
        This attribute is a struct of type **code_t**, and allows for calling the source code in different contexts (e.g. within a thread).

    :ivar str hash: Returns a string which is derived from hashing the source code.
    :ivar callable fx: Returns the input function.
    :ivar bool is_class: Returns a boolean indicating whether the input was a class
    :ivar bool is_function: Returns a boolean indicating whether the input was a function 
    :ivar bool is_callable: Returns a boolean indicating whether the input function can be called, e.g. ``name()``
    :ivar bool is_initialized: 

        Returns a boolean indicating whether the input function was already initialized.
        This can be particularly useful when the input has input requirements before being called, e.g. ``__init__(self, var1)``.

    :ivar str function_name: Returns a string of the function name if the input was a function, else an empty string is returned.
    :ivar str class_name: Returns a string of the class name if the input was a class, else an empty string is returned.
    :ivar str source_code: Returns the original source code of the file from which the object originated from.
    :ivar str object_code: Returns the object definition source code.
    :ivar list[str] co_vars: Returns a list of the input variables.
    :ivar dict[str, str] input_params: Returns a dictionary of the co-variables with their default values.
    :ivar dict param_space: 

        An empty placeholder used to add additional parameters to the object. 
        This can be useful when the instantiated object requires some input, which is not always available during instantiation.

    :ivar list defaults: Returns a list of default input variable values.
    :ivar None trace: Returns a dictionary outlining the dependency tree of the object and any external imports.
    :ivar dict extern_imports: A dictionary of external libraries that the code relies on.
