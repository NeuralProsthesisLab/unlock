from core import UnlockApplication

class Dashboard(UnlockApplication):

    name = "Unlock Dashboard"

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
        self.grid = {self.cursor: {'app':self, 'icon':None}}
        self.marker = self.screen.drawText('+', cx, cy)

#        self.image_size = self.grid[1][0].get_width()
#        self.box_padding = 10
#        self.box_size = self.image_size + 2 * self.box_padding
#        self.x_center  = (self.screen.get_width() - self.box_size) / 2
#        self.y_center  = (self.screen.get_height() - self.box_size) / 2

#    def onReturn(self, kwargs):
#        self.controller.current_stimulus.start()
#
#    def drawStrokeBox(self):
#        pygame.draw.rect(self.screen, (67,86,102),
#            (self.x_center + self.cursor[0] * self.box_size,
#             self.y_center - self.cursor[1] * self.box_size,
#             self.box_size, self.box_size), 1)

    def on_attach(self, app):
        """
        Update the dashboard to reflect the new app.
        """
        place = self.app_order[self.installed_apps]

        cx, cy = self.screen.get_center()
        ix = cx + place[0] * self.icon_size[0]
        iy = cy + place[1] * self.icon_size[1]
        icon = self.screen.loadSprite(app.icon, ix, iy)
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
                self.marker.x += move[0] * self.icon_size[0]
                self.marker.y += move[1] * self.icon_size[1]

        if selection:
            if self.cursor in self.grid:
                self.open(self.grid[self.cursor]['app'])