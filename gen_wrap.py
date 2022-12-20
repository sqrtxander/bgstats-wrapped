import os
import json
import requests

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import textwrap

import argparse

from get_data import *


def truncate_name(name, max_length=15):
    if len(name) > max_length:
        return f'{name[:max_length]}...'
    return name


def generate_image1(games, players, mechanics, year, output_path):
    background_colour = (20, 20, 20)
    text_colour = (255, 255, 255)

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

    gameimage = gameimage.resize((544, 544))

    wrapped = Image.new('RGB', (1080, 1920), background_colour)
    wrapped.paste(backdropimage, (100, 80), backdropimage)
    wrapped.paste(gameimage, (268, 264))

    font = ImageFont.truetype('fonts/Courier Prime Bold.ttf', 36)
    font_heading = ImageFont.truetype('fonts/Courier Prime.ttf', 36)
    font_big = ImageFont.truetype('fonts/Courier Prime Bold.ttf', 68)
    font_year = ImageFont.truetype('fonts/Courier Prime Bold.ttf', 112)
    draw = ImageDraw.Draw(wrapped)

    draw.text(
        (20, 20), f'/{"ALL TIME" if year is None else year}',
        text_colour, font_year)

    draw.text((100, 1000), "Top Players", text_colour, font_heading)

    for i, player in list(enumerate(players_plays))[:min(5, len(players_plays))]:
        draw.text((100,  1080+i * 45),
                  f'{i+1} {truncate_name(player.name)}', text_colour, font)

    draw.text((560, 1000), "Top Games", text_colour, font_heading)
    for i, game in list(enumerate(games_plays))[:min(5, len(games_plays))]:
        draw.text((560, 1080+i*45),
                  f'{i+1} {truncate_name(game.name)}', text_colour, font)

    draw.text((100, 1440), "Total Plays", text_colour, font_heading)
    draw.text((100, 1520), f'{total_plays}', text_colour, font_big)

    if mechanics_plays:
        draw.text((560, 1440), "Top Mechanic", text_colour, font_heading)
        draw.text((560, 1520), mechanics_plays[0].replace(
            " ", "\n"), text_colour, font_big)

    wrapped.save(output_path)


def generate_image2(games, year):
    background_colour = (246, 116, 1896)
    text_colour = (0, 0, 0)

    games_plays = [game for game in games.values() if game.plays[year]]
    games_plays.sort(key=lambda game: game.plays[year], reverse=True)

    font_small = ImageFont.truetype('fonts/Courier Prime.ttf', 24)
    font = ImageFont.truetype('fonts/Courier Prime Bold.ttf', 36)
    font_heading = ImageFont.truetype('fonts/Courier Prime.ttf', 36)
    font_big = ImageFont.truetype('fonts/Courier Prime Bold.ttf', 68)
    font_year = ImageFont.truetype('fonts/Courier Prime Bold.ttf', 112)

    wrapped = Image.new('RGB', (1080, 1920), background_colour)
    draw = ImageDraw.Draw(wrapped)
    
    draw.text(
        (20, 20), f'/{"ALL TIME" if year is None else year}',
        text_colour, font_year)

    draw.text((130, 210), 'My Top Games', text_colour, font_big)

    for i, game in list(enumerate(games_plays))[:min(5, len(games_plays))]:
        draw.text((130, 385 + 105 + 234 * i), f'{i + 1}', text_colour, font_big, anchor='lm')
        
        print(game)
        response = requests.get(game.image)
        gameimage = Image.open(BytesIO(response.content)).resize((210, 210))
        time.sleep(0.5)
        wrapped.paste(gameimage, (226, 384 + 234 * i))

        draw.text((478, 472 + 234 * i), textwrap.fill(game.name, 20), text_colour, font, anchor='ld')

        draw.text((478, 494 + 234 * i), '\n'.join(game.mechanics[:min(3, len(game.mechanics))]), text_colour, font_small)
    
    wrapped.save('temp.png')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--new', action='store_true')
    parser.add_argument('-y', '--year', type=int)
    parser.add_argument('-p', '--path', type=str)
    parser.add_argument('-o', '--output', type=str)
    args = parser.parse_args()

    pickles_path = os.path.join(os.path.dirname(__file__), 'pickles/')
    if args.new and os.path.exists(pickles_path):
        for filename in os.listdir(pickles_path):
            if os.path.isfile(path := os.path.join(pickles_path, filename)):
                os.remove(path)

    if not args.path:
        args.path = os.path.join(os.path.dirname(
            __file__), 'BGStatsExport.json')
    if not args.output:
        if args.year:
            args.output = f'wrapped{args.year}.png'

        else:
            args.output = 'wrappedAllTime.png'

    with open(args.path, 'r', encoding='UTF-8') as f:
        data = json.load(f)

    if not os.path.exists(pickles_path):
        os.mkdir(pickles_path)

    games = load_games(data)
    players = load_players(data)
    mechanics = get_mechanics(games, data)

    generate_image1(games, players, mechanics, args.year, args.output)
    generate_image2(games, args.year)

if __name__ == '__main__':
    main()
