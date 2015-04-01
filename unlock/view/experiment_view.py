import numpy as np

from unlock.view import UnlockView, PygletTextLabel
from unlock.state import UnlockState


class ExperimentView(UnlockView):
    CueState = 0
    PrepState = 1
    TrialState = 2
    FeedbackState = 3
    RestState = 4

    def __init__(self, model, canvas):
        super(ExperimentView, self).__init__()
        self.model = model
        self.canvas = canvas
        cx, cy = canvas.center()
        self.text = PygletTextLabel(UnlockState(True), canvas, '', cx, cy, size=200)
        self.cues = ('\u21e7', '\u21e9', '\u21e6', '\u21e8')  # outline arrows
        self.feedbacks = ('\u2714', '\u2718')  # check, x

    def render(self):
        state = self.model.get_state()
        if state is not None:
            if state == ExperimentView.CueState:
                self.text.label.text = np.random.choice(self.cues)
                self.text.label.font_size = 200
            elif state == ExperimentView.FeedbackState:
                self.text.label.text = np.random.choice(self.feedbacks)
                self.text.label.font_size = 120
            else:
                self.text.label.text = ''