from Node import Node
import sys
from threading import Thread

if __name__ == '__main__':
    process_id = int(input("Enter Your Process ID: "))

    node = Node(process_id)
    Thread(target=node.start(), args=()).start()

    while True:
        line = sys.stdin.readline().rstrip("\n")
        command = line.split(" ")

        if command[0] == "transfer":
            node.moneyTransfer(int(command[1]), int(command[2]), int(command[3]))

        elif command[0] == "failLink":
            node.failLink(int(command[1]), int(command[2]))

        elif command[0] == "fixLink":
            node.fixLink(int(command[1]), int(command[2]))

        elif command[0] == "failProcess":
            node.failProcess()

        elif command[0] == "printBlockchain":
            node.printBlockchain()

        elif command[0] == "printBalance":
            node.printBalance()

        elif command[0] == "printQueue":
            node.printQueue()

        else:
            print("Error Command")
