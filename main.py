import os
import sys

import json
import requests
import xmltodict
import pickle

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

import collections

import time

class Game:
    def __init__(self, bgg_id):
        self.bgg_id = bgg_id
        r = requests.get(
            f'https://boardgamegeek.com/xmlapi2/thing?id={bgg_id}')
        game_dict = xmltodict.parse(r.text)['items']['item']
        self.image = game_dict['image']
        self.mechanics = [link['@value'] for link in game_dict['link']
                          if link['@type'] == 'boardgamemechanic']

        try:
            self.name = game_dict['name'][0]['@value']
        except KeyError:
            self.name = game_dict['name']['@value']

        self.plays = 0


class Player:
    def __init__(self, id_, name):
        self.id = id_
        self.name = name
        self.plays = 0


def load_games():
    if os.path.exists('pickles/games.pickle'):
        with open('pickles/games.pickle', 'rb') as f:
            return pickle.load(f)
    games = {}
    for game in DATA['games']:
        games[game['id']] = Game(game['bggId'])
        print(f'Loaded {game["bggName"]}')

        time.sleep(1.5)

    for play in DATA['plays']:
        games[play['gameRefId']].plays += 1

    with open('pickles/games.pickle', 'wb') as f:
        pickle.dump(games, f)

    return games


def load_players():
    if os.path.exists('pickles/players.pickle'):
        with open('pickles/players.pickle', 'rb') as f:
            return pickle.load(f)
    players = {}
    for player in DATA['players']:
        players[player['id']] = Player(player['id'], player['name'])
        print(f'Loaded {player["name"]}')

    for play in DATA['plays']:
        for player in play['playerScores']:
            players[player['playerRefId']].plays += 1

    with open('pickles/players.pickle', 'wb') as f:
        pickle.dump(players, f)

    return players


def get_mechanics(games):
    mechanics = collections.defaultdict(int)
    for play in DATA['plays']:
        game = games[play['gameRefId']]
        for mechanic in game.mechanics:
            mechanics[mechanic] += 1
    return mechanics


def truncate_name(name, max_length=15):
    if len(name) > max_length:
        return f'{name[:max_length]}...'
    return name


def generate_image(games, players, mechanics):
    games_plays = list(games.values())
    games_plays.sort(key=lambda game: game.plays, reverse=True)

    players_plays = list(players.values())
    players_plays.sort(key=lambda player: player.plays, reverse=True)

    mechanics_plays = list(mechanics.keys())
    mechanics_plays.sort(
        key=lambda mechanic: mechanics[mechanic], reverse=True)

    total_plays = sum(game.plays for game in games.values())

    gameimage_url = games_plays[0].image
    response = requests.get(gameimage_url)

    backdropimage = Image.open('images/backdrop.png')

    gameimage = Image.open(BytesIO(response.content))
    gameimage.save('images/gameimage.png')
    gameimage = gameimage.resize((544, 544))

    img = Image.new('RGB', (1080, 1920), color=BACKGROUND_COLOUR)
    img.paste(backdropimage, (100, 80), backdropimage)
    img.paste(gameimage, (268, 264))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('fonts/Courier Prime Bold.ttf', 36)
    font_heading = ImageFont.truetype('fonts/Courier Prime.ttf', 36)
    font_big = ImageFont.truetype('fonts/Courier Prime Bold.ttf', 68)
    font_mechanic = ImageFont.truetype('fonts/Courier Prime Bold.ttf', 42)
    draw.text((100, 1000), "Top Players", TEXT_COLOUR, font=font_heading)
    for i, player in list(enumerate(players_plays))[:5]:
        draw.text((100,  1080+i * 45),
                  f'{i+1} {truncate_name(player.name)}', TEXT_COLOUR, font=font)

    draw.text((560, 1000), "Top Games", TEXT_COLOUR, font=font_heading)
    for i, game in list(enumerate(games_plays))[:5]:
        draw.text((560, 1080+i*45),
                  f'{i+1} {truncate_name(game.name)}', TEXT_COLOUR, font=font)

    draw.text((100, 1440), "Total Plays", TEXT_COLOUR, font=font_heading)
    draw.text((100, 1520), f'{total_plays}', TEXT_COLOUR, font=font_big)

    draw.text((560, 1440), "Top Mechanic", TEXT_COLOUR, font=font_heading)
    draw.text((560, 1520), mechanics_plays[0].replace(
        " ", "\n"), TEXT_COLOUR, font=font_big)

    img.save('wrapped.png')

def main():
    games = load_games()
    players = load_players()
    mechanics = get_mechanics(games)
    generate_image(games, players, mechanics)

TEXT_COLOUR = (255, 255, 255)
BACKGROUND_COLOUR = (20, 20, 20)

try:
    path = sys.argv[1]
except IndexError:
    path = os.path.join(os.path.dirname(__file__), 'BGStatsExport2022-12-11.json')
with open(path, 'r', encoding='UTF-8') as f:
    DATA = json.load(f)

if __name__ == '__main__':
    main()
