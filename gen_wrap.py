from __future__ import annotations

import os
import json

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import textwrap

import argparse

from collections import defaultdict

import matplotlib.pyplot as plt
import numpy

from get_data import *


def get_text_height(text: str, font: ImageFont.truetype) -> int:
    ascent, descent = font.getmetrics()
    lines = text.count('\n') + 1

    return ascent * lines


def title_image(year: int | None, output_path: str) -> None:
    img = Image.open('images/title.png')
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype('fonts/Louis George Cafe Light.ttf', 108)
    text_colour = (0, 0, 0)

    text = f'/{"All Time" if year is None else year}'

    draw.text((20, 20), text, text_colour, font)

    img.save(os.path.join(output_path, '00title.png'))


def plays_image(
    games: dict[int | None, Game],
    year: int | None,
    output_path: str
) -> None:
    games_plays = [game for game in games.values() if game.plays[year]]
    total_plays = f'{sum(game.plays[year] for game in games_plays)}'
    unique_games = f'{len(games_plays)}'

    text_colour = (0, 0, 0)
    font = ImageFont.truetype('fonts/verdanab.ttf', 72)

    img = Image.open('images/plays.png')
    draw = ImageDraw.Draw(img)

    draw.text((1584, 877), total_plays, text_colour, font, anchor='mm')
    draw.text((1584, 1557), unique_games, text_colour, font, anchor='mm')

    img.save(os.path.join(output_path, '01plays.png'))


def games_image(
    games: dict[int | None, Game],
    year: int | None,
    output_path: str
) -> None:
    top_games = [game for game in games.values() if game.plays[year]]
    top_games.sort(key=lambda game: game.plays[year], reverse=True)
    top_games = top_games[:min(5, len(top_games))]

    text_colour = (251, 194, 0)
    outline_colour_0 = (255, 255, 255)
    outline_colour_1 = (0, 0, 0)
    font = ImageFont.truetype('fonts/SATANICK.TTF', 84)
    img = Image.open('images/games.png')

    img_outline_0 = Image.new('RGBA', img.size)
    draw_outline_0 = ImageDraw.Draw(img_outline_0)

    img_outline_1 = Image.new('RGBA', img.size)
    draw_outline_1 = ImageDraw.Draw(img_outline_1)

    img_text = Image.new('RGBA', img.size)
    draw_text = ImageDraw.Draw(img_text)

    positions = [(356, 482), (1212, 732), (356, 982),
                 (1212, 1233), (356, 1483)]
    max_lens = [14, 14, 14, 14, 14]
    anchors = ['lt', 'rt', 'lt', 'rt', 'lt']
    scale = (img.width - 30) / top_games[0].plays[year]

    for game, pos, max_len, anchor in zip(top_games, positions, max_lens, anchors):
        text = textwrap.fill(game.name, max_len)
        lines = text.splitlines()
        height = get_text_height(text, font)
        pos = (pos[0], pos[1] - height)

        for line in lines:
            # outline 0
            draw_outline_0.text(pos, line, outline_colour_0, font,
                                anchor=anchor, stroke_width=10)

            # outline 1
            draw_outline_1.text(pos, line, outline_colour_1, font,
                                anchor=anchor, stroke_width=5)

            # regular text
            draw_text.text(pos, line, text_colour, font, anchor=anchor)

            # update pos for next line
            height = get_text_height(line, font)
            pos = (pos[0], pos[1] + height)

        # add bar chart
        draw_outline_0.rectangle(
            (15, pos[1]+10, 15 + game.plays[year] * scale, pos[1] + 50), outline_colour_0)
        draw_outline_1.rectangle(
            (20, pos[1]+15, 10 + game.plays[year] * scale, pos[1] + 45), outline_colour_1)
        draw_text.rectangle(
            (25, pos[1]+20, 5 + game.plays[year] * scale, pos[1] + 40), text_colour)

    # add outline and text
    img.paste(img_outline_0, img_outline_0)
    img.paste(img_outline_1, img_outline_1)
    img.paste(img_text, img_text)

    img.save(os.path.join(output_path, '02games.png'))


