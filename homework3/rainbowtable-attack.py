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

if args.columns % 2 == 1:
    args.columns += 1


def perform_chain(col, max_col, starting_val):
    current_value = starting_val
    do_reduction = bool(col % 2)
    for col_num in range(col, max_col):
        if do_reduction:
            current_value = reduction_function(
                ALPHABET, current_value, col_num // 2)
        else:
            current_value = hash_function(current_value)
        do_reduction = not do_reduction
    return current_value



def table_generation_job(row_num):
    start_str = reduction_function(ALPHABET, hex(row_num))
    final_hash = perform_chain(0, args.columns, start_str)
    return (start_str, final_hash)


def table_generation_job_reduction(accumulator, entry, f):
    start, end = entry
    if end in accumulator:
        accumulator[end].append(start)
    else:
        accumulator[end] = [start]
    print(f'{start} {end}', file=f)
    return accumulator


class cracking_job:
    def __init__(self, rainbow_table):
        self.__rainbow_table = rainbow_table
    
    def __call__(self, hash_to_crack):
        found = False
        col = args.columns
        if args.columns % 2 == 0:
            col -= 1
        solution = None
        while not found and col > 0:
            final_hash = perform_chain(col, args.columns, hash_to_crack)
            try:
                starting_vals = self.__rainbow_table[final_hash]
                for starting_val in starting_vals:
                    cleartext = perform_chain(0, col - 1, starting_val)
                    if hash_function(cleartext) == hash_to_crack:
                        solution = (hash_to_crack, (cleartext, starting_val, col))
                        found = True
                        break
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

'''
a = [
    ('7c63ef24d0be87ab25286f9e62a4b8d109022ee29d55806f65afa409e7ed8f19', ('8ee8rw0b', '4zlaaaaa', 191)),
    ('378d76c8c714995c7704dd87657883ec3e353ce806252cb6fc90402af2e562f7', ('7a789hkp', 'kiacaaaa', 543)),
    ('30005408c97e2eed4153235805b1e13962cc93394712499ca2aa013d66c849a4', ('a3eq5n37', 'd8uaaaaa', 195)),
    ('fde32abf5fa6e9ace91c248d452fdee4bd73c5a8dcc50082a24aa7407fb981ae', ('v7a5i8xl', 'zn1aaaaa', 277)),
    ('48b15bd51308132d52161241950db12e20fc022c66de93822576844ab8f8f412', ('prz2v88o', 'gq8aaaaa', 97)),
    ('431682ab1e714ca5201f399ae20a7285e52f5ac567ee3e4b3150a6944ad258da', ('urqw5ztj', 'qxwbaaaa', 473)),
    ('6ec98c6005cc53171c71a49cfa3b7f79b5c792ab74b579a3ad2c9fd100b244f7', ('clud92oc', 'a6ybaaaa', 201)),
    ('bda636842265dacfac9bdaf79154bab95680f945bad33ef3a3c0b5bb251a53d1', ('sjd2za0e', 'yxrbaaaa', 379)),
    ('57f96fb76dd7901bf5c7dcca37e99355add8eadbe960af48a57e0c90258b3767', ('ys7g4lhr', 'i7eaaaaa', 333)),
    ('b791bc0a40bbba785d4ad4c2ab80ff3a546b53fdeb2672c87da2b277c75a026d', ('6yo486i4', 'yaecaaaa', 189)),
    ('a31ac7ecd04c4abf40379af1d22bdf0eb923a311c1efb7178518b9213aa1b758', ('67uxs1r9', 'axtaaaaa', 211)),
    ('1db3b9761b0d9999c5b415f169e225d1d48f9694b2ae4884d891122a6163cf95', ('nko3x1bx', 'c4jaaaaa', 381)),
    ('380f0814a0b20aa870d31ee3db30974aa9509689dedd27217a7a663d12e86d20', ('ib6har43', 'fn0aaaaa', 303)),
    ('0e18218cd44895d5d8f3ffccbaf7e13fbd0965b320d407a1fd91d3750d465ef2', ('jkibfofp', 'ulwaaaaa', 39)),
    ('65d49e2359dff4d5b3edf3c8394a5460352247ff44911462559be66f30c81722', ('qsginsov', 'c1oaaaaa', 737)),
    ('9329552d77e31a9e54b7193d614eea6a6f6e74f90844945fa0870c1e75e05bc2', ('zijq6vb0', '0fwaaaaa', 691)),
    ('9b9ed470dc6d31e8a218aaceda23eb4fd7fbf59e68502aef42922c1090fbf88e', ('wyoiyuzh', 'h9iaaaaa', 269)),
    ('29d9efe23e15d727d98414c247c994f27f810c4c6461c5e15e222e20fc14631a', ('rjosw4nf', '9e3aaaaa', 349)),
    ('78db9ac0baced63158284290606c36a99c6bdc33a493175f59fc8b494872553b', ('46vf1loj', 'feecaaaa', 587)),
    ('fe704a0a128f98b0ca821113e7462d8c395e89e468c4462add74a51a3050bf2e', ('ny62cp9i', 'br8aaaaa', 119)),
    ('b0ab9deb9744ede5aa1aa87e605ee76b405c73f0eac4b2e7b85a5d8e91686544', ('bzbgwbey', 'bktbaaaa', 217)),
    ('05ce910a22660babf6e651a054b0eb7a4b622163b806ade5df39900a854b4a19', ('tuvpbuv4', 'evfaaaaa', 159)),
    ('6c5e34c1fc408a4c4d8780e6818450ba4a8e00dd3cc93702574312fa5dc69c3f', ('n1ncekdk', 'vkqbaaaa', 67)),
    ('dddbd9d9e05c3eb7c45126c1fddac41e7ae575babd1518d90df931b29df4d3bf', ('hlazabxp', '5jlaaaaa', 219)),
    ('9111e4873524c0f1695c8f8742220c3dbf6f8f71510c1a50e616d5e47691b2f6', ('49vdoxc0', '64ccaaaa', 309)),
    ('0fa29cd6bf2f510db878c102f22349ef165461993794a882a13f7f01bf3216a7', ('tfhliy6s', 'njvbaaaa', 519)),
    ('8d1073209532adf302586abcef72bf72d618635d21c133edaa42f4d4dc4b2670', ('r90vmblw', 'cudcaaaa', 653)),
    ('afbd85f28b08d43d507b5b5a3c7bf5d78d70b619a6b08f31a04c11c2508a96b7', ('fk4z0v68', 'tq2baaaa', 353)),
    ('75b510322c2a6c86b0760f798ebbae92d99801dc5fb5679979c911b519bf2fec', ('vsfwjtku', 'ib5aaaaa', 345)),
    ('c457247a3301bf9a884bd353fc18146e9cd34fd88149e403a1830a01e172e375', ('lntsxaiu', 'vc8baaaa', 161)),
    ('03385ff741d36a8de85003fc409a48019ce8253118fcc0a516435a36dfd58b12', ('adgnrwka', 'smhaaaaa', 511)),
    ('b22a939f45b36e8ed62c00f96a71de46336bbc2fc597ada0dec9e2cc5a57a5a4', ('98os60ag', '6kxaaaaa', 355)),
    ('b5251b92016fb87f54e7459ad128bec97cabba5e2a6bbe24813b53c86d43f1bc', ('ae1q6mn6', 'v4faaaaa', 497)),
    ('dc6866d1fd8ffbac981d25c080bf7e4b427cade70daec47de031456e5691e41e', ('wiitapc6', '0oibaaaa', 803)),
    ('51137e89850388b84ee616a4689e6f1b8cbe1ba5b1fab713bcce4f65abc681c9', ('df9ojbbb', 'ubbcaaaa', 201)),
    ('8cf71a4c5c0bb0c3ed39e635aa35b4fda89d16b0f3469659998079298f89801b', ('upfwakjp', 'e4oaaaaa', 157)),
    ('a316d9944b8b9ca236b77b8657d90b046483692d0033766bdcb87c8a14947f41', ('irt5dua1', 'vm5aaaaa', 109)),
    ('bcec583abe94269b7b96fa1396a0afe0b55178a47203291ec78614c925b38a64', ('j2df88df', 'j3caaaaa', 643)),
    ('c09c569a480ef0016ec6f90a4d7ad82568e76b53456d9e07c3d21383ebf339a1', ('zy6838a4', '0h4baaaa', 535)),
    ('875f039f4aed271c8772f6006c78544486b17f9e752686914059a664dd238584', ('mrnorvy6', 'bgvbaaaa', 155)),
    ('9613a78a584fefd042cfa455515c49e9e21903c1ad959c4fd07dd97ff644bc9b', ('5ydvd2va', 'cpsaaaaa', 467)),
    ('b0f46a5dbc68a7aae81b6e21e24a8615c02adf288836ad8bd860fb29b5f367eb', ('v9pum1j3', '4mnbaaaa', 115)),
    ('48910a4957eb162811e2f574a7ae69cf1121094d415badc965199afe289c50c5', ('zvupnq8b', 'e9eaaaaa', 241)),
    ('1f3406bd705e50b90e6b73065694696d9853cfe166f44f1bd2ac22c2cc590ad8', ('pn4a3gbp', 'je0aaaaa', 377)),
    ('5dd87c553bc221e07fb048bc5bf328a4e0499647c9e75b1e9ac42ab3da5fad6d', ('cuiib9qf', '9o9baaaa', 197)),
    ('3d114dca0a0b90a39082b000fd137c63498f9b5b8ded2b7ff20ff171e26c504d', ('qjg199jf', 'nw3baaaa', 25)),
    ('3de99a987ec88b5a1334b8938ca26a46c487ba6c6129fc7ea86614338d91fba9', ('d9tmoyfj', 'aslbaaaa', 617)),
    ('63e2c17e258751105e455a5a0b65cd886ae071d86c7e274f0e19eddd751095a3', ('ybgtrwro', 't3taaaaa', 53)),
    ('78dfe7440354093e49849b977d6f65f412452bdaa1db20910f2be4fa2815b8c3', ('nyisofag', 'r2ccaaaa', 463)),
    ('e1746a0df104830ab692c63b9541c7e5ab95cddaab84e69dfd299d00d723ddd1', ('no6ukl5r', 'ps0aaaaa', 361)),
    ('af2a12e50f650ff0005dccd3e5fd5baba0f46369b67bf4d4013d033c3a0397f8', ('znr7e1n2', 'jndcaaaa', 483)),
    ('cf36484332e4ca5700a2513c95dd95e7fd65059518d13361af6aad7768e23849', ('xvv2dfyp', 'cwabaaaa', 95)),
    ('ff20eb60b553b276215e20699813c319bd3c7001bc7a659a1117c9e03f346d09', ('zf6knr0p', '9mfaaaaa', 145)),
    ('b97e3f4bbd1f0e5dfbcc9a4dd9f6e4682f4ec1cb78cecfbf054368a6ac4ea353', ('nhhn0sir', 'fnnaaaaa', 179)),
    ('6a7b0025df46afcdc40968500061ed1143d27adbb3c064c5df2ef63ef7127db3', ('4qfqor6y', 'mreaaaaa', 201)),
    ('a2225d8a74e1c678d3bab82f3de106ec37e318638b065ea461fdee97f0d58ccf', ('0zwz4oih', 'vobcaaaa', 59)),
    ('de9d469df4685a29d72f178acc0c3f4939bf002c323c5d7d1a578d7ecec9c2bd', ('j5r05x15', 'drvbaaaa', 559)),
    ('03ad03de858514d64005a270bcae5108509f1a0a0927bacef48aa04bc9576f5d', ('zr7c6k8e', '4i7baaaa', 277)),
    ('4e3b0d18326477b3cea438f965fa7fdda818956b1ea17539e674cbdc9d2d3b87', ('ck3w3qes', 'a04baaaa', 193)),
    ('393ab9620b82f9aa976c74ced63c34e92c470bb88edd620fec3feadb5e57a61e', ('ohpnjolc', 'b3fbaaaa', 17))
]

for hash_, (pw, start, col) in a:
    for i in range(1, 1001, 2):
        if perform_chain(0, i, start) == hash_:
            print('Equal', pw, i, col)

exit(0)
'''

with Pool(processes=cpu_count()) as pool:
    with open(f'rainbow_table_{args.rows}X{args.columns}.txt', 'w') as f:
        print(args.columns, file=f)
        # Generate rainbow table
        print(f'    Generating rainbow table of size {args.rows}X{args.columns}...')
        rainbow_table = reduce(lambda acc, x: table_generation_job_reduction(acc, x, f), 
            pool.imap_unordered(table_generation_job, range(args.rows)),
            {})

    print('Table size', len(rainbow_table))

    '''
    import random
    for k in range(1000):
        rand = random.randint(0, args.rows)
        s = reduction_function(ALPHABET, hex(rand))
        rand = random.randint(0, args.columns - 2) 
        if rand % 2 == 0:
            rand += 1
        print(perform_chain(0, rand, s))
    '''

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