class TileMap:
    def __init__(self, name) -> None:
        self.name = name
        self.layers = {}

    def add_layer(self, name, width, height, data, tileset):
        self.layers[name] = (width, height, data, tileset)

    def includes(self):
        includes = []
        includes.append(self.layers["static"][3][1])
        return includes

    def to_c_str(self) -> tuple[str, str]:
        layers_data_str = {}
        for name, (_, _, data, _) in self.layers.items():
            data_str_list: list[str] = [str(x - 1) if x >= 1 else str(x) for x in data]
            layers_data_str[name] = ", ".join(data_str_list)

        static = self.layers["static"]
        collision = self.layers["collision"]

        h = f"extern const struct TileMap {self.name}_tilemap;\n"
        c = (
            f"const struct TileMap {self.name}_tilemap = "
            + "{\n"
            + "    .static_map = {\n"
            + f"        .width = {static[0]},\n"
            + f"        .height = {static[1]},\n"
            + "        .map = (uint32_t []){"
            + layers_data_str["static"]
            + "},\n"
            + f"        .tileset = &{static[3][0]}_tileset\n"
            + "    },\n"
            + "    .collision_map = {\n"
            + f"        .width = {collision[0]},\n"
            + f"        .height = {collision[1]},\n"
            + "        .map = (uint32_t []){"
            + layers_data_str["collision"]
            + "}\n"
            + "    },\n"
            + "};\n"
        )
        return (h, c)
