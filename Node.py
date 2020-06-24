from Block import Block
from Blockchain import Blockchain
from threading import Thread
import socket
import time
from Transaction import Transaction
import random
import Type
import pickle
IP = "127.0.0.1"

constant_delay = 5
time_out_a = 2
time_out_b = 5


class Node:
    def __init__(self, process_id):
        self.chain = Blockchain(process_id)
        self.process_id = process_id
        self.message_queue = []     # bytes format
        self.transaction_queue = []

        self.port = 5000 + process_id
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('', self.port))
        self.server_socket.listen(10)

        self.client_socket_list = []  # sending message
        self.connecting_socket_list = []  # receiving message
        self.link_status_list = [1] * 5

        self.time_out = random.randint(time_out_a, time_out_b)
        self.timer = 0

        self.leader_process_id = 0
        self.ballot = Type.Ballot(0, process_id, 0)

        self.acceptNum = Type.Ballot(0, 0, 0)
        self.acceptVal = None

        self.first_count = 0
        self.second_count = 0

        self.success = False

    def active_connection(self):
        for i in range(0, 5):
            if i != self.process_id:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((IP, 5000 + i))
                self.client_socket_list.append(client_socket)
                print("Connecting to Process " + str(i) + " successfully")
            else:
                self.client_socket_list.append(None)

    def passive_connection(self):
        # separate thread, listening for connection
        count_socket = 0
        while count_socket < 5:
            if count_socket == self.process_id:
                self.connecting_socket_list.append(None)
            else:
                connecting_socket, connecting_address = self.server_socket.accept()
                self.connecting_socket_list.append(connecting_socket)
                print("Incoming connection")
            count_socket = count_socket + 1

    def start(self):
        a = Thread(target=self.passive_connection, args=())
        a.start()
        time.sleep(20)
        self.active_connection()
        a.join()
        print("-----You may start entering commands-----")
        self.five_receiving_message_thread()  # creates 5 separate threads to listen to incoming transactions

        Thread(target=self.analyze_message_queue, args=()).start()
        Thread(target=self.start_protocol, args=()).start()

    def moneyTransfer(self, src, dest, amount):
        if src != self.process_id:
            print("Permission Denied!")
        else:
            self.chain.add_transaction_to_temp_block(Transaction(src, dest, amount))
            if self.chain.temp_block.compute_balance_change(self.process_id) > self.chain.balance:
                print("Insufficient Fund")
                self.chain.withdraw_previous_temp_transcation()
            self.timer = time.time()

    def failLink(self, src, dest):
        if src == self.process_id:
            self.link_status_list[dest] = 0

        if dest == self.process_id:
            self.link_status_list[src] = 0

    def fixLink(self, src, dest):
        if src == self.process_id:
            self.link_status_list[dest] = 1

        if dest == self.process_id:
            self.link_status_list[src] = 1

    def failProcess(self):
        for i in range(0, len(self.link_status_list)):
            self.link_status_list[i] = 0

    def printBlockchain(self):
        self.chain.print_chain()

    def printBalance(self):
        print(f"${self.chain.balance}")

    def printQueue(self):
        self.chain.temp_block.print_block()

    def send_message_to_all_process(self, message):
        for i in range(0, len(self.client_socket_list)):
            if i != self.process_id and self.link_status_list[i] == 1:
                object_bytes = pickle.dumps(message)
                self.client_socket_list[i].send(object_bytes)

    def five_receiving_message_thread(self):
        # create 4 separate thread to listen to others
        for process in range(0, len(self.connecting_socket_list)):
            if process != self.process_id:
                Thread(target=self.keep_receiving_message_from_process, args=(process,)).start()

    def keep_receiving_message_from_process(self, process):
        while True:
            if self.link_status_list[process] == 1:
                message_bytes = self.connecting_socket_list[process].recv(1024)
                time.sleep(constant_delay)
                my_object = pickle.loads(message_bytes)
                self.message_queue.append(my_object)

    def if_leader(self):
        return self.process_id == self.leader_process_id

    def analyze_message_queue(self):
        while True:
            if len(self.message_queue) > 0:
                receive = self.message_queue.pop(0)         # pop the fist element in the queue
                if type(receive) == Type.Prepare:      # participant, receive promise phase
                    print("Participant has received a Prepare()")
                    self.participant_promise_phase(receive)
                if type(receive) == Type.Promise and self.process_id == receive.ballot.process_id:
                    print("Leader has received a Promise()")
                    self.leader_accept_phase(receive)
                if type(receive) == Type.Accept and not self.if_leader():
                    print("Participant has received an Accept()")
                    self.participant_accept_phase(receive)
                if type(receive) == Type.Accepted and receive.you ==self.process_id:
                    print("Leader has received a Accepted()")
                    self.leader_decision_phase(receive)
                if type(receive) == Type.Decision and not self.if_leader():
                    print("Participant has received an Decision()")
                    self.participant_decision_phase(receive)

    def leader_prepare_phase(self):
        self.ballot.increment_num()
        self.ballot.process_id = self.process_id
        self.ballot.depth = len(self.chain.chain)
        self.send_message_to_all_process(Type.Prepare(self.ballot))
        print("Leader has walked through Prepare()")

    def participant_promise_phase(self, prepare):
        if prepare.ballot >= self.ballot:
            self.ballot = prepare.ballot
            self.send_message_to_all_process(Type.Promise(self.ballot, self.acceptNum, self.acceptVal))
            self.leader_process_id = prepare.ballot.process_id
            print("Current leader is: " + str(self.leader_process_id))
            print("Participant has sent a Promise()")

    def leader_accept_phase(self, promise):
        max_previous_ballot_num = Type.Ballot(0, 0, 0)
        self.first_count = self.first_count + 1
        if promise.acceptVal != 0 and promise.acceptNum >= max_previous_ballot_num:
            self.acceptVal = promise.acceptVal
            max_previous_ballot_num = promise.acceptNum

        if self.first_count == 2:
            self.send_message_to_all_process(Type.Accept(self.ballot, self.chain.temp_block))
            self.leader_process_id = self.process_id
            print("Leader Prepare Phase Complete!")
            print("Current leader is: " + str(self.leader_process_id))
        # elif self.first_count == 4:
        #     self.first_count = 0

    def participant_accept_phase(self, accept):
        if accept.b >= self.ballot:
            self.acceptNum = accept.b
            self.acceptVal = accept.v
            print("Current leader is: " + str(self.leader_process_id))
            self.send_message_to_all_process(Type.Accepted(self.ballot, self.acceptVal,self.acceptNum.process_id))
            print("Participant has sent a Accepted()")

    def leader_decision_phase(self, accepted):
        self.second_count = self.second_count + 1

        if self.second_count == 2:
            self.success = True
            self.send_message_to_all_process(Type.Decision(accepted.v))
            self.chain.officially_append_the_temp_block()
            print("Leader Decision Phase Complete!")
        elif self.second_count == 4:
            self.reset_protocol()

    def participant_decision_phase(self, decision):
        self.chain.officially_append_outside_block(decision.v)
        self.reset_protocol()

    def pack_block(self):
        self.chain.compute_temp_block_nonce()
        self.timer = 0

    def start_protocol(self):
        while True:
            if self.timer != 0 and time.time() - self.timer > self.time_out:
                self.pack_block()
                self.leader_prepare_phase()
                time.sleep(30)

    def reset_protocol(self):
        self.ballot = Type.Ballot(0, self.process_id, 0)

        self.acceptNum = Type.Ballot(0, 0, 0)
        self.acceptVal = None

        self.first_count = 0
        self.second_count = 0

        self.success = False


