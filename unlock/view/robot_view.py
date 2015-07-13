from unlock.view import UnlockView


class RobotView(UnlockView):
    def __init__(self, model, canvas):
        super(RobotView, self).__init__()
        self.model = model
        self.canvas = canvas
        cx, cy = self.canvas.center()
        self.x = cx - 320/2
        self.y = cy - 240/2
        if not self.model.manual:
            self.obj1 = self.drawRect(cx - 360 - 90 - 40, cy - 90,
                                  30, 180,
                                  canvas.batch, color=(0,255,0),
                                  fill=True)
            self.obj2 = self.drawRect(cx - 90, cy + 360 + 90 + 10,
                                  180, 30,
                                  canvas.batch, color=(0,0,255),
                                  fill=True)
            self.obj3 = self.drawRect(cx + 360 + 90 + 10, cy - 90,
                                  30, 180,
                                  canvas.batch, color=(255,0,0),
                                  fill=True)

    def render(self):
        if self.model.frame is not None:
            self.model.frame.blit(self.x, self.y)
