from unlock.view import UnlockView


class EyeBlinkCalibrationView(UnlockView):
    def __init__(self, model, canvas):
        super(EyeBlinkCalibrationView, self).__init__()
        self.model = model
        self.canvas = canvas

    def render(self):
        pass
