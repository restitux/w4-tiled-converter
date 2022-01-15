import argparse
import json
from os.path import basename, join, split, splitext
import sys

import png

# Convert a tiled tmx tilemap to source files
def tilemap(filename: str):
    # Read in JSON tilemap
    with open(filename) as f:
        tilemap = json.load(f)

    # Calculate output filenames
    h_filename = splitext(filename)[0] + '.h'
    c_filename = splitext(filename)[0] + '.c'

    # Get base filename
    base_filename = splitext(basename(splitext(filename)[0]))[0]

    # general includes
    includes = '#include <stdint.h>\n\n'

    h_file = includes
    c_file = f'#include "{basename(h_filename)}"\n\n'

    # get size of data
    data_h = tilemap["layers"][0]["height"]
    data_w = tilemap["layers"][0]["width"]
    data_len = data_h * data_w

    varname = base_filename.upper()

    # c declaration for array name and type
    tilemap_var = f'const uint32_t {varname}_TILEMAP[{data_len}]'

    # Add array declaration to header file
    h_file += 'extern ' + tilemap_var + ';' + '\n'

    # Add constants to source file
    c_file += f'const uint32_t {varname}_TILEMAP_HEIGHT = {data_h};' + '\n'
    c_file += f'const uint32_t {varname}_TILEMAP_WIDTH = {data_w};' + '\n'

    # Add array definition to source file
    c_file += tilemap_var
    c_file += " = {\n"
    data_str = [str(x) for x in tilemap["layers"][0]["data"]]
    c_file += ", ".join(data_str)
    c_file += "};\n"


    # write header and source files to disk
    with open(h_filename, 'w') as f:
        f.write(h_file)

    with open(c_filename, 'w') as f:
        f.write(c_file)


def tileset(filename: str):
    #print("ERROR: not implemented")
    #sys.exit(-1)

    print(f'INFO: Processing tileset {filename}')

    with open(filename) as f:
        tileset = json.load(f)

    image_w = tileset['imagewidth']
    image_h = tileset['imageheight']

    png_filename = join(split(filename)[0], tileset['image'])

    pngfile = png.Reader(png_filename).read()

    # TODO: DEBUG
    print(pngfile)

    if (image_w != pngfile[0]) or (image_h != pngfile[1]):
        print(f"ERROR: PNG file w/h ({pngfile[0]}, {pngfile[1]}), doesn't match tileset w/h ({tileset['imagewidth']}, {tileset['imageheight']})")
        sys.exit(-1)

    pixel_mapping = {
        'FF0000': '00',
        '000000': '01',
        'A6A6A6FF': '10',
        'FFFFFFFF': '11',
    }

    pixel_list = []

    pngdata = list(pngfile[2])
    print(pngdata)

    for y in range(image_h):
        print(pngdata[y])
        print(len(pngdata[y]))
        for x in range(0, len(pngdata[y]), 4):
            pixel_data = [d for d in pngdata[y][x:x + 4]]
            pixel_data = ''.join([format(e, 'X') for e in pixel_data])
            print(pixel_data)
            if pixel_data not in pixel_mapping:
                print(f"ERROR: Pixel data {pixel_data} not known")
                sys.exit(-1)



    # Calculate output filenames
    h_filename = splitext(filename)[0] + '.h'
    c_filename = splitext(filename)[0] + '.c'

    # Get base filename
    base_filename = splitext(basename(splitext(filename)[0]))[0]


    # general includes
    includes = '#include <stdint.h>\n\n'

    h_file = includes
    c_file = f'#include "{basename(h_filename)}"\n\n'



    sys.exit(-1)

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
        tilemap(args.filename)
    else:
        tileset(args.filename)



if __name__ == "__main__":
    main()
