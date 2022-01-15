

class TwoBitImage:
    def __init__(self, name, width, height, data) -> None:
        self.name = name
        self.width = width
        self.height = height
        self.data = data


    def to_define(self):
        bs = []
        for i in range(0, len(self.data), 4):
            cols = self.data[i:i+4]
            print(cols)
            str_col = ["{0:02b}".format(c) for c in cols]
            binary_cols = "".join(str_col)
            bs.append(f"0b{binary_cols}")
        

        array_define = ", ".join(bs)

        return f"#define {self.name} [{array_define}]\n"

class Header:
    def __init__(self) -> None:
        self.images = {}
        self.defines = {}


    def add_2bpp_image(self, name, width, height, data):
        self.images[name] = TwoBitImage(name, width, height, data)

    def add_define(self, name, value):
        self.defines[name] = value

    def add_tileset(self, name, tilesize, width, height, data):
        self.add_2bpp_image(f"TILESET_{name}", width, height, data)
        self.add_define(f"TILESIZE_{name}", tilesize)
    

    def print(self):
        o = ""
        for k, v in self.images.items():
            o += v.to_define()
            print(v.to_define())
        for k, v in self.defines.items():
            o += f"#define {k} {v}"
            print(f"#define {k} {v}")
        return o

    def to_file(self):
        with open('example.h', 'w') as out:
            out.write(self.print())



