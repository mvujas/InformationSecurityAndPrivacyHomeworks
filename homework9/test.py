from miner import BlockChain, Block

genesis = Block(b'', b'\x00')
bc = BlockChain(genesis)
b1 = Block(b'perica', genesis.hash())
print(bc.append(b1) is not None)
b2 = Block(b'perica2', genesis.hash())
print(bc.append(b2) is not None)
