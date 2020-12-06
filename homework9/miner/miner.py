import sys
import time
import socket
import threading
import random
import multiprocessing
from block import Block, TARGET
from blockchain import BlockChain


class Miner:

    def __init__(self, host, port, miners, genesis):
        self.address = (host, port)
        self.__blockchain = None
        self.miners = miners
        self.genesis = genesis
        self.__read_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__write_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__write_lock = threading.Lock()
        self.__block_queue = multiprocessing.Queue()
        self.__receive_process = threading.Thread(target=self.__receive_blocks)
        self.__update_process = threading.Thread(target=self.__update_chain)

    def broadcast(self, block):
        for miner in self.miners:
            self.__write_lock.acquire()
            self.__write_socket.sendto(block.encode(), miner)
            self.__write_lock.release()

    def __find_p_o_w(self):
        max_val = int.from_bytes(b'\xff' * 8, byteorder='big', signed=False)
        p_o_w = None
        for i in range(max_val + 1):
            i_bytes = i.to_bytes(8, 'big')
            if Block.is_valid_p_o_w(i_bytes):
                p_o_w = i_bytes
                break
        return p_o_w
        

    def __receive_blocks(self):
        while True:
            data, addr = self.__read_socket.recvfrom(1024)
            new_block = Block.decode(data)
            self.__block_queue.put(new_block)

    def __update_chain(self):
        while True:
            block = self.__block_queue.get()
            if not Block.is_valid_p_o_w(block.p_o_w):
                raise ValueError('Received a block, but it has invalid Proof of work!')
            if self.__blockchain is None:
                self.__blockchain = BlockChain(block)
                print('Block chain created')
            else:
                if self.__blockchain.append(block) is None:
                    print('Received block but didnt add')
                else:
                    print('Block added')

    def __create_block(self, block):
        self.__block_queue.put(block)
        self.broadcast(block)

    def run(self):
        self.__read_socket.bind(self.address)
        self.__receive_process.start()
        self.__update_process.start()
        if self.genesis:
            time.sleep(.1)
            genesis_block = Block(b'I\'m the one that come before all others', b'\x00', self.__find_p_o_w())
            self.__create_block(genesis_block)   

        while True:
            time.sleep(1e-3)
            if self.__blockchain is not None:
                proof_of_work = self.__find_p_o_w()
                target = self.__blockchain.blocks[-1] if self.__blockchain.blocks else self.__blockchain.root
                new_block = Block(b'Random block', target.hash(), proof_of_work)
                self.__create_block(new_block)

def parse_address(address):
    tokens = address.strip().split(':')
    if len(tokens) == 2:
        host, port = tokens
    else:
        host = tokens[0]
        port = 1000
    port = int(port)
    return (host, port)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 miner.py [addr] [others] [genesis]")
        print("\taddr:\t\taddress of the miner in the format " \
             "host:port")
        print("\tothers:\t\tcomma-separated list of the other " \
              "miners' addresses \n\t\t\tin the format host:port," \
              "host:port,...")
        print("\tgenesis:\toptional, \"genesis\" if the miner must " \
                "generate\n\t\t\tthe genesis block")
        sys.exit(0)
    miner_address = parse_address(sys.argv[1])
    other_miners = [parse_address(address) for address in sys.argv[2].strip().split(',')]
    produce_genesis = len(sys.argv) > 3 and sys.argv[3].strip() == 'genesis'
    miner = Miner(*miner_address, other_miners, produce_genesis)
    miner.run()