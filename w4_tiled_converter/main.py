import argparse
import json
from os.path import basename, splitext
import sys


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
    print("ERROR: not implemented")
    sys.exit(-1)

    #with open(filename) as f:
    #    tileset = json.load(f)

    #h_file = splitext(filename)[0] + '.h'
    #c_file = splitext(filename)[0] + '.c'

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
