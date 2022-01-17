from os.path import basename

from w4_tiled_converter import tilemap, tileset


class Sources:
    def __init__(self, h_filename: str, c_filename: str) -> None:
        self.h_filename: str = h_filename
        self.c_filename: str = c_filename
        self.includes: list[str] = ["#include <stdint.h>\n", '#include "tiled.h"\n']
        self.defines: dict[str, str] = {}
        self.arrays: list[tuple[str, str]] = []

    def add_define(self, name: str, value: str):
        self.defines[name] = value

    def add_array(self, value: tuple[str, str]):
        self.arrays.append(value)

    # def add_tileset(self, name, tilesize, width, height, data):
    def add_tileset(self, name, tilesize, ts: tileset.TileSet):
        # image = TwoBitImage(name, width, height, data)

        c_src = ts.to_c_src()
        self.add_array(c_src)
        self.add_define(f"TILESIZE_{name}", str(tilesize))

    def add_tilemap(self, tm: tilemap.TileMap):
        c_src = tm.to_c_str()
        self.add_array(c_src)
        includes = tm.includes()
        for include in includes:
            self.includes += f'#include "{include}"\n'

    def print_header(self) -> str:
        h = ""

        for v in self.includes:
            h += v

        for k, v in self.defines.items():
            h += f"#define {k} {v}\n"

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
        with open(self.h_filename, "w") as out:
            out.write(self.print_header())
        with open(self.c_filename, "w") as out:
            out.write(self.print_source())
