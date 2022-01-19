import json
from os.path import basename, splitext

from PIL import Image

from w4_tiled_converter import sources, tilemap, tileset
from w4_tiled_converter.block_spawn import BlockSpawn
from w4_tiled_converter.data_layer import DataLayer


def get_pixel_color_id(color):
    if color == (255, 0, 0):
        return 0
    elif color == (0, 0, 0):
        return 1
    elif color == (168, 168, 168):
        return 2
    elif color == (255, 255, 255):
        return 3
    else:
        print(f"ERROR: unknown color: {color}")
        exit(1)


def convert_region(tile_id, region):
    result = []
    for y in range(region.size[1]):  # framebuffer coords = y * 160 + x
        for x in range(region.size[0]):
            color_id = get_pixel_color_id(region.getpixel((x, y)))
            result.append(color_id)
    return result


def convert_tileset(
    png_filename: str, h_filename: str, c_filename: str, tilesize: int, name: str
):
    png = Image.open(png_filename)
    print(f"image is {png.format} of {png.size}")

    tile_id = 0
    color_ids = []
    for tile_y in range(0, png.size[1], tilesize):
        for tile_x in range(0, png.size[0], tilesize):
            tile_region = (tile_x, tile_y, tile_x + tilesize, tile_y + tilesize)
            tile_colors = convert_region(tile_id, png.crop(tile_region))
            color_ids.extend(tile_colors)
            tile_id += 1

    ts = tileset.TileSet(name, png.size[0], png.size[1], color_ids)

    s = sources.Sources(h_filename, c_filename)
    s.add_tileset(name, tilesize, ts)
    s.to_file()

def get_property(layer, name: str) -> str:
    if (layer['properties']):
        for p in layer['properties']:
            if p['name'] == name:
                return p['value']
    return None

def convert_tilemap(tilemap_filename: str, h_filename: str, c_filename: str, name: str):

    # Read in JSON tilemap
    with open(tilemap_filename) as f:
        tilemap_json = json.load(f)

    s = sources.Sources(h_filename, c_filename)

    tm = tilemap.TileMap(name)
    for layer in tilemap_json["layers"]:
        if layer["type"] == "tilelayer":
            layer_name = layer["name"]
            data_h = layer["height"]
            data_w = layer["width"]
            data_len = data_h * data_w
            data = layer["data"]
            if get_property(layer, 'kind') == "data":
                tm.add_data_layer(DataLayer(name, layer_name, int(data_w), int(data_h), data))

            print(f"adding layer {layer_name}")
            tm.add_layer(
                layer_name,
                data_w,
                data_h,
                data,
            )
        elif layer["type"] == "objectgroup":
            if layer["name"] == "entrances":
                tm.add_entrances(layer)
            if layer["name"] == "block-spawns":
                for obj in layer["objects"]:
                    x = int(obj["x"])
                    y = int(obj["y"])
                    id = int(obj["id"])
                    tm.add_block_spawn(BlockSpawn(x, y, id))

    for tileset in tilemap_json["tilesets"]:
        tileset_name = basename(splitext(tileset["source"])[0]).replace("-", "_")
        tileset_include = splitext(tileset["source"])[0] + ".set.h"
        tileset_gid = tileset["firstgid"]
        tm.add_tileset(tileset_name, (tileset_include, tileset_gid))

    s.add_tilemap(tm)
    s.to_file()
