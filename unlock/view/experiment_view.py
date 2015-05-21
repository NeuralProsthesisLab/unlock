import numpy as np
import pyglet

from unlock.view import UnlockView, PygletTextLabel, PygletSprite
from unlock.state import UnlockState
from unlock.state.experiment_state import TrialState, RestState, FeedbackQualitativeState


class ExperimentView(UnlockView):
    def __init__(self, model, canvas, normal_view, overlap_view):
        super(ExperimentView, self).__init__()
        self.model = model
        self.canvas = canvas
        self.normal_view = normal_view
        self.overlap_view = overlap_view
        cx, cy = canvas.center()
        self.text = PygletTextLabel(UnlockState(True), canvas, '', cx, cy)
        img = pyglet.image.load("view/resource/oddball.png")
        self.oddball = PygletSprite(UnlockState(True), canvas, img, cx, cy, 0)
        self.oddball.sprite.visible = False

        self.feedback = None
        self.feedback_mask = np.tile(np.array([0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.uint8), (4,))

    def create_feedback(self, score):
        cx, cy = self.canvas.center()
        r = 60
        color = self.feedback_mask * score
        self.feedback = self.canvas.batch.add(16, pyglet.gl.GL_QUADS, None,
                                              ('v2f', (cx, cy, cx+r, cy+r, cx+2*r, cy, cx+r, cy-r,
                                                       cx, cy, cx+r, cy-r, cx, cy-2*r, cx-r, cy-r,
                                                       cx, cy, cx-r, cy-r, cx-2*r, cy, cx-r, cy+r,
                                                       cx, cy, cx-r, cy+r, cx, cy+2*r, cx+r, cy+r)),
                                              ('c3B', color))

    def clear_feedback(self):
        self.feedback.delete()
        self.feedback = None

    def render(self):
        state = self.model.get_state()
        if state is not None:
            self.text.label.text = state.label
            self.text.label.font_size = state.size
            color = getattr(state, 'color', (255, 255, 255, 255))
            self.text.label.color = color
            pos = getattr(state, 'position', (0.5, 0.5))
            self.text.label.x = self.canvas.width * pos[0]
            self.text.label.y = self.canvas.height * pos[1]
            if state is FeedbackQualitativeState:
                self.create_feedback(self.model.get_feedback_score())
            elif state is RestState:
                self.clear_feedback()
        for view in self.overlap_view:
            view.render()
        for view in self.normal_view:
            view.render()
        oddball = self.model.get_oddball_state()
        if oddball is not None:
            self.oddball.sprite.visible = oddball[0]
            self.oddball.sprite.set_position(*oddball[1])
            self.oddball.sprite.color = oddball[2]
            self.oddball.sprite.scale = oddball[3]

class ExperimentTrainerView(ExperimentView):
    def __init__(self, model, canvas, normal_view, overlap_view):
        super(ExperimentTrainerView, self).__init__(model, canvas, normal_view, overlap_view)
        self.feedback_mask = np.array([0, 1, 1])

    def create_feedback(self, cue):
        cx, cy = self.canvas.center()
        radius = 60
        offset = 210
        if cue == 0:
            self.feedback = self.canvas.batch.add(4, pyglet.gl.GL_QUADS, None,
                                                  ('v2f', (cx, cy + offset + radius,
                                                           cx + radius, cy + offset,
                                                           cx, cy + offset - radius,
                                                           cx - radius, cy + offset)),
                                                  ('c3B', (0, 0, 0)*4))
        elif cue == 1:
            self.feedback = self.canvas.batch.add(4, pyglet.gl.GL_QUADS, None,
                                                  ('v2f', (cx, cy - offset - radius,
                                                           cx + radius, cy - offset,
                                                           cx, cy - offset + radius,
                                                           cx - radius, cy - offset)),
                                                  ('c3B', (0, 0, 0)*4))
        elif cue == 2:
            self.feedback = self.canvas.batch.add(4, pyglet.gl.GL_QUADS, None,
                                                  ('v2f', (cx - offset - radius, cy,
                                                           cx - offset, cy + radius,
                                                           cx - offset + radius, cy,
                                                           cx - offset, cy - radius)),
                                                  ('c3B', (0, 0, 0)*4))
        elif cue == 3:
            self.feedback = self.canvas.batch.add(4, pyglet.gl.GL_QUADS, None,
                                                  ('v2f', (cx + offset + radius, cy,
                                                           cx + offset, cy + radius,
                                                           cx + offset - radius, cy,
                                                           cx + offset, cy - radius)),
                                                  ('c3B', (0, 0, 0)*4))

    def render(self):
        state = self.model.get_state()
        if state is not None:
            self.text.label.text = state.label
            self.text.label.font_size = state.size
            color = getattr(state, 'color', (255, 255, 255, 255))
            self.text.label.color = color
            pos = getattr(state, 'position', (0.5, 0.5))
            self.text.label.x = self.canvas.width * pos[0]
            self.text.label.y = self.canvas.height * pos[1]
            if not self.model.initial_phase:
                if state.__base__ is TrialState:
                    self.create_feedback(self.model.cue)
                elif state is RestState:
                    self.clear_feedback()
        for view in self.overlap_view:
            view.render()
        for view in self.normal_view:
            view.render()
        if self.feedback is not None:
            self.feedback.colors[0:3] = self.feedback_mask * self.model.get_feedback_score()
