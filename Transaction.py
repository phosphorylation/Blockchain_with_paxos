class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

    def output_bytes(self):
        result = ""
        if self.sender != 0:
            result += str(self.sender)

        if self.receiver != 0:
            result += str(self.receiver)

        if self.amount != 0:
            result += str(self.amount)

        return result.encode()

    def display(self):
        print(f"({self.sender}, {self.receiver}, ${self.amount})", end=" ")
