from PIL import Image
import header

TILESIZE = 8


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
    print(f"handling tile {tile_id} (size: {region.size})")
    result = []
    for y in range(region.size[1]): #framebuffer coords = y * 160 + x
        for x in range(region.size[0]):
            color_id = get_pixel_color_id(region.getpixel((x, y)))
            result.append(color_id)
    return result


def convert(png):
    tile_id = 0
    color_ids = []
    for tile_x in range(0, png.size[0], TILESIZE):
        for tile_y in range(0, png.size[1], TILESIZE):
            print(tile_x, tile_y)
            tile_region = (tile_x, tile_y, tile_x + 8, tile_y + 8)
            tile_colors = convert_region(tile_id, im.crop(tile_region))
            color_ids.extend(tile_colors)
            tile_id += 1
            print(tile_colors)


    h = header.Header()
    h.add_tileset("tiles", TILESIZE, png.size[0], png.size[1], color_ids)
    h.print()
    h.to_file()

if __name__ == "__main__":
    im = Image.open('tiles.png')
    print(f"image is {im.format} of {im.size}")
    convert(im)