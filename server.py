import socket
from _thread import *
import pickle
from game import game

server = "192.168.0.35" 
port = 7777

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection, Server Started")

connected = set() #stores the ip of connected players
games = {} #stores the game data
idCount = 0 #keep track of current ID to not override any over games.


def threaded_client(conn, p, gameId):
    global idCount
    conn.send(str.encode(str(p)))

    reply = ""
    while True:
        try:
            data = conn.recv(4096).decode()

            if gameId in games:
                game = games[gameId]

                if not data:
                    break
                else:
                    if data == "reset":
                        game.resetWent()
                    elif data != "get":
                        game.play(p, data)

                    conn.sendall(pickle.dumps(game))
            else:
                break
        except:
            break

    print("Lost connection")
    try:
        del games[gameId]
        print("Closing Game", gameId)
    except:
        pass
    idCount -= 1
    conn.close()



while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    idCount += 1 
    p = 0 #current player
    gameId = (idCount - 1)//2 # increment every game ID by 1 when every player joins.
    if idCount % 2 == 1:
        games[gameId] = Game(gameId) 
        print("Creating a new game...")
    else:
        games[gameId].ready = True #when 2nd player connects this will alot the program to start the game.
        p = 1


    start_new_thread(threaded_client, (conn, p, gameId))