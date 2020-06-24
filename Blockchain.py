from Block import Block


class Blockchain:
    def __init__(self, process_id):
        self.chain = []
        self.balance = 50
        self.process_id = process_id
        self.temp_block = Block()

    def add_transaction_to_temp_block(self, transaction):
        self.temp_block.add_transaction(transaction)

    def withdraw_previous_temp_transcation(self):
        self.temp_block.delete_previous_transaction()

    def compute_temp_block_nonce(self):
        if len(self.chain) != 0:    # empty chain
            self.temp_block.previous_hash = self.chain[-1].current_hash
        self.temp_block.update_current_hash_and_compute_nonce()

    def officially_append_the_temp_block(self):
        self.balance += self.temp_block.compute_balance_change(self.process_id)

        if len(self.chain) > 0:  # if currently non-empty chain, update previous_hash
            self.temp_block.previous_hash = self.chain[-1].current_hash
        self.chain.append(self.temp_block)
        self.temp_block = Block()    # reset

    def officially_append_outside_block(self, block):
        if len(self.chain) == 0:        # currently empty chain
            self.balance += block.compute_balance_change(self.process_id)
            self.chain.append(block)
        else:                           # non-empty chain
            if block.previous_hash != self.chain[-1].current_hash:      # previous hash must match
                print("Invalid Block")
            else:
                self.balance += block.compute_balance_change(self.process_id)
                self.chain.append(block)

    def print_chain(self):
        for this_block in self.chain:
            this_block.print_block()

