from unlock.state import UnlockState
from unlock.view import UnlockView, PygletTextLabel


class EyeBlinkCalibrationView(UnlockView):
    def __init__(self, model, canvas):
        super(EyeBlinkCalibrationView, self).__init__()
        self.model = model
        self.canvas = canvas
        cx, cy = canvas.center()
        self.text = PygletTextLabel(UnlockState(state=True), canvas, '', cx, cy)

    def render(self):
        state = self.model.get_state()
        if state is not None:
            self.text.label.text = "x: %d, y: %d" % (state[0], state[1])
