from core import UnlockApplication

class Dashboard(UnlockApplication):

    name = "Unlock Dashboard"
    icon = "unlock.png"

    app_order = [(0,1),(1,0),(0,-1),(-1,0),
                 (1,1),(1,-1),(-1,-1),(-1,1)]
    icon_size = (128,128)

    def __init__(self, screen):
        super(self.__class__, self).__init__(screen)


        self.installed_apps = 0
        self.cursor = (0,0)

        cx, cy = self.screen.get_center()
        ## x_offset (int) -> { y_offset (int) -> app }
        ## offsets are from the origin (0,0) at center
        self.marker = self.screen.drawRect(cx-64, cy-64, 128, 128)
        icon = self.screen.loadSprite(self.resource_path + self.icon, cx, cy)
        self.grid = {self.cursor: {'app':self, 'icon':icon}}
    @override
    def on_attach(self, app):
        """
        Update the dashboard to reflect the new app.
        """
        super(self.__class__, self).on_attach(app)
        
        place = self.app_order[self.installed_apps]
        cx, cy = self.screen.get_center()
        ix = cx + place[0] * self.icon_size[0]
        iy = cy + place[1] * self.icon_size[1]
        try:
            icon = self.screen.loadSprite(app.resource_path + app.icon, ix, iy)
        except AttributeError:
            icon = self.screen.drawText(app.name, ix, iy, size=18)
        self.grid[place] = {'app': app, 'icon': icon}
        self.installed_apps += 1

    def update(self, dt, decision, selection):
        if decision is not None:
            move = [0,0]
            if decision == 1:
                move[1] = 1
            elif decision == 2:
                move[1] = -1
            elif decision == 3:
                move[0] = -1
            elif decision == 4:
                move[0] = 1

            new_cursor = (self.cursor[0] + move[0], self.cursor[1] + move[1])
            if new_cursor in self.grid:
                self.cursor = new_cursor
                self.moveBox(self.marker, move[0], move[1])

        if selection:
            if self.cursor in self.grid:
                self.open(self.grid[self.cursor]['app'])

    def moveBox(self, box, x_step, y_step):
        """Moves box by n x_step or y_step. x_step and y_step are
         defined by the height of the grid elements"""
        if x_step:
            box.vertices[::2] = [i + int(x_step)*self.icon_size[0] for i in
                                 box.vertices[::2]]
        if y_step:
            box.vertices[1::2] = [i + int(y_step)*self.icon_size[1] for i in
                                  box.vertices[1::2]]