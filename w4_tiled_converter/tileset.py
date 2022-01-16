class TileSet:
    def __init__(self, name, width, height, data) -> None:
        self.name = name
        self.width = width
        self.height = height
        self.data = data

    def to_c_src(self) -> tuple[str, str]:
        bs = []
        for i in range(0, len(self.data), 4):
            cols = self.data[i : i + 4]
            str_col = ["{0:02b}".format(c) for c in cols]
            binary_cols = "".join(str_col)
            bs.append(f"0b{binary_cols}")

        array_define = ", ".join(bs)

        return (
            f"extern const uint8_t {self.name}_tileset[{len(bs)}];\n",
            f"const uint8_t {self.name}_tileset[] ="
            + " {"
            + f"{array_define}"
            + "};\n",
        )
