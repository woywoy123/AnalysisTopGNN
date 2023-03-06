import hashlib 

class Hashing:

    def __init__(self):
        pass
    
    def MD5(self, inpt):
        return str(hashlib.md5(inpt.encode("utf-8")).hexdigest())
