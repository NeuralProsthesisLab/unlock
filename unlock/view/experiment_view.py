from unlock.view import UnlockView, PygletTextLabel
from unlock.state import UnlockState


class ExperimentView(UnlockView):
    def __init__(self, model, canvas):
        super(ExperimentView, self).__init__()
        self.model = model
        self.canvas = canvas
        cx, cy = canvas.center()
        self.text = PygletTextLabel(UnlockState(True), canvas, '', cx, cy)

    def render(self):
        state = self.model.get_state()
        if state is not None:
            self.text.label.text = state.label
            self.text.label.font_size = state.size