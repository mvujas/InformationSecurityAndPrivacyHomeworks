import os
import time
import string
import hashlib
from multiprocessing import Pool, cpu_count
from queue import LifoQueue

ALPHABET = string.ascii_lowercase + string.digits
"""
Results obtained after 6 hours on very low end processor with 4 cores:
('7rimq7', 'f5cd3218d18978d6e5ef95dd8c2088b7cde533c217cfef4850dd4b6fa0deef72')
('26i4id', '10dccbaff60f7c6c0217692ad978b52bf036caf81bfcd90bfc9c0552181da85a')
('2vdxm', '1035f3e1491315d6eaf53f7e9fecf3b81e00139df2720ae361868c609815039c')
('xontbc', '37a2b469df9fc4d31f35f26ddc1168fe03f2361e329d92f4f2ef04af09741fb9')
('xex167', '7c58133ee543d78a9fce240ba7a273f37511bfe6835c04e3edf66f308e9bc6e5')
('szpn9', '19dbaf86488ec08ba7a824b33571ce427e318d14fc84d3d764bd21ecb29c34ca')
('j67c', '845e7c74bc1b5532fe05a1e682b9781e273498af73f401a099d324fa99121c99')
('gi02n', 'dd9ad1f17965325e4e5de2656152e8a5fce92b1c175947b485833cde0c824d64')
('feh9ay', '06240d77c297bb8bd727d5538a9121039911467c8bb871a935c84a5cfe8291e4')
('bgfvf', 'a6fb7de5b5e11b29bc232c5b5cd3044ca4b70f2cf421dc02b5798a7f68fc0523')
"""
HASHES = set([
    '7c58133ee543d78a9fce240ba7a273f37511bfe6835c04e3edf66f308e9bc6e5',
    '37a2b469df9fc4d31f35f26ddc1168fe03f2361e329d92f4f2ef04af09741fb9',
    '19dbaf86488ec08ba7a824b33571ce427e318d14fc84d3d764bd21ecb29c34ca',
    '06240d77c297bb8bd727d5538a9121039911467c8bb871a935c84a5cfe8291e4',
    'f5cd3218d18978d6e5ef95dd8c2088b7cde533c217cfef4850dd4b6fa0deef72',
    'dd9ad1f17965325e4e5de2656152e8a5fce92b1c175947b485833cde0c824d64',
    '845e7c74bc1b5532fe05a1e682b9781e273498af73f401a099d324fa99121c99',
    'a6fb7de5b5e11b29bc232c5b5cd3044ca4b70f2cf421dc02b5798a7f68fc0523',
    '1035f3e1491315d6eaf53f7e9fecf3b81e00139df2720ae361868c609815039c',
    '10dccbaff60f7c6c0217692ad978b52bf036caf81bfcd90bfc9c0552181da85a'
])

def possible_password_generator(alphabet, min_size, max_size):
    stack = LifoQueue(100000)
    for ch in alphabet:
        stack.put(ch)
    while not stack.empty():
        pw = stack.get()
        
        pw_len = len(pw)
        if pw_len >= min_size:
            yield pw
        
        if pw_len < max_size:
            for ch in alphabet:
                stack.put(pw + ch)


def worker_job(password):
    hexdigest = hashlib.sha256(password.encode()).hexdigest()
    return (password, hexdigest) if hexdigest in HASHES else None


with Pool(processes=cpu_count() - 1) as pool:
    for worker_result in pool.imap_unordered(
            worker_job, 
            possible_password_generator(ALPHABET, 4, 6),
            chunksize=10000):
        if worker_result is not None:
            print(worker_result)