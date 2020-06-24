import hashlib
import random
from struct import pack
from Transaction import Transaction


class Block:
    def __init__(self):
        self.transactions = []
        self.nonce = 0
        self.previous_hash = ""
        self.current_hash = ""

    def output_bytes(self):
        result = b""
        for transaction in self.transactions:
            result += transaction.output_bytes()
        nonce_bytes = pack("I", self.nonce)
        result += nonce_bytes + self.previous_hash.encode()

        return result

    def update_sha256(self):
        self.current_hash = hashlib.sha256(self.output_bytes()).hexdigest()

    def update_current_hash_and_compute_nonce(self):
        while self.current_hash == "" or self.current_hash[-1] > "4":
            self.nonce = random.randint(0, 4294967295)
            self.update_sha256()

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    def compute_balance_change(self, current_process_id):
        change = 0
        for transaction in self.transactions:
            if transaction.sender == current_process_id:
                change -= transaction.amount

            elif transaction.receiver == current_process_id:
                change += transaction.amount

        return change

    def print_block(self):
        for transaction in self.transactions:
            transaction.display()
        print("")

    def delete_previous_transaction(self):
        self.transactions.pop(-1)
