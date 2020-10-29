import re
import os
import hashlib
from multiprocessing import Pool, Process, cpu_count, Queue
from queue import Empty
from functools import reduce

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DICTIONARY_DIR = os.path.join(BASE_DIR, 'dictionaries')
OUTPUT_FILE = 'dictionary-attack-with-salt-cracked-passwords.txt'

HASH_SALT_STR = [
    '962642e330bd50792f647c1bf71895c5990be4ebf6b3ca60332befd732aed56c(b9)',
    '8eef79d547f7a6d6a79329be3c7035f8e377f9e629cd9756936ec233969a45a3(be)',
    'e71067887d50ce854545afdd75d10fa80b841b98bb13272cf4be7ef0619c7dab(bc)',
    '889a22781ef9b72b7689d9982bb3e22d31b6d7cc04db7571178a4496dc5ee128(72)',
    '6a16f9c6d9542a55c1560c65f25540672db6b6e121a6ba91ee5745dabdc4f208(9f)',
    '2317603823a03507c8d7b2970229ee267d22192b8bb8760bb5fcef2cf4c09edf(17)',
    'c6c51f8a7319a7d0985babe1b6e4f5c329403d082e05e83d7b9d0bf55876ecdc(94)',
    'c01304fc36655dd37b5aa8ca96d34382ed9248b87650fffcd6ec70c9342bf451(7f)',
    'cff39d9be689f0fc7725a43c3bdc7f5be012c840b9db9b547e6e3c454a076fc8(2e)',
    '662ab7be194cee762494c6d725f29ef6321519035bfb15817e84342829728891(24)'
]
HASH_SALT_PAIR = []
hash_salt_re = re.compile(r'^(?P<hash>.*)\((?P<salt>.{2})\)$')
for hash_salt in HASH_SALT_STR:
    m = hash_salt_re.match(hash_salt)
    if m:
        HASH_SALT_PAIR.append((m.group('hash'), m.group('salt')))


file_encodings = os.popen(
    f'file -i "{DICTIONARY_DIR}"/*').read().split('\n')
dictionary_files_encoding = {}
file_command_regex = re.compile('^(.+?):.*charset=(.+)$')
for line in file_encodings:
    m = file_command_regex.match(line)
    if m:
        file_path = m.group(1)
        encoding = m.group(2)
        dictionary_files_encoding[file_path] = encoding


def producer(files, collection):
    for file_name in files:
        print('---------', file_name)    
        with open(file_name, 'rb') as f:
            for line in f:
                try:
                    tokens = line.decode(files[file_name]).strip().split()
                    if len(tokens) > 0:
                        collection.put(tokens[-1])
                except:
                    pass

def intermediate_consumer(collection):
    try:
        while True:
            yield collection.get(timeout = 2)
    except Empty:
        print('Finish')


def worker_job(word):
    match_entry = {}
    possible_pw = word
    for hash_to_crack, salt in HASH_SALT_PAIR:
        pw_salt = possible_pw + salt
        digest = hashlib.sha256(pw_salt.encode()).hexdigest()
        if digest == hash_to_crack:
            match_entry[f'{hash_to_crack}({salt})'] = possible_pw
    return match_entry


def reducer(current, new_entry):
    for key in new_entry:
        if key not in current:
            current[key] = new_entry[key]
    return current


queue = Queue(200000)
prod = Process(target=lambda: producer(dictionary_files_encoding, queue))
prod.start()

with Pool(processes=cpu_count() - 1) as pool:
    found_passwords = reduce(reducer,
        pool.imap_unordered(worker_job, intermediate_consumer(queue), chunksize=1000),
        {})

output_file_path = os.path.join(BASE_DIR, OUTPUT_FILE)
with open(output_file_path, 'a') as f:
    for hash_and_salt in found_passwords:
        print(f'HASH(SALT): PASSWORD {hash_and_salt}: {found_passwords[hash_and_salt]}', file=f)
