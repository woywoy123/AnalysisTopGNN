import importlib
import inspect

def StringToObject(module, name):
    modul = importlib.import_module(module)
    obj = getattr(modul, name)
    return CheckObjectInputs(obj)

def CheckObjectInputs(obj):
    _def = obj.__init__.__defaults__
    _req = [i for i in obj.__init__.__code__.co_varnames if i != "self"]

    if _def == None:
        return None, obj()
    _dic = {_req[i] : _def[i] for _, i in zip(_def, range(len(_req)))}
    return _dic, obj  


def GetSourceCode(obj):
    try:
        return inspect.getsource(obj)
    except:
        return inspect.getsource(obj.__class__)


def GetSourceFile(obj):
    
    if obj.__class__.__name__ == "type":
        return GetSourceCode(obj)
    try:
        return "".join(open(inspect.getfile(obj.__class__), "r").readlines())
    except: 
        return inspect.getsource(obj)
