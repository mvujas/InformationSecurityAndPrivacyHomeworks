import asyncio
import websockets
import os
from hashlib import sha256

EMAIL = "your.email@epfl.ch"
PASSWORD = "correct horse battery staple"
H = sha256
N = int('EEAF0AB9ADB38DD69C33F80AFA8FC5E86072618775FF3C0B9EA2314C9C256576D674DF7496EA81D3383B4813D692C6E0E0D5D8E250B98BE48E495C1D6089DAD15DC7D7B46154D6B6CE8EF4AD69B15D4982559B297BCF1885C529F566660E57EC68EDBC3C05726CC02FD4CBF4976EAA9AFD5138FE8376435B9FC61D2FC0EB06E3', 16)
g = 2

U = EMAIL

def calc_A(a):
    return pow(g, a, N)

def encode_int(n):
    return format(n, 'x').encode()

def calc_u(A, B):
    h = H()
    h.update(encode_int(A))
    h.update(encode_int(B))
    return int(h.hexdigest(), 16)

def calc_x(salt, U, PASSWORD):
    def calc_inner_hash(U, PASSWORD):
        h = H()
        h.update(U.encode())
        h.update(':'.encode())
        h.update(PASSWORD.encode())
        return int(h.hexdigest(), 16)
    h = H()
    h.update(encode_int(salt))
    h.update(encode_int(calc_inner_hash(U, PASSWORD)))
    return int(h.hexdigest(), 16)

def calc_S(B, g, x, a, u, N):
    degree = a + u * x
    base = B - pow(g, x, N)
    return pow(base, degree, N)

def calc_check(A, B, S):
    h = H()
    h.update(encode_int(A))
    h.update(encode_int(B))
    h.update(encode_int(S))
    return int(h.hexdigest(), 16)

async def exchange():
    uri = "ws://127.0.0.1:5000/"
    async with websockets.connect(uri) as websocket:
        # Client step 1
        encoded_email = EMAIL.encode()
        await websocket.send(encoded_email)
        
        # After server step 1
        salt_hex = await websocket.recv()
        salt = int(salt_hex, 16)

        # Client step 2 
        a = int.from_bytes(os.urandom(32), 'big')
        A = calc_A(a)
        await websocket.send(encode_int(A))

        # After server step 2
        B_hex_encoded = await websocket.recv()
        B = int(B_hex_encoded, 16)
        
        # Client step 3
        u = calc_u(A, B)

        x = calc_x(salt, U, PASSWORD)

        S = calc_S(B, g, x, a, u, N)

        check_hash = calc_check(A, B, S)
        print(check_hash)
        await websocket.send(encode_int(check_hash))#.lstrip('0'))

        last_msg = await websocket.recv()
        print(last_msg)

asyncio.get_event_loop().run_until_complete(exchange())