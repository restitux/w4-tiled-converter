import argparse
import json
from os.path import basename, join, split, splitext
import sys

from w4_tiled_converter import converters

# Convert a tiled tmx tilemap to source files
def tilemap_subcommand(filename: str):
    print(f"INFO: Processing tilemap {filename}")
    name = basename(splitext(splitext(filename)[0])[0])
    # Calculate output filenames
    h_filename = splitext(filename)[0] + ".h"
    c_filename = splitext(filename)[0] + ".c"

    converters.convert_tilemap(filename, h_filename, c_filename, name)


def tileset_subcommand(filename: str):
    print(f"INFO: Processing tileset {filename}")

    # Calculate output filenames
    h_filename = splitext(filename)[0] + ".h"
    c_filename = splitext(filename)[0] + ".c"

    # Read in JSON tileset
    with open(filename) as f:
        tileset_json = json.load(f)

    # Validate tiles are square
    tile_w = tileset_json["tilewidth"]
    tile_h = tileset_json["tileheight"]
    if tile_w != tile_h:
        print(f"ERROR: Tiles of different h / w are not supported ({tile_w}, {tile_h})")
        sys.exit(-1)

    # Convert tileset to source files
    png_filename = join(split(filename)[0], tileset_json["image"])
    converters.convert_tileset(
        png_filename, h_filename, c_filename, tile_w, tileset_json["name"]
    )


def header_subcommand(filename: str):
    header = """
#ifndef __TILED_H_
#define __TILED_H_

#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>

struct Entrance;

struct TileSet {
    const uint8_t *tileset;
};

struct TileMap_MapLayer {
    uint32_t width;
    uint32_t height;
    const uint16_t *map;
    const struct TileSet *tileset;
};

struct TileMap_DataLayer {
    uint32_t width;
    uint32_t height;
    const uint8_t *map;
};

struct TileMap_Entrance {
    uint32_t x;
    uint32_t y;
    uint32_t width;
    uint32_t height;
    uint8_t id;
    const struct TileMap *target_map;
    bool is_entrance;
    uint32_t target_entrance;
};

struct TileMap_BlockSpawn {
    uint8_t x;
    uint8_t y;
    uint8_t id;
};

struct TileMap_Entrances {
    struct TileMap_Entrance *entrances;
    uint32_t length;
};

struct TileMap_BlockSpawns {
    struct TileMap_BlockSpawn *block_spawns;
    uint32_t length;
};

struct TileMap {
    struct TileMap_MapLayer static_map;
    struct TileMap_MapLayer overlay_map;
    struct TileMap_DataLayer collision_map;
    struct TileMap_DataLayer special_map;
    struct TileMap_Entrances entrances;
    struct TileMap_BlockSpawns block_spawns;
};



#endif // __TILED_H
"""

    with open(filename, "w") as out:
        out.write(header)


def main():
    # exit(-1)
    # print("w4 tileset converter")

    parser = argparse.ArgumentParser(description="Generate sources from a tilemap")
    parser.add_argument(
        "filetype",
        action="store",
        help="tilemap, tileset or header",
        choices=("tilemap", "tileset", "header"),
    )
    parser.add_argument("filename", action="store", help="filename")

    args = parser.parse_args()

    if args.filetype == "tilemap":
        tilemap_subcommand(args.filename)
    elif args.filetype == "tileset":
        tileset_subcommand(args.filename)
    elif args.filetype == "header":
        header_subcommand(args.filename)


if __name__ == "__main__":
    main()
