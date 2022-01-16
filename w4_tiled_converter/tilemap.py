import json

from w4_tiled_converter import sources

def convert(tilemap_filename : str, h_filename : str, c_filename : str, name : str):

    # Read in JSON tilemap
    with open(tilemap_filename) as f:
        tilemap = json.load(f)

    data_h = tilemap["layers"][0]["height"]
    data_w = tilemap["layers"][0]["width"]
    data_len = data_h * data_w
    data = tilemap["layers"][0]["data"]

    s = sources.Sources(h_filename, c_filename)
    s.add_tilemap(name, data_w, data_h, data)
    s.to_file()
