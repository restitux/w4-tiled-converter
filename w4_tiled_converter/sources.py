from os.path import basename

class TwoBitImage:
    def __init__(self, name, width, height, data) -> None:
        self.name = name
        self.width = width
        self.height = height
        self.data = data


    def to_c_src(self) -> tuple[str, str]:
        bs = []
        for i in range(0, len(self.data), 4):
            cols = self.data[i:i+4]
            str_col = ["{0:02b}".format(c) for c in cols]
            binary_cols = "".join(str_col)
            bs.append(f"0b{binary_cols}")


        array_define = ", ".join(bs)

        return (
            f'extern const uint8_t {self.name}_tileset[{len(bs)}];\n',
            f'const uint8_t {self.name}_tileset[] =' + ' {' + f'{array_define}' + '};\n'
        )

class TileMap:
    def __init__(self, name, width, height, data) -> None:
        self.name = name
        self.width = width
        self.height = height
        self.data = data

    def to_c_str(self) -> tuple[str, str]:
        data_str_list : list[str] = [str(x) for x in self.data]
        data_str : str = ", ".join(data_str_list)

        return (
            f'extern const uint32_t {self.name}_tilemap[{len(self.data)}];\n',
            f'const uint32_t {self.name}_tilemap[] =' + ' {' + data_str + '};\n'
        )

class Sources:
    def __init__(self, h_filename : str, c_filename : str) -> None:
        self.h_filename : str = h_filename
        self.c_filename : str = c_filename
        self.includes : list[str] = ["#include <stdint.h>\n"]
        self.defines : dict[str, str] = {}
        self.arrays : list[tuple[str, str]] = []

    def add_define(self, name : str, value : str):
        self.defines[name] = value

    def add_array(self, value : tuple[str, str]):
        self.arrays.append(value)

    def add_tileset(self, name, tilesize, width, height, data):
        image = TwoBitImage(name, width, height, data)

        c_src = image.to_c_src()
        self.add_array(c_src)
        self.add_define(f"TILESIZE_{name}", str(tilesize))

    def add_tilemap(self, name, width, height, data):
        tilemap = TileMap(name, width, height, data)
        c_src = tilemap.to_c_str()
        self.add_array(c_src)


    def print_header(self) -> str:
        h = ""

        for v in self.includes:
            h += v

        for k, v in self.defines.items():
            h += f'#define {k} {v}\n'

        for v in self.arrays:
            h += v[0]

        return h

    def print_source(self) -> str:
        c = ""

        c += f'#include "{basename(self.h_filename)}"\n'

        for v in self.arrays:
            c += v[1]

        return c


    def to_file(self):
        with open(self.h_filename, 'w') as out:
            out.write(self.print_header())
        with open(self.c_filename, 'w') as out:
            out.write(self.print_source())
