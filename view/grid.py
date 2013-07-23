from unlock.model import UnlockModel


class Grid(UnlockView):
    #icons = (path, name)
    def __init__(self, model, canvas, icons, center_x, center_y, rect_xoffset=64, rect_yoffset=64,
                 icon_width=128, icon_length=128):
        super(Grid, self).__init__()
        self.icon_width = icon_width
        self.icon_length = icon_length
        
        self.controller_count = 0
        self.cursor = (0,0)
        self.grid = {}
        self.vertex_list = self.drawRect(center_x-rect_xoffset, center_y-rect_yoffset,
                                            self.icon_width, self.icon_length)
        index = 0
        model = UnlockModel(state=True)
        for icon_path, icon_name in icons:
            x_offset, y_offset = self.model.ordering[index]
            icon_x = center_x + x_offset * self.icon_width
            icon_y = center_y + y_offset * self.icon_length
            try:
                icon_widget = PygletSprite.create_image_sprite(model, canvas, icon_path, icon_x, icon_y)
            except AttributeError:
                icon_widget = self.screen.drawText(icon_name, icon_x, icon_y, size=18)
            self.icon_widgets.append(icon_widget)
            index += 0
            
    def render(self):
        state = self.model.get_state()
        if not state:
            return
            
        if state.change == GridStateChange.XChange:
            self.marker.vertices[::2] = [i + int(state.step_value)*self.icon_width for i in self.marker.vertices[::2]]
        elif state.change == GridStateChange.YChange:
            self.marker.vertices[1::2] = [i + int(state.step_value)*self.icon_length for i in self.marker.vertices[1::2]]
            
            