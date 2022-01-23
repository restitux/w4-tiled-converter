from w4_tiled_converter import block_spawn
from w4_tiled_converter.text_trigger import TextTriggers
from w4_tiled_converter.block_spawn import BlockSpawns
from w4_tiled_converter.image_layer import ImageLayer
from w4_tiled_converter.data_layer import DataLayer

import hashlib


class TileMap:
    def __init__(self, name) -> None:
        self.name = name
        self.entrances = {}
        self.layers = {}
        self.image_layers = {}
        self.data_layers = {}
        self.tilesets = {}
        self.block_spawns = BlockSpawns(name)
        self.text_triggers = TextTriggers(name)
        name_hash = hashlib.md5(name.encode("utf-8")).hexdigest()
        self.name_hash = str(int(name_hash, 16) % (2 ** 16) - 1)

    def add_layer(self, name, width, height, data):
        self.layers[name] = (width, height, data)

    def add_image_layer(self, image_layer: ImageLayer):
        self.image_layers[image_layer.name] = image_layer

    def add_data_layer(self, data_layer: DataLayer):
        self.data_layers[data_layer.name] = data_layer

    def add_tileset(self, name, tileset):
        self.tilesets[name] = tileset

    def add_entrances(self, entrances):
        self.entrances = entrances

    def add_block_spawn(self, b):
        self.block_spawns.block_spawns.add_spawn(b)

    def add_text_trigger(self, t):
        self.text_triggers.text_triggers.add_trigger(t)

    def includes(self):
        includes = []
        includes.append(self.tilesets["tiles"][0])
        for o in self.entrances["objects"]:
            target_map = ""
            for x in o["properties"]:
                if x["name"] == "target_map":
                    target_map = x["value"]
            if target_map != self.name:
                includes.append(f"{target_map}.map.h")

        return includes

    def split_id(self, tile_id) -> tuple[int, int]:
        id_bits = tile_id & 0xFFF
        rotation_bits = (tile_id & (0xF << 28)) >> 28
        return (id_bits, rotation_bits)

    def fix_id(self, tile_id):
        id_bits = tile_id & 0xFFF
        rotation_bits = (tile_id & (0xF << 28)) >> 16
        new_tile_id = id_bits | rotation_bits

        if id_bits > 0 and id_bits < 257:
            return new_tile_id - 1
        elif id_bits >= 257:
            return new_tile_id - 257
        else:
            return new_tile_id

    def make_static_data_str(self, data) -> tuple[str, str]:

        split_id_list: list[tuple[int, int]] = [self.split_id(x) for x in data]

        data_str_list: list[str] = [
            str(x[0] - 1) if x[0] >= 1 else str(x[0]) for x in split_id_list
        ]
        data_str: str = ", ".join(data_str_list)

        data_rot_str_list: list[str] = []
        for i in range(0, len(split_id_list), 2):
            lsb: str = format(split_id_list[i][1], "04b")
            msb: str = format(split_id_list[i + 1][1], "04b")
            c_bits: str = f"0b{msb}{lsb}"
            if len(c_bits) != 10:
                raise Exception(
                    f'packed static data rotation bits "{c_bits}" at index "{i}" was the wrong length'
                )
            data_rot_str_list.append(c_bits)
        data_rot_str: str = ", ".join(data_rot_str_list)

        return (data_str, data_rot_str)

    def make_collision_data_str(self, data):
        binary_data = [0 if d == 0 else 1 for d in data]
        out = []
        for i in range(0, len(binary_data), 8):
            b = binary_data[i : i + 8]
            b.reverse()  # lsb should be 0 index
            b_str = "".join([str(bit) for bit in b])
            out.append(f"0b{b_str}")
        return ", ".join(out)

    def to_c_str(self) -> tuple[str, str]:

        layers_data_str = {}
        for name, (_, _, data) in self.layers.items():
            if name == "collision":
                layers_data_str[name] = self.make_collision_data_str(data)
            else:
                layers_data_str[name] = self.make_static_data_str(data)

        if self.entrances and self.entrances["objects"]:
            entrances_arr = []
            entrances_target_init = []
            for i, o in enumerate(self.entrances["objects"]):
                props = {}
                for p in o["properties"]:
                    props[p["name"]] = p["value"]
                entrances_arr.append(
                    "(struct TileMap_Entrance){"
                    + f'.x = {o["x"]}, '
                    + f'.y = {o["y"]}, '
                    + f'.width = {o["width"]}, '
                    + f'.height = {o["height"]}, '
                    + f'.id = {o["id"]}, '
                    + f".target_map = NULL, "
                    + f'.target_entrance = {props["target_entrance"]}, '
                    + f'.is_entrance = {str(props["is_entrance"]).lower()}'
                    + "}"
                )
                entrances_target_init.append(
                    f"{self.name}_tilemap.entrances.entrances[{i}].target_map = &{props['target_map']}_tilemap;"
                )
            entrances_arr_str = ", ".join(entrances_arr)
            entrances_target_init_str = "\n".join(entrances_target_init)
            entrances_str = (
                "    .entrances = {\n"
                f"        .entrances = {self.name}_entrances_data,\n"
                + f"        .length = {len(entrances_arr)}\n"
                + "    },\n"
            )
        else:
            entrances_str = (
                "    .entrances = {\n"
                + "        .entrances = NULL,\n"
                + "        .length = 0\n"
                + "    },\n"
            )
            entrances_target_init_str = ""

        # if len(self.block_spawns.block_spawns) > 0:

        static = self.layers["static"]
        # collision = self.layers["collision"]
        # overlay = self.layers["overlay"]

        h = f"extern struct TileMap {self.name}_tilemap;\nvoid initalize_{self.name}_tilemap();\n"
        c = (
            f"struct TileMap {self.name}_tilemap;\n\n"
            + f"const uint8_t {self.name}_static_map[] = {{{layers_data_str['static'][0]}}};\n"
            + f"const uint8_t {self.name}_static_map_rotations[] = {{{layers_data_str['static'][1]}}};\n"
            + self.image_layers["overlay"].make_static_initalization()
            + "\n"
            # + f"const uint8_t {self.name}_overlay_map[] = {{{layers_data_str['overlay'][0]}}};\n"
            # + f"const uint8_t {self.name}_overlay_map_rotations[] = {{{layers_data_str['overlay'][1]}}};\n"
            + f"struct TileMap_Entrance {self.name}_entrances_data[] = {{{entrances_arr_str}}};\n"
            + self.block_spawns.block_spawns.make_static_init()
            + self.text_triggers.text_triggers.make_static_init()
            + "\n"
            + self.data_layers["collision"].make_static_initalization()
            + "\n"
            + self.data_layers["special"].make_static_initalization()
            + "\n"
            + f"void initalize_{self.name}_tilemap() "
            + "{\n"
            + f"{self.name}_tilemap = (struct TileMap)"
            + "{\n"
            + f"    .id = {self.name_hash},\n"
            + "    .static_map = {\n"
            + f"        .width = {static[0]},\n"
            + f"        .height = {static[1]},\n"
            + f"        .map = {self.name}_static_map,\n"
            + f"        .map_rotations = {self.name}_static_map_rotations,\n"
            + f"        .tileset = &tiles_tileset\n"
            + "    },\n"
            + f"    .collision_map = {self.data_layers['collision'].make_assignment()}"
            + f"    .special_map = {self.data_layers['special'].make_assignment()}"
            + f"    .overlay_map = {self.image_layers['overlay'].make_assignment()}"
            # + "    .overlay_map = {\n"
            # + f"        .width = {overlay[0]},\n"
            # + f"        .height = {overlay[1]},\n"
            # + f"        .map = {self.name}_overlay_map,\n"
            # + f"        .map_rotations = {self.name}_overlay_map_rotations,\n"
            # + f"        .tileset = &tiles_tileset\n"
            # + "    },\n"
            + entrances_str
            + f"    .block_spawns = {self.block_spawns.make_assignment()}"
            + f"    .text_triggers = {self.text_triggers.make_assignment()}"
            + "};\n"
            + entrances_target_init_str
            + "\n}"
        )
        return (h, c)
