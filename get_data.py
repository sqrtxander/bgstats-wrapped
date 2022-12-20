import pickle
import collections
import requests
import xmltodict
import time
from datetime import datetime
import os


class Game:
    def __init__(self, bgg_id, name):
        self.bgg_id = bgg_id
        self.name = name
        self.plays = collections.defaultdict(int)

        if bgg_id == 0:
            self.image = 'images/none_game.png'
            self.mechanics = []
            return

        r = requests.get(
            f'https://boardgamegeek.com/xmlapi2/thing?id={bgg_id}')
        game_dict = xmltodict.parse(r.text)['items']['item']
        self.image = game_dict['image']
        self.mechanics = [link['@value'] for link in game_dict['link']
                          if link['@type'] == 'boardgamemechanic']


class Player:
    def __init__(self, id_, name):
        self.id = id_
        self.name = name
        self.plays = collections.defaultdict(int)
        self.stat_plays = collections.defaultdict(int)
        self.wins = collections.defaultdict(int)
        self.stat_wins = collections.defaultdict(int)
        self.start = collections.defaultdict(int)


def load_games(data):
    if os.path.exists('pickles/games.pickle'):
        with open('pickles/games.pickle', 'rb') as f:
            return pickle.load(f)
    count = len(data['games'])
    games = {}
    for i, game in enumerate(data['games'], start=1):
        games[game['id']] = Game(game['bggId'], game['name'])
        print(f'Loaded {game["name"]} {i}/{count}')

        time.sleep(2)

    for play in data['plays']:
        year = datetime.strptime(play['playDate'], '%Y-%m-%d %H:%M:%S').year
        games[play['gameRefId']].plays[year] += 1
        games[play['gameRefId']].plays[None] += 1

    with open('pickles/games.pickle', 'wb') as f:
        pickle.dump(games, f)

    return games


def load_players(data):
    if os.path.exists('pickles/players.pickle'):
        with open('pickles/players.pickle', 'rb') as f:
            return pickle.load(f)
    count = len(data['players'])
    players = {}
    for i, player in enumerate(data['players'], start=1):
        players[player['id']] = Player(player['id'], player['name'])
        print(f'Loaded {player["name"]} {i}/{count}')

    for play in data['plays']:
        for player in play['playerScores']:
            year = datetime.strptime(
                play['playDate'], '%Y-%m-%d %H:%M:%S').year

            players[player['playerRefId']].plays[year] += 1
            players[player['playerRefId']].plays[None] += 1

            if not play['ignored']:
                players[player['playerRefId']].stat_plays[year] += 1
                players[player['playerRefId']].stat_plays[None] += 1

            if player['winner']:
                players[player['playerRefId']].wins[year] += 1
                players[player['playerRefId']].wins[None] += 1

                if not play['ignored']:
                    players[player['playerRefId']].stat_wins[year] += 1
                    players[player['playerRefId']].stat_wins[None] += 1

            if player['startPlayer']:
                players[player['playerRefId']].start[year] += 1
                players[player['playerRefId']].start[None] += 1

    with open('pickles/players.pickle', 'wb') as f:
        pickle.dump(players, f)

    return players


def get_mechanics(games, data):
    mechanics = collections.defaultdict(lambda: collections.defaultdict(int))
    for play in data['plays']:
        game = games[play['gameRefId']]
        year = datetime.strptime(play['playDate'], '%Y-%m-%d %H:%M:%S').year
        for mechanic in game.mechanics:
            mechanics[year][mechanic] += 1
            mechanics[None][mechanic] += 1
    return mechanics