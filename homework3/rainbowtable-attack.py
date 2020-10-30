import os
import argparse
import hashlib
import string
from multiprocessing import Pool, cpu_count
from functools import reduce

PASSWORD_SIZE = 8
ALPHABET = string.ascii_lowercase + string.digits

def reduction_function(alphabet, hash_, column_index=0):
    hash_ = int(hash_, 16)
    # Every column should have 
    hash_ += column_index

    alphabet_size = len(alphabet)
    res_text = ''
    text_size = 0
    while text_size < PASSWORD_SIZE:
        char_index = hash_ % alphabet_size
        res_text += alphabet[char_index]
        hash_ //= alphabet_size
        text_size += 1
    return res_text


def hash_function(text):
    return hashlib.sha256(text.encode()).hexdigest()


DEFAULT_COLS = 1_000
DEFAULT_ROWS = 10_000_000

parser = argparse.ArgumentParser(description='Generate rainbow table')
parser.add_argument('--rows', dest='rows', default=DEFAULT_ROWS, type=int,
                help=f'number of rows of rainbow table (default {DEFAULT_ROWS})')
parser.add_argument('--cols', dest='columns', default=DEFAULT_COLS, type=int,
                help=f'number of columns of rainbow table (default {DEFAULT_COLS})')
parser.add_argument('--hashes', dest='hashesfilename', type=str, required=True,
                help='File with hashes to break')
parser.add_argument('--out', dest='outputfile', type=str, required=True,
                help='Output file')
parser.add_argument('--force', dest='forceout', action='store_true',
                help='Force output')
args = parser.parse_args()

if not os.path.isfile(args.hashesfilename):
    raise ValueError('File with hashes doesn\'t exist')

if not args.forceout and os.path.isfile(args.outputfile):
    raise ValueError('File in place of output file already exist')

if args.columns % 2 == 0:
    args.columns += 1


def perform_chain(col, max_col, starting_val):
    current_value = starting_val
    do_reduction = bool(col % 2)
    for col_num in range(col, max_col):
        if do_reduction:
            current_value = reduction_function(
                ALPHABET, current_value, col_num)
        else:
            current_value = hash_function(current_value)
        do_reduction = not do_reduction
    return current_value



def table_generation_job(row_num):
    start_str = reduction_function(ALPHABET, hex(row_num))
    final_hash = perform_chain(0, args.columns, start_str)
    return (start_str, final_hash)


def table_generation_job_reduction(accumulator, entry):
    start, end = entry
    accumulator[end] = start
    return accumulator


class cracking_job:
    def __init__(self, rainbow_table):
        self.__rainbow_table = rainbow_table
    
    def __call__(self, hash_to_crack):
        found = False
        col = args.columns
        solution = None
        while not found and col > 0:
            final_hash = perform_chain(col, args.columns, hash_to_crack)
            try:
                cleartext = perform_chain(0, col - 1, self.__rainbow_table[final_hash])
                solution = (final_hash, cleartext)
                found = True
            except KeyError:
                col -= 2
        return solution


def cracking_result_reduction(accumulator, entry):
    if entry is not None:
        accumulator.append(entry)
    return accumulator


# Load hash dump
with open(args.hashesfilename, 'r') as hashfile:
    hashes = list(map(lambda s: s.strip(), hashfile.readlines()))

with Pool(processes=cpu_count()) as pool:
    # Generate rainbow table
    print(f'    Generating rainbow table of size {args.rows}X{args.columns}...')
    rainbow_table = reduce(table_generation_job_reduction, 
        pool.imap_unordered(table_generation_job, range(args.rows)),
        {})

    # Crack passwords
    print('    Starting password cracking...')
    cracked_passwords = reduce(cracking_result_reduction,
        pool.imap_unordered(cracking_job(rainbow_table), hashes), 
        [])

if not cracked_passwords:
    print('--- No passwords cracked.')
else:
    print('--- Cracked password:')
    with open(args.outputfile, 'w') as outputf:
        for hash_, cleartext in cracked_passwords:
            print(cleartext)
            print(f'HASH, PASSWORD  {hash_}:{cleartext}', file=outputf)
