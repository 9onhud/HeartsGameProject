import socket


def give_cards():
    cards = []
    for i in range(13):
        card = client_socket.recv(2).decode()  # (13 Receive)
        print("Give a " + card + " card.")
        cards.append(card)
    return cards


def exchange_cards():
    cards_exchange = []
    # give 3 cards from MainGame to assign var cards_exchange

    # Just for Test
    for i in range(3):
        # cards_exchange.append(input("Card Exchange: "))
        client_socket.send(input("Card Exchange: ").encode())

    # for card_exchange in cards_exchange:  # (3 send)
    #     client_socket.send(card_exchange.encode())
    cards_from_other = []
    for i in range(3):
        cards_from_other.append(
            client_socket.recv(2).decode())  # parameter 2 is mean maximum string size in byte (1str = 1byte)
    print(cards_from_other)


def check_can_put(first_card, can_play_heart, cards, card_put):
    def check_free_play_card():
        for card in cards:
            if card_put[1] == card[1]:
                return False
        return True

    def check_can_open_heart():
        for card in cards:
            if card[1] != "H":
                return False
        return True

    if first_card == "2C":
        if card_put == "QS":
            return False
        if card_put[1] == "H":
            return False
        if card_put[1] == "C":
            return True
        return False
    elif first_card == "":
        if can_play_heart == "YES":
            return True
        else:
            if check_can_open_heart():
                return True
            else:
                if card_put[1] != "H":
                    return True
                return False
    else:
        if first_card[1] == card_put[1]:
            return True
        else:
            if check_free_play_card():
                return True
            return False


def start_client():
    def give_status():
        return client_socket.recv(1024).decode()

    try:
        client_socket.connect((socket.gethostname(), port))

        # send name to server
        name = input("My name: ")
        client_socket.send(name.encode())  # (1 Send)

        cards_give = []
        while True:
            status = give_status()      # (... Receive)
            if status == "Ready":
                cards = give_cards()  # (13 Receive)
                print("All cards you have :", cards)
                # send cards to MainGame to set GameGUI
            elif status == "Exchange":
                exchange_cards()  # (3 Send)
            elif status == "Your Turn":
                print("My Turn.")
                first_card = client_socket.recv(1024).decode()  # (1 Receive)
                can_play_heart = client_socket.recv(1024).decode()  # (1 Receive)

                while True:
                    card_put = input("Choose Card : ")
                    if check_can_put(first_card, can_play_heart, cards, card_put):
                        client_socket.send(card_put.encode())       # (1 Send)
                        break

                for i in range(4):
                    cards_give.append(client_socket.recv(2).decode())
                print("I have : ", cards_give)

    except Exception as e:
        print("You aren't connect.")
        print(e)
    finally:
        client_socket.close()
        print("Client is disconnect")


if __name__ == "__main__":
    port = 5098
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    start_client()
