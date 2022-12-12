import os

import json
import requests
import xmltodict
import pickle

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

import collections

import time
from datetime import datetime

import argparse


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

        self.plays = collections.defaultdict(int)


class Player:
    def __init__(self, id_, name):
        self.id = id_
        self.name = name
        self.plays = collections.defaultdict(int)


def load_games(data):
    if os.path.exists('pickles/games.pickle'):
        with open('pickles/games.pickle', 'rb') as f:
            return pickle.load(f)
    games = {}
    for game in data['games']:
        games[game['id']] = Game(game['bggId'])
        print(f'Loaded {game["bggName"]}')

        time.sleep(2)

    for play in data['plays']:
        year = datetime.strptime(play['playDate'], '%Y-%m-%d %H:%M:%S').year
        games[play['gameRefId']].plays[year] += 1

    with open('pickles/games.pickle', 'wb') as f:
        pickle.dump(games, f)

    return games


def load_players(data):
    if os.path.exists('pickles/players.pickle'):
        with open('pickles/players.pickle', 'rb') as f:
            return pickle.load(f)
    players = {}
    for player in data['players']:
        players[player['id']] = Player(player['id'], player['name'])
        print(f'Loaded {player["name"]}')

    for play in data['plays']:
        for player in play['playerScores']:
            year = datetime.strptime(
                play['playDate'], '%Y-%m-%d %H:%M:%S').year
            players[player['playerRefId']].plays[year] += 1

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
    return mechanics


def truncate_name(name, max_length=15):
    if len(name) > max_length:
        return f'{name[:max_length]}...'
    return name


def generate_image(games, players, mechanics, year, output_path):
    games_plays = [game for game in games.values() if game.plays[year]]
    games_plays.sort(key=lambda game: game.plays[year], reverse=True)

    players_plays = [player for player in players.values()
                     if player.plays[year]]
    players_plays.sort(key=lambda player: player.plays[year], reverse=True)

    mechanics_plays = list(mechanics[year])
    mechanics_plays.sort(
        key=lambda mechanic: mechanics[year][mechanic], reverse=True)

    total_plays = sum(game.plays[year] for game in games.values())

    backdropimage = Image.open('images/backdrop.png')

    gameimage = Image.open('images/none_game.png')
    if games_plays:
        gameimage_url = games_plays[0].image
        response = requests.get(gameimage_url)
        gameimage = Image.open(BytesIO(response.content))
        gameimage.save('images/gameimage.png')

    gameimage = gameimage.resize((544, 544))

    wrapped = Image.new('RGB', (1080, 1920), color=BACKGROUND_COLOUR)
    wrapped.paste(backdropimage, (100, 80), backdropimage)
    wrapped.paste(gameimage, (268, 264))

    font = ImageFont.truetype('fonts/Courier Prime Bold.ttf', 36)
    font_heading = ImageFont.truetype('fonts/Courier Prime.ttf', 36)
    font_big = ImageFont.truetype('fonts/Courier Prime Bold.ttf', 68)
    font_year = ImageFont.truetype('fonts/Courier Prime Bold.ttf', 112)
    draw = ImageDraw.Draw(wrapped)

    draw.text((20, 20), f'/{year}', TEXT_COLOUR, font=font_year)

    draw.text((100, 1000), "Top Players", TEXT_COLOUR, font=font_heading)

    for i, player in list(enumerate(players_plays))[:min(5, len(players_plays))]:
        draw.text((100,  1080+i * 45),
                  f'{i+1} {truncate_name(player.name)}', TEXT_COLOUR, font=font)

    draw.text((560, 1000), "Top Games", TEXT_COLOUR, font=font_heading)
    for i, game in list(enumerate(games_plays))[:min(5, len(games_plays))]:
        draw.text((560, 1080+i*45),
                  f'{i+1} {truncate_name(game.name)}', TEXT_COLOUR, font=font)

    draw.text((100, 1440), "Total Plays", TEXT_COLOUR, font=font_heading)
    draw.text((100, 1520), f'{total_plays}', TEXT_COLOUR, font=font_big)

    if mechanics_plays:
        draw.text((560, 1440), "Top Mechanic", TEXT_COLOUR, font=font_heading)
        draw.text((560, 1520), mechanics_plays[0].replace(
            " ", "\n"), TEXT_COLOUR, font=font_big)

    wrapped.save(output_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--new', action='store_true')
    parser.add_argument('-y', '--year', type=int)
    parser.add_argument('-p', '--path', type=str)
    parser.add_argument('-o', '--output', type=str)
    args = parser.parse_args()

    if args.new and os.path.exists('pickles/'):
        os.removedirs('pickles/')
    if not args.year:
        args.year = datetime.now().year
    if not args.path:
        args.path = os.path.join(os.path.dirname(
            __file__), 'BGStatsExport.json')
    if not args.output:
        args.output = f'wrapped{args.year}.png'

    with open(args.path, 'r', encoding='UTF-8') as f:
        data = json.load(f)

    games = load_games(data)
    players = load_players(data)
    mechanics = get_mechanics(games, data)

    generate_image(games, players, mechanics, args.year, args.output)


TEXT_COLOUR = (255, 255, 255)
BACKGROUND_COLOUR = (20, 20, 20)


if __name__ == '__main__':
    main()
