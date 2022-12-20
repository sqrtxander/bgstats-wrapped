from __future__ import annotations

import os
import json

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import textwrap

import argparse

from collections import defaultdict


from get_data import *


def get_text_height(text: str, font: ImageFont.truetype) -> int:
    ascent, descent = font.getmetrics()
    lines = text.count('\n') + 1

    return ascent * lines


def mechanics_image(
        mechanics: defaultdict[int|None, defaultdict[str, int]],
        year: int|None,
        output_path: str
) -> None:
    mechanics_plays = list(mechanics[year])
    mechanics_plays.sort(
        key=lambda mechanic: mechanics[year][mechanic], reverse=True)

    text_colour = (237, 227, 217)
    blur_colour = (0, 0, 0)
    font = ImageFont.truetype('fonts\plump.ttf', 96)

    img = Image.open('images/mechanics.png')
    draw = ImageDraw.Draw(img)

    positions = [(656, 174), (500, 491), (656, 803), (347, 1118), (656, 1428)]
    max_lens = [14, 16, 14, 19, 14]
    for mechanic, pos, max_len in zip(mechanics_plays[:min(5, len(mechanics_plays))], positions, max_lens):
        text = textwrap.fill(mechanic, max_len)
        lines = text.splitlines()
        height = get_text_height(text, font)
        pos = (pos[0], pos[1] - height)
        pos_store = pos

        blurred = Image.new('RGBA', img.size)
        draw_b = ImageDraw.Draw(blurred)

        for line in lines:
            # blurred backdrop
            draw_b.text(pos, line, blur_colour, font, stroke_width=5)

            # update pos for next line
            height = get_text_height(line, font)
            pos = (pos[0], pos[1] + height)

        # blur outlined text
        blurred = blurred.filter(ImageFilter.BoxBlur(5))
        img.paste(blurred, blurred)

        pos = pos_store
        for line in lines:
            # regular text
            draw.text(pos, line, text_colour, font)

            # update pos for next line
            height = get_text_height(line, font)
            pos = (pos[0], pos[1] + height)

    img.save(os.path.join(output_path, 'mechanics.png'))


def games_image(
        games: dict[int|None, Game],
        year: int|None,
        output_path: str
) -> None:
    games_plays = [game for game in games.values() if game.plays[year]]
    games_plays.sort(key=lambda game: game.plays[year], reverse=True)

    text_colour = (251, 194, 0)
    outline_colour_0 = (0, 0, 0)
    outline_colour_1 = (255, 255, 255)
    font = ImageFont.truetype('fonts/SATANICK.TTF', 96)

    img = Image.open('images/games.png')
    draw = ImageDraw.Draw(img)

    positions = [(356, 500), (1212, 766), (356, 1040),
                 (1212, 1297), (356, 1545)]
    max_lens = [14, 14, 14, 14, 14]
    anchors = ['lt', 'rt', 'lt', 'rt', 'lt']
    for game, pos, max_len, anchor in zip(games_plays[:min(5, len(games_plays))], positions, max_lens, anchors):
        text = textwrap.fill(game.name, max_len)
        lines = text.splitlines()
        height = get_text_height(text, font)
        pos = (pos[0], pos[1] - height)
        pos_store = pos

        for line in lines:
            # outline
            draw.text(pos, line, outline_colour_1, font,
                      anchor=anchor, stroke_width=10)

            # update pos for next line
            height = get_text_height(line, font)
            pos = (pos[0], pos[1] + height)

        pos = pos_store
        for line in lines:
            draw.text(pos, line, outline_colour_0, font,
                      anchor=anchor, stroke_width=5)

            # update pos for next line
            height = get_text_height(line, font)
            pos = (pos[0], pos[1] + height)

        pos = pos_store
        for line in lines:
            # regular text
            draw.text(pos, line, text_colour, font, anchor=anchor)

            # update pos for next line
            height = get_text_height(line, font)
            pos = (pos[0], pos[1] + height)

    img.save(os.path.join(output_path, 'games.png'))


def players_image(
        players: dict[int|None, Player],
        year: int|None,
        output_path: str
) -> None:
    players_plays = [player for player in players.values()
                     if player.plays[year]]
    players_plays.sort(key=lambda player: player.plays[year], reverse=True)

    text_colour = (0, 0, 0)
    font = ImageFont.truetype('fonts/IBMPlexSans-Thin.ttf', 64)

    img = Image.open('images/players.png')
    draw = ImageDraw.Draw(img)

    positions = [(220, 380), (220, 500), (220, 620),
                 (220, 740), (220, 860)]
    max_lens = [15, 15, 15, 15, 15]
    for player, pos, max_len in zip(players_plays[:min(5, len(players_plays))], positions, max_lens):
        text = textwrap.fill(player.name.upper(), max_len)
        height = get_text_height(text, font)
        pos = (pos[0], pos[1] - height)

        for line in text.splitlines():
            # regular text
            draw.text(pos, line, text_colour, font, anchor='lt')

            # update pos for next line
            height = get_text_height(line, font)
            pos = (pos[0], pos[1] + height)

    img.save(os.path.join(output_path, 'players.png'))


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

    with open(args.path, 'r', encoding='UTF-8') as f:
        data = json.load(f)

    if not os.path.exists(pickles_path):
        os.mkdir(pickles_path)

    if not os.path.exists(args.output):
        os.mkdir(args.output)

    games = load_games(data)
    players = load_players(data)
    mechanics = get_mechanics(games, data)

    mechanics_image(mechanics, args.year, args.output)
    games_image(games, args.year, args.output)
    players_image(players, args.year, args.output)


if __name__ == '__main__':
    main()
