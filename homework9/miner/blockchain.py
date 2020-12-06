class BlockChain:

    def __init__(self, genesis_block):
        self.root = genesis_block
        self.root.previous_hash = b'\x00'
        self.blocks = []

    def append(self, new_block):
        is_valid = False
        if self.blocks:
            is_valid = new_block.previous_hash == self.blocks[-1].hash()
        else:
            is_valid = new_block.previous_hash == self.root.hash()
        result = None
        if is_valid:
            self.blocks.append(new_block)
            result = new_block
        return result
