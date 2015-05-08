import pyglet

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
            pos = getattr(state, 'position', (0.5, 0.5))
            self.text.label.x = self.canvas.width * pos[0]
            self.text.label.y = self.canvas.height * pos[1]
        for view in self.overlap_view:
            view.render()
        for view in self.normal_view:
            view.render()


class ExperimentTrainerView(ExperimentView):
    def __init__(self, model, canvas, normal_view, overlap_view):
        super(ExperimentTrainerView, self).__init__(model, canvas, normal_view, overlap_view)
        color0 = (0, 0, 0)
        color1 = (0, 0, 0)

        cx, cy = canvas.center()
        self.feedbacks = [
            canvas.batch.add(4, pyglet.gl.GL_QUADS, None,
                             ('v2f', (cx, cy + 270,
                                      cx + 60, cy + 210,
                                      cx, cy + 150,
                                      cx - 60, cy + 210)),
                             ('c3B', color1+color0*3)),
            canvas.batch.add(4, pyglet.gl.GL_QUADS, None,
                             ('v2f', (cx, cy - 270,
                                      cx + 60, cy - 210,
                                      cx, cy - 150,
                                      cx - 60, cy - 210)),
                             ('c3B', color1+color0*3)),
            canvas.batch.add(4, pyglet.gl.GL_QUADS, None,
                             ('v2f', (cx - 270, cy,
                                      cx - 210, cy + 60,
                                      cx - 150, cy,
                                      cx - 210, cy - 60)),
                             ('c3B', color1+color0*3)),
            canvas.batch.add(4, pyglet.gl.GL_QUADS, None,
                             ('v2f', (cx + 270, cy,
                                      cx + 210, cy + 60,
                                      cx + 150, cy,
                                      cx + 210, cy - 60)),
                             ('c3B', color1+color0*3)),
        ]

    def render(self):
        super(ExperimentTrainerView, self).render()
        for feedback, score in zip(self.feedbacks, self.model.decoder_scores):
            feedback.colors[1:3] = [score, score]