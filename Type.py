class Prepare:
    def __init__(self, ballot):
        self.ballot = ballot


class Promise:
    def __init__(self, ballot, acceptNum, acceptVal):
        self.ballot = ballot
        self.acceptNum = acceptNum
        self.acceptVal = acceptVal


class Accept:
    def __init__(self, b, v):
        self.b = b
        self.v = v


class Accepted:
    def __init__(self, b, v,you):
        self.b = b
        self.v = v
        self.you =you


class Decision:
    def __init__(self, v):
        self.v = v


class Ballot:
    def __init__(self, num, process_id, depth):
        self.num = num
        self.process_id = process_id
        self.depth = depth

    def increment_num(self):
        self.num = self.num + 1

    def __ge__(self, other):
        if self.num > other.num:
            return True
        elif self.num == other.num and self.process_id >= other.process_id:
            return True
        else:
            return False

    def __le__(self, other):
        if self.num < other.num:
            return True
        elif self.num == other.num and self.process_id <= other.process_id:
            return True
        else:
            return False
