from unlock.view import UnlockView


class RobotView(UnlockView):
    def __init__(self, model, canvas):
        super(RobotView, self).__init__()
        self.model = model
        self.canvas = canvas
        cx, cy = self.canvas.center()
        self.x = cx - 320/2
        self.y = cy - 240/2

    def render(self):
        self.model.frame.blit(self.x, self.y)
