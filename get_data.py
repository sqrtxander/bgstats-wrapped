from __future__ import annotations
import pickle
from collections import defaultdict
import requests
import xmltodict
import time
from datetime import datetime
import os


class Game:
    def __init__(self, bgg_id: int, name: str) -> None:
        self.bgg_id = bgg_id
        self.name = name
        self.plays = defaultdict(int)

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
    def __init__(self, id_: int, name: str) -> None:
        self.id = id_
        self.name = name
        self.plays = defaultdict(int)
        self.stat_plays = defaultdict(int)
        self.wins = defaultdict(int)
        self.stat_wins = defaultdict(int)
        self.start = defaultdict(int)


def load_games(data) -> dict[int | None, Game]:
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


def load_players(data) -> dict[int | None, Player]:
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

            players[player['playerRefId']
                    ].stat_plays[year] += not play['ignored']
            players[player['playerRefId']
                    ].stat_plays[None] += not play['ignored']

            players[player['playerRefId']].wins[year] += player['winner']
            players[player['playerRefId']].wins[None] += player['winner']

            players[player['playerRefId']
                    ].stat_wins[year] += player['winner'] and not play['ignored']
            players[player['playerRefId']
                    ].stat_wins[None] += player['winner'] and not play['ignored']

            players[player['playerRefId']].start[year] += player['startPlayer']
            players[player['playerRefId']].start[None] += player['startPlayer']

    with open('pickles/players.pickle', 'wb') as f:
        pickle.dump(players, f)

    return players


def get_mechanics(games: dict[int | None, Game], data) -> defaultdict[int | None, defaultdict[str, int]]:
    mechanics = defaultdict(lambda: defaultdict(int))
    for play in data['plays']:
        game = games[play['gameRefId']]
        year = datetime.strptime(play['playDate'], '%Y-%m-%d %H:%M:%S').year
        for mechanic in game.mechanics:
            mechanics[year][mechanic] += 1
            mechanics[None][mechanic] += 1
    return mechanics
