class TileMap:
    def __init__(self, name, width, height, data) -> None:
        self.name = name
        self.width = width
        self.height = height
        self.data = data

    def to_c_str(self) -> tuple[str, str]:
        data_str_list: list[str] = [str(x) if x >= 1 else str(x - 1) for x in self.data]
        data_str: str = ", ".join(data_str_list)

        return (
            f"extern const uint32_t {self.name}_tilemap[{len(self.data)}];\n",
            f"const uint32_t {self.name}_tilemap[] =" + " {" + data_str + "};\n",
        )
