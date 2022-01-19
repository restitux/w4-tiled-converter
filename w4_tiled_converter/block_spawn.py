
class BlockSpawn:
    STRUCT_NAME = "TileMap_BlockSpawn"

    def __init__(self, x:int , y: int, id: int) -> None:
        self.x = x
        self.y = y
        self.id = id

    
    def make_static_init_entry(self) -> str:
        return f"({BlockSpawn.typename()}) {{.id={self.id}, .x={self.x}, .y={self.y}}}"

    def typename() -> str:
        return f"struct {BlockSpawn.STRUCT_NAME}"

class StaticBlockSpawnList:
    def __init__(self, ctx_name: str) -> None:
        self.spawns = []
        self.ctx_name = ctx_name

    def add_spawn(self, x: BlockSpawn):
        self.spawns.append(x)


    def make_static_init(self) -> str:
        list_entries = ", ".join([s.make_static_init_entry() for s in self.spawns])

        return f"{BlockSpawn.typename()} {self.get_static_array_name()}[] = {{{list_entries}}};"

    def get_static_array_name(self):
        return f"{self.ctx_name}_block_spawns_data"


class BlockSpawns:
    def __init__(self, ctx_name: str) -> None:
        self.block_spawns = StaticBlockSpawnList(ctx_name)
        self.ctx_name = ctx_name

    def make_assignment(self) -> str:
        return ("{\n"
            f".block_spawns = {self.block_spawns.get_static_array_name()},"
            f".length = {len(self.block_spawns.spawns)},"
        "},\n")
        