def players_image(
    players: dict[int | None, Player],
    year: int | None,
    output_path: str
) -> None:
    top_players = [player for player in players.values()
                   if player.plays[year]]
    top_players.sort(key=lambda player: player.plays[year], reverse=True)
    top_players = top_players[:min(5, len(top_players))]

    text_colour = (0, 0, 0)
    font = ImageFont.truetype('fonts/IBMPlexSans-Thin.ttf', 64)

    img = Image.open('images/players.png')

    img_text = Image.new('RGBA', img.size)
    draw_text = ImageDraw.Draw(img_text)

    positions = [(220, 360), (220, 480), (220, 600),
                 (220, 720), (220, 840)]
    max_lens = [15, 15, 15, 15, 15]
    scale = (img.width - 440) / top_players[0].plays[year]

    for player, pos, max_len in zip(top_players, positions, max_lens):
        text = textwrap.fill(player.name.upper(), max_len)
        height = get_text_height(text, font)
        pos = (pos[0], pos[1] - height)

        for line in text.splitlines():
            # regular text
            draw_text.text(pos, line, text_colour, font, anchor='lt')

            # update pos for next line
            height = get_text_height(line, font)
            pos = (pos[0], pos[1] + height)

        # add bars
        draw_text.rectangle(
            (220, pos[1] - 5, 220 + player.plays[year] * scale, pos[1] + 15), text_colour)
        draw_text.rectangle(
            (222, pos[1] - 3, 218 + player.plays[year] * scale, pos[1] + 13), (0, 0, 0, 0))

    # add text
    img.paste(img_text, img_text)

    img.save(os.path.join(output_path, '03players.png'))


def mechanics_image(
    mechanics: defaultdict[int | None, defaultdict[str, int]],
    year: int | None,
    output_path: str
) -> None:
    top_mechanics = list(mechanics[year])
    top_mechanics.sort(
        key=lambda mechanic: mechanics[year][mechanic], reverse=True)
    top_mechanics = top_mechanics[:min(5, len(top_mechanics))]
    text_colour = (237, 227, 217)
    shadow_colour = (0, 0, 0)
    font = ImageFont.truetype('fonts/plump.ttf', 96)

    img = Image.open('images/mechanics.png')

    img_shadow = Image.new('RGBA', img.size)
    draw_shadow = ImageDraw.Draw(img_shadow)

    img_text = Image.new('RGBA', img.size)
    draw_text = ImageDraw.Draw(img_text)

    positions = [(656, 174), (500, 491), (656, 803), (347, 1118), (656, 1428)]
    bar_y_positions = [193, 339-30, 640, 1137, 1278-30]
    max_lens = [14, 16, 14, 19, 14]
    scale = (img.width - 72) / mechanics[year][top_mechanics[0]]

    for mechanic, pos, bary, max_len in zip(top_mechanics, positions, bar_y_positions, max_lens):
        text = textwrap.fill(mechanic, max_len)
        lines = text.splitlines()
        height = get_text_height(text, font)
        pos = (pos[0], pos[1] - height)

        for line in lines:
            # img_shadow backdrop
            draw_shadow.text(pos, line, shadow_colour, font, stroke_width=5)

            # regular text
            draw_text.text(pos, line, text_colour, font)

            # update pos for next line
            height = get_text_height(line, font)
            pos = (pos[0], pos[1] + height)

        # add bars
        draw_shadow.rectangle(
            (31, bary, 21 + mechanics[year][mechanic] * scale, bary + 30), shadow_colour)
        draw_text.rectangle(
            (36, bary + 5, 16 + mechanics[year][mechanic] * scale, bary + 25), text_colour)

    # blur outlined text
    img_shadow = img_shadow.filter(ImageFilter.BoxBlur(5))

    # add shadow and text
    img.paste(img_shadow, img_shadow)
    img.paste(img_text, img_text)

    img.save(os.path.join(output_path, '04mechanics.png'))


def main() -> None:
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
            args.output = os.path.join(
                os.path.dirname(__file__), f'wrapped{args.year}')

        else:
            args.output = os.path.join(
                os.path.dirname(__file__), 'wrappedAllTime')

    if not os.path.exists(pickles_path):
        os.mkdir(pickles_path)

    if not os.path.exists(args.output):
        os.mkdir(args.output)

    with open(args.path, 'r', encoding='UTF-8') as f:
        data = json.load(f)

    games = load_games(data)
    players = load_players(data)
    mechanics = get_mechanics(games, data)

    title_image(args.year, args.output)
    plays_image(games, args.year, args.output)
    games_image(games, args.year, args.output)
    players_image(players, args.year, args.output)
    mechanics_image(mechanics, args.year, args.output)


if __name__ == '__main__':
    main()
