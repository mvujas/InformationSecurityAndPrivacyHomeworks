import hashlib
import base64
import json

TARGET = int(2**235)#int.from_bytes(b'\x0f\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff', byteorder='big', signed=False) 

class Block:
    def __init__(self, data, previous, p_o_w):
        if not (isinstance(previous, bytes) and len(previous) in [1, 32]):
            raise ValueError('Previous must be bytes object')
        if not (isinstance(data, bytes) and len(data) <= 4096):
            raise ValueError('Data must be bytes object of size between 0 and 4096')
        if not Block.is_valid_p_o_w(p_o_w):
            raise ValueError('Invalid Proof of Work')
        self.data = data
        self.previous_hash = previous * (32 // len(previous))
        self.p_o_w = p_o_w

    def hash(self):
        return hashlib.sha256(
            self.data + self.previous_hash + self.p_o_w).digest()

    def encode(self):
        json_object = json.dumps({
            'data': base64.b64encode(self.data).decode(),
            'previous': self.previous_hash.hex(),
            'p_o_w': self.p_o_w.hex()
        })
        return json_object.encode('utf-8')

    @staticmethod
    def decode(b):
        json_object = b.decode()
        value = json.loads(json_object)
        block = Block(
            base64.b64decode(value['data'].encode()),
            bytes.fromhex(value['previous']),
            bytes.fromhex(value['p_o_w']))
        return block

    @staticmethod
    def is_valid_p_o_w(p_o_w):
        p_o_w_hash_int = int.from_bytes(
            hashlib.sha256(p_o_w).digest(), byteorder='big', signed=False)
        return len(p_o_w) == 8 and p_o_w_hash_int <= TARGET