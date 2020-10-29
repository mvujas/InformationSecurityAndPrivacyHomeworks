import os
import re
import subprocess
import hashlib
from multiprocessing import Queue, Process, Pool, cpu_count
from queue import Empty
from functools import reduce

import transformationrules

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DICTIONARY_DIR = os.path.join(BASE_DIR, 'dictionaries')
OUTPUT_FILE = 'dictionary-attack-with-rules-cracked-passwords.txt'

HASHES = set([
    '2e41f7133fd134335f566736c03cc02621a03a4d21954c3bec6a1f2807e87b8a',
    '7987d2f5f930524a31e0716314c2710c89ae849b4e51a563be67c82344bcc8da',
    '076f8c265a856303ac6ae57539140e88a3cbce2a2197b872ba6894132ccf92fb',
    'b1ea522fd21e8fe242136488428b8604b83acea430d6fcd36159973f48b1102e',
    '3992b888e772681224099302a5eeb6f8cf27530f7510f0cce1f26e79fdf8ea21',
    '326e90c0d2e7073d578976d120a4071f83ce6b7bc89c16ecb215d99b3d51a29b',
    '269398301262810bdf542150a2c1b81ffe0e1282856058a0e26bda91512cfdc4',
    '4fbee71939b9a46db36a3b0feb3d04668692fa020d30909c12b6e00c2d902c31',
    '55c5a78379afce32da9d633ffe6a7a58fa06f9bbe66ba82af61838be400d624e',
    '5106610b8ac6bc9da787a89bf577e888bce9c07e09e6caaf780d2288c3ec1f0c'
])

#dir_files = os.listdir(DICTIONARY_DIR)
#dictionary_files = [
#    os.path.join(DICTIONARY_DIR, dictionary_name) \
#        for dictionary_name in dir_files \
#            if os.path.isfile(os.path.join(DICTIONARY_DIR, dictionary_name))]


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
                    #print('Can\'t read')


def intermediate_consumer(collection):
    try:
        while True:
            yield collection.get(timeout = 2)
    except Empty:
        print('Finish')


def worker_job(word):
    transformed = transformationrules.apply_transformation_rules(word)
    look_up_entry = {}
    for possible_pw in transformed:
        digest = hashlib.sha256(possible_pw.encode()).hexdigest()
        if digest not in look_up_entry:
            look_up_entry[digest] = possible_pw
    return look_up_entry


def reducer(current, new_entry):
    # Too low RAM to do this
    #for key in new_entry:
    #    if key not in current:
    #        current[key] = new_entry[key]
    for key in new_entry:
        if key not in current and key in HASHES:
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
    for hash_ in found_passwords:
        print(hash_, found_passwords[hash_])
        print(f'HASH, PASSWORD {hash_}: {found_passwords[hash_]}', file=f)