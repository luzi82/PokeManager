#!/usr/bin/python

# luzi@gmail.com
# used for list pokemon only
# based on demo.py
# remove all user interaction

import argparse
import logging
import time
import sys
import operator
import random
import getpass
import os.path

import POGOProtos.Enums.PokemonMove_pb2 as PokemonMove_pb2

from collections import Counter
from custom_exceptions import GeneralPogoException
from api import PokeAuthSession
from location import Location
from pokedex import pokedex
from inventory import items

def setupLogger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

def viewPokemon(session,aSort):
    party = session.checkInventory().party
    myParty = []
    
    # Get the party and put it into a nicer list
    for pokemon in party:
        IvPercent = ((pokemon.individual_attack + pokemon.individual_defense + pokemon.individual_stamina)*100)/45
        # Get the names of the moves and remove the _FAST part of move 1
        move_1 = PokemonMove_pb2.PokemonMove.Name(pokemon.move_1)
        move_1 = move_1[:-5]
        move_2 = PokemonMove_pb2.PokemonMove.Name(pokemon.move_2)
        L = [
            pokedex[pokemon.pokemon_id],
            pokemon.cp,
            pokemon.individual_attack,
            pokemon.individual_defense,
            pokemon.individual_stamina,

            IvPercent,
            pokemon,
            move_1,
            move_2,
            pokemon.creation_time_ms,

            pokemon.favorite,
            pokemon.pokemon_id,
            -pokemon.cp
        ]
        myParty.append(L)
    
    if aSort == 'recent':
        myParty.sort(key = operator.itemgetter(9))
        myParty = reversed(myParty)
    elif aSort == 'iv':
        myParty.sort(key = operator.itemgetter(5))
        myParty = reversed(myParty)
    elif aSort == 'number':
        myParty.sort(key = operator.itemgetter(11,12))
    
    i = 0
    # Display the pokemon, with color coding for IVs and separation between types of pokemon
    print ' NAME            | G F | CP    | ATK | DEF | STA | IV% | MOVE 1          | MOVE 2'
    print '---------------- | --- | ----- | --- | --- | --- | --- | --------------- | --------------- '
    for monster in myParty:
        if i == 3:
            print ''
            i = 0
        logging.info(
            ' %-15s | %-1s %-1s | %-5s | %-3s | %-3s | %-3s | %-3s | %-15s | %-15s | %-15s',
            monster[0],
            ('G' if monster[5]>90 else ' '),
            ('F' if monster[10] else ' '),
            monster[1],
            monster[2],monster[3],monster[4],monster[5],monster[7],monster[8],monster[9])
        i = i+1

# Entry point
# Start off authentication and demo
if __name__ == '__main__':
    setupLogger()
    logging.debug('Logger set up')

    # Read in args
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--auth", help="Auth Service", required=True)
    parser.add_argument("-u", "--username", help="Username", required=True)
    parser.add_argument("-p", "--password", help="Password", required=False)
    parser.add_argument("-l", "--location", help="Location", required=False)
    parser.add_argument("-g", "--geo_key", help="GEO API Secret")
    parser.add_argument("-s", "--sort", help="Sort order", required=False)
    args = parser.parse_args()

    # Check service
    if args.auth not in ['ptc', 'google']:
        logging.error('Invalid auth service {}'.format(args.auth))
        sys.exit(-1)
        
        
    if args.sort == '':
        args.sort = 'recent'
    if args.sort not in ['recent','iv','number']:
        logging.error('Invalid sort {}'.format(args.sort))
        sys.exit(-1)

    # Check password
    if args.password == None:
        args.password = getpass.getpass()

    # Create PokoAuthObject
    poko_session = PokeAuthSession(
        args.username,
        args.password,
        args.auth,
        geo_key=args.geo_key
    )

    # Authenticate with a given location
    # Location is not inherent in authentication
    # But is important to session
    if args.location != '':
        session = poko_session.authenticate(args.location)
    else:
        session = poko_session.authenticate()

    # Time to show off what we can do
    if session:
        viewPokemon(session,args.sort)
    else:
        logging.critical('Session not created successfully')
        sys.exit(-1)
