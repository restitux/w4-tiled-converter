def split_id(tile_id) -> tuple[int, int]:
    id_bits = tile_id & 0xFFF
    rotation_bits = (tile_id & (0xF << 28)) >> 28
    return (id_bits, rotation_bits)


class RLE:
    def __init__(self, max_run: int, run_value: int):
        self.max_run = max_run
        self.run_value = run_value
        self.is_run = False
        self.run_length = 0
        self.a = []
        self.b = []

    def start_run(self):
        self.is_run = True
        self.run_length = 0

    def end_run(self):
        self.a.append(self.run_value)
        self.b.append(self.run_length)
        self.is_run = False

    def add_free_value(self, value):
        (t, r) = split_id(value)
        # add tile and rotation
        self.a.append(t)
        self.b.append(r)

    def step(self, value: int):
        # if in run
        if self.is_run:
            # if run exceedes max length, stop run
            if self.run_length == self.max_run:
                self.end_run()
            # if current value is not a run, end run
            elif value != self.run_value:
                self.end_run()
                self.add_free_value(value)
            # continue run
            else:
                self.run_length += 1
        # if not in a run
        else:
            # if value in run value, start run
            if value == self.run_value:
                self.start_run()
                # add value
            else:
                self.add_free_value(value)

    def get_vals(self) -> tuple[list[int], list[int]]:
        if self.is_run:
            self.end_run()
        return (self.a, self.b)


class EncodedRoom:
    def __init__(self, tiles: list[int]):

        self.tiles = []
        self.rotations = []

        rle = RLE(255, 0)
        # iterate through tiles in room
        for tile in tiles:
            rle.step(tile)

        (a, b) = rle.get_vals()
        self.tiles = a
        self.rotations = b


class ImageLayer:
    STRUCT_NAME = "TileMap_MapLayer"

    def __init__(self, ctx_name, name, width, height, data) -> None:
        self.ctx_name = ctx_name
        self.name = name
        self.width = width
        self.height = height

        ## 1. Reorganize data to be per room

        ROOM_HEIGHT: int = 20
        ROOM_WIDTH: int = 20

        room_tiles: list[list[int]] = []
        # iterate through grid of rooms in tilemap
        for room_y in range(self.height // 20):
            # base index for this row
            room_column_base: int = (
                ROOM_WIDTH * ROOM_HEIGHT * (self.width // ROOM_WIDTH) * room_y
            )
            for room_x in range(self.width // 20):
                # base index for this column
                room_row_base: int = ROOM_WIDTH * room_x
                # get the index of the top left corner of the room
                room_base: int = room_row_base + room_column_base

                tiles: list[int] = []
                # add tiles from all room rows to array
                for y in range(ROOM_HEIGHT):
                    tile_row_base: int = room_base + (
                        y * ROOM_WIDTH * (self.width // 20)
                    )
                    tiles += data[tile_row_base : tile_row_base + ROOM_WIDTH]

                room_tiles.append(tiles)

        ## 2. Generate output strings
        tiles_arr: list[int] = []
        rotations_arr: list[int] = []

        for room in room_tiles:
            r = EncodedRoom(room)
            tiles_arr += r.tiles
            rotations_arr += r.rotations

        tiles_arr_str: list[str] = [str(x - 1) if x > 0 else str(x) for x in tiles_arr]
        rotations_arr_str: list[str] = [str(x) for x in rotations_arr]

        tiles_str: str = ", ".join(tiles_arr_str)
        rotations_str: str = ", ".join(rotations_arr_str)

        self.tiles_str = tiles_str
        self.rotations_str = rotations_str

    def make_static_initalization(self):
        tile_str: str = f"const uint8_t {self.map_static_initalizer_name()}[] = {{{self.tiles_str}}};"
        rotations_str: str = f"const uint8_t {self.rotations_static_initalizer_name()}[] = {{{self.rotations_str}}};"
        return tile_str + "\n" + rotations_str

    def make_assignment(self):
        return f"{{ .width={self.width}, .height={self.height}, .map={self.map_static_initalizer_name()}, .map_rotations={self.rotations_static_initalizer_name()}, .tileset = &tiles_tileset }},\n"

    def typename():
        return f"struct {ImageLayer.STRUCT_NAME}"

    def map_static_initalizer_name(self):
        return f"{self.ctx_name}_{self.name}_map_map"

    def rotations_static_initalizer_name(self):
        return f"{self.ctx_name}_{self.name}_map_rotations"
