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

        array_str = ", ".join(bs)

        h = f"extern const struct TileSet {self.name}_tileset;\n"
        c = (
            f"const struct TileSet {self.name}_tileset = "
            + "{\n"
            + "    .tileset = (uint8_t[]){"
            + array_str
            + "}\n"
            + "};\n"
        )
        return (h, c)
