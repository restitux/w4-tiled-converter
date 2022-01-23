class TextTrigger:
    STRUCT_NAME = "TileMap_TextTrigger"

    def __init__(
        self, id: int, x: int, y: int, width: int, height: int, string: str, ability_pickup: int
    ) -> None:
        self.id = id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.string = string
        self.id = id
        self.ability_pickup = int(ability_pickup) if not ability_pickup is None else -1

    def make_static_init_entry(self) -> str:
        return f'({TextTrigger.typename()}) {{.id = {self.id}, .x={self.x}, .y={self.y},  .width={self.width}, .height={self.height}, .string = "{self.string}", .length={len(self.string)}, .ability_pickup={self.ability_pickup}}}'

    def typename() -> str:
        return f"struct {TextTrigger.STRUCT_NAME}"


class StaticTextTriggerList:
    def __init__(self, ctx_name: str) -> None:
        self.triggers = []
        self.ctx_name = ctx_name

    def add_trigger(self, x: TextTrigger):
        self.triggers.append(x)

    def make_static_init(self) -> str:
        list_entries = ", ".join([s.make_static_init_entry() for s in self.triggers])

        return f"{TextTrigger.typename()} {self.get_static_array_name()}[] = {{{list_entries}}};"

    def get_static_array_name(self):
        return f"{self.ctx_name}_text_triggers_data"


class TextTriggers:
    def __init__(self, ctx_name: str) -> None:
        self.text_triggers = StaticTextTriggerList(ctx_name)
        self.ctx_name = ctx_name

    def make_assignment(self) -> str:
        return (
            "{\n"
            f".text_triggers = {self.text_triggers.get_static_array_name()},"
            f".length = {len(self.text_triggers.triggers)},"
            "},\n"
        )
