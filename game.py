import random

def assign_roles(clients):
    artist = clients[random.randint(0,len(clients)-1)]
    print("artist is: ",artist.username)
    guessers = clients
    guessers.remove(artist)
    print("guessers:")
    for i in guessers:
        print(i.username)
    return artist, guessers

def give_score(clients):
    for i in clients:
        if i.artist == True:
            artist = i
    for i in clients:
        if i.guessed == True:
            i.points += 100
            artist.points += 50
    return clients
