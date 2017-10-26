import socket
from random import SystemRandom
from threading import Thread
from src.python.Card import Cards


class Player:
    def __init__(self, client_name, client, address):
        self.name = client_name
        self.client = client
        self.address = address

    def send(self, data):
        self.client.send(data.encode())

    def receive(self, size):
        return self.client.recv(size).decode()


class ReceiveThread(Thread):
    def __init__(self, client, number_of_receive):
        Thread.__init__(self)
        self.client = client
        self.number_of_receive = number_of_receive
        self.inputs = []
        self.set_return_complete = False

    def run(self):
        self.set_return()

    def set_return(self):
        for i in range(self.number_of_receive):
            s = self.client.recv(1024).decode()
            print(s)
            self.inputs.append(s)
        self.set_return_complete = True

    def get_return(self):
        while True:
            if self.set_return_complete:
                print("In if")
                return self.inputs


# def transfer_data(client):
#     while True:
#         data = client.recv(1024).decode()
#
#         if not data:
#             break
#
#         print("Receive :" + data)
#
#         data = data.upper()
#
#         client.send(data.encode())
#         print("Send :" + data)
#     client.close()
#     print("Client is disconnect")

def play_game():
    # deal 13 cards to each player
    def deal_cards():
        def make_cards():
            for rank in "23456789TJQKA":
                for suit in "CDHS":
                    cards.append(rank + suit)

        # random card and send to each player 13 cards (13 Send)
        def deal():
            global beginner
            for i in range(13):
                for j in range(4):
                    card = SystemRandom().choice(cards)
                    print("Send : " + card + " To : " + str(j))
                    if card == "2C":  # in game rule, player who have "2C" card is the game beginner
                        beginner = j

                    players[j].send(card)
                    cards.remove(card)

        cards = []
        make_cards()
        deal()

    # in game rule if round%4 != 0 , all player must exchange cards
    def exchange_cards():
        # send to all player that this game have exchange state
        def send_exchange_status():  # (1 Send)
            for player in players:
                player.send("Exchange")

        def give_exchange_cards():  # (3 Receive)
            threads = []
            for player in players:
                thread = ReceiveThread(player.client, 3)
                threads.append(thread)
                thread.start()

            for thread in threads:
                cards_after_exchange.append(thread.get_return())

            print(cards_after_exchange)

        # 3 if in this function is just make from rule of game
        def send_exchange_cards():  # (3 Send)
            global beginner
            if game_round % 4 == 1:
                for i in range(len(players)):
                    for j in range(len(cards_after_exchange[0])):
                        players[i].send(cards_after_exchange[i - 1][j])

                        # in game rule, player who have "2C" card is the game beginner
                        if "2C" == cards_after_exchange[i - 1][j]:
                            beginner = i

            elif game_round % 4 == 2:
                for i in range(len(players)):
                    for j in range(len(cards_after_exchange[0])):
                        players[i].send(cards_after_exchange[(i + 1) % 4][j])

                        # in game rule, player who have "2C" card is the game beginner
                        if "2C" == cards_after_exchange[(i + 1) % 4][j]:
                            beginner = i

            elif game_round % 4 == 3:
                for i in range(len(players)):
                    for j in range(len(cards_after_exchange[0])):
                        players[i].send(cards_after_exchange[(i + 2) % 4][j])

                        # in game rule, player who have "2C" card is the game beginner
                        if "2C" == cards_after_exchange[(i + 2) % 4][j]:
                            beginner = i

        if game_round % 4 != 0:
            cards_after_exchange = []
            send_exchange_status()
            give_exchange_cards()
            send_exchange_cards()

    def play():
        # set first card (use in game rule)
        def set_first_card(four_cards):
            if i+1 == 1 and j+1 == 1:
                return "2C"
            else:
                if j == 1:
                    return ""
                return four_cards[1]

        # check who give highest rank
        def check_who_give():
            max_rank = 0
            recipient = 0
            for i in range(len(four_cards)):
                if four_cards[i][1] == first_card[1]:        # check suit of card
                    if all_cards.get_rank(four_cards[i]) > max_rank:
                        max_rank = all_cards.get_rank(four_cards[i])
                        recipient = i
            return recipient

        # send four cards to player who give highest rank
        def send_four_cards():
            for i in players:
                for j in range(len(four_cards)):
                    if i == recipient:
                        players[i].send(four_cards[j])
                    else:
                        players[i].send("")

        global beginner
        play_round = 1      # play_round is sub round of game_round
        can_play_heart = "NO"
        for i in range(13):  # each player have 13 cards then play 13 round
            four_cards = []

            for j in range(len(players)):
                first_card = set_first_card(four_cards)

                players[(beginner + j) % 4].send("Your Turn")

                players[(beginner + j) % 4].send(first_card)
                players[(beginner + j) % 4].send(can_play_heart)

                four_cards.append(players[(beginner + j) % 4].receive(2))  # parameter 2 is mean 1card = 2character

            recipient = check_who_give()
            send_four_cards()
            beginner = recipient

            for card in four_cards:
                if card[1] == "H":
                    can_play_heart = "YES"

            play_round += 1

    while True:
        beginner = 0
        deal_cards()  # 13 send
        exchange_cards()  # 1 send

        play()  # until score more than or equal 100

        # if score >= 100:
        #     break


def start_server():
    # wait 4 client(Player) connect and receive name from client
    def connect_client():
        for i in range(player_number):
            client, address = server_socket.accept()
            client_name = client.recv(1024).decode()  # wait to receive name from client

            players.append(Player(client_name, client, address))
            print("Client: " + players[i].name + " Connect")

    # send to all client that all client are connection
    def send_ready():
        for player in players:
            player.send("Ready")

    port = 5098
    player_number = 4

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((socket.gethostname(), port))

    print("Server is wait for client's connect")
    server_socket.listen(player_number)  # can connect 4 client

    connect_client()  # wait to connect 4 clients (1 Receive)
    send_ready()  # send ready to client (1 Send)


if __name__ == "__main__":
    players = []
    all_cards = Cards()
    start_server()

    game_round = 1
    while True:
        play_game()  # start game
        game_round += 1
