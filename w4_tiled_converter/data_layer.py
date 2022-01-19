
class DataLayer:
    STRUCT_NAME = "TileMap_DataLayer"
    def __init__(self, ctx_name, name, width, height, data) -> None:
        self.ctx_name = ctx_name
        self.name = name
        self.width = width
        self.height = height
        self.data = data

    def make_data_str(self):
        binary_data = [0 if d == 0 else 1 for d in self.data]
        out = []
        for i in range(0, len(binary_data), 8):
            b = binary_data[i:i+8]
            b.reverse() #lsb should be 0 index
            b_str = "".join([str(bit) for bit in b]) 
            out.append(f"0b{b_str}")
        return ", ".join(out) 

    def make_static_initalization(self):
        return f"const uint8_t {self.make_static_initalizer_name()}[] = {{{self.make_data_str()}}};"

    def make_assignment(self):
        return f"{{ .width={self.width}, .height={self.height}, .map={self.make_static_initalizer_name()} }},\n"

    def typename():
        return f"struct {DataLayer.STRUCT_NAME}"

    def make_static_initalizer_name(self):
        return f"{self.ctx_name}_{self.name}_map_data"