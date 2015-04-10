from unlock.view import UnlockView, PygletTextLabel
from unlock.state import UnlockState

class ExperimentView(UnlockView):
    def __init__(self, model, canvas, normal_view, overlap_view):
        super(ExperimentView, self).__init__()
        self.model = model
        self.canvas = canvas
        self.normal_view = normal_view
        self.overlap_view = overlap_view
        cx, cy = canvas.center()
        self.text = PygletTextLabel(UnlockState(True), canvas, '', cx, cy)

    def render(self):
        state = self.model.get_state()
        if state is not None:
            self.text.label.text = state.label
            self.text.label.font_size = state.size
            color = getattr(state, 'color', (255, 255, 255, 255))
            self.text.label.color = color
        for view in self.overlap_view:
            view.render()
        for view in self.normal_view:
            view.render()