import argparse
import json
from os.path import basename, join, split, splitext
import sys

from w4_tiled_converter import tileset, tilemap

# Convert a tiled tmx tilemap to source files
def tilemap_subcommand(filename: str):
    print(f'INFO: Processing tilemap {filename}')
    name = basename(splitext(splitext(filename)[0])[0])
    # Calculate output filenames
    h_filename = splitext(filename)[0] + '.h'
    c_filename = splitext(filename)[0] + '.c'

    tilemap.convert(filename, h_filename, c_filename, name)



def tileset_subcommand(filename: str):
    print(f'INFO: Processing tileset {filename}')

    # Calculate output filenames
    h_filename = splitext(filename)[0] + '.h'
    c_filename = splitext(filename)[0] + '.c'

    # Read in JSON tileset
    with open(filename) as f:
        tileset_json = json.load(f)

    # Validate tiles are square
    tile_w = tileset_json['tilewidth']
    tile_h = tileset_json['tileheight']
    if tile_w != tile_h:
        print(f'ERROR: Tiles of different h / w are not supported ({tile_w}, {tile_h})')
        sys.exit(-1)

    # Convert tileset to source files
    png_filename = join(split(filename)[0], tileset_json['image'])
    tileset.convert(png_filename, h_filename, c_filename, tile_w, tileset_json['name'])


def main():
    #print("w4 tileset converter")

    parser = argparse.ArgumentParser(description='Generate sources from a tilemap')
    parser.add_argument('filetype', action='store',
                        help='tilemap or tileset',
                        choices=('tilemap', 'tileset'))
    parser.add_argument('filename', action='store',
                        help='filename')

    args = parser.parse_args()


    if args.filetype == 'tilemap':
        tilemap_subcommand(args.filename)
    else:
        tileset_subcommand(args.filename)



if __name__ == "__main__":
    main()
