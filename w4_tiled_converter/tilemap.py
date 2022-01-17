class TileMap:
    def __init__(self, name) -> None:
        self.name = name
        self.layers = {}
        self.tilesets = {}

    def add_layer(self, name, width, height, data):
        self.layers[name] = (width, height, data)

    def add_tileset(self, name, tileset):
        self.tilesets[name] = tileset

    def includes(self):
        includes = []
        includes.append(self.tilesets["tiles"][0])
        return includes
    def fix_id(self, tile_id):
        if (tile_id & 0xFFF) > 0 and (tile_id & 0xFFF) < 257:
            return tile_id - 1
        elif (tile_id & 0xFFF) > 257:
            return tile_id - 257 
        else:
            return tile_id


    def to_c_str(self) -> tuple[str, str]:
        layers_data_str = {}
        for name, (_, _, data) in self.layers.items():
            data_str_list: list[str] = [str(self.fix_id(int(x))) for x in data]
            layers_data_str[name] = ", ".join(data_str_list)

        static = self.layers["static"]
        collision = self.layers["collision"]
        overlay = self.layers['overlay']

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
            + f"        .tileset = &tiles_tileset\n"
            + "    },\n"
            + "    .collision_map = {\n"
            + f"        .width = {collision[0]},\n"
            + f"        .height = {collision[1]},\n"
            + "        .map = (uint32_t []){"
            + layers_data_str["collision"]
            + "}\n"
            + "    },\n"
            + "    .overlay_map = {\n"
            + f"        .width = {overlay[0]},\n"
            + f"        .height = {overlay[1]},\n"
            + "        .map = (uint32_t []){"
            + layers_data_str["overlay"]
            + "},\n"
            + f"        .tileset = &tiles_tileset\n"
            + "    },\n"
            + "};\n"
        )
        return (h, c)
