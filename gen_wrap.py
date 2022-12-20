import os
import json
import requests

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import textwrap

import argparse

from get_data import *


def truncate_name(name, max_length=15):
    if len(name) > max_length:
        return f'{name[:max_length-3]}...'
    return name


def get_text_height(text_string, font):
    ascent, descent = font.getmetrics()
    lines = text_string.count('\n') + 1

    return ascent * lines


def mechanics_image(mechanics, year, output_path):
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
        height = get_text_height(text, font)
        pos = (pos[0], pos[1] - height)

        for line in text.splitlines():
            # blurred backdrop
            blurred = Image.new('RGBA', img.size)
            draw_b = ImageDraw.Draw(blurred)
            draw_b.text(pos, line, blur_colour, font, stroke_width=5)
            blurred = blurred.filter(ImageFilter.BoxBlur(5))

            img.paste(blurred, blurred)

            # regular text
            draw.text(pos, line, text_colour, font)

            # update pos for next line
            height = get_text_height(line, font)
            pos = (pos[0], pos[1] + height)

    img.save(os.path.join(output_path, 'mechanics.png'))


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


if __name__ == '__main__':
    main()
