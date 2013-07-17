from unlock.core import UnlockApplication


class MSpeller(UnlockApplication):
    """
    An m-sequence speller BCI application based on Spuler at al (2012).
    """
    name = "M-Speller"

    def __init__(self, screen, rows, cols, labels, sequence):
        super(self.__class__, self).__init__(screen)
        self.rows = rows + 2
        self.cols = cols + 2
        self.size = rows * cols
        self.labels = labels
        self.sequence = sequence
        self.length = len(sequence)
        self.time = 0
        self.cursor = 0
        self.period = 1/60.0
        self.feedback = False
        self.feedback_time = 0.150

        self.buffer = screen.drawText('_', 20, screen.height - 50)
        self.buffer.anchor_x = 'left'

        self.target_width = screen.width / self.cols
        self.target_height = (screen.height - 100) / self.rows

        self.targets = []
        idx = self.size - self.cols + 1
        for i in xrange(self.rows):
            for j in xrange(self.cols):
                x = (j + 0.5) * self.target_width
                y = ((self.rows - i) - 0.5) * self.target_height
                a = 255*self.sequence[idx*2]
                text = labels[idx]
                if i in [0, self.rows - 1] or j in [0, self.cols - 1]:
                    text = ''
                label = screen.drawText(text, x, y,
                                        color=(127, 127, 127, 255))
                target = screen.drawRect(x - 0.5*self.target_width,
                                         y - 0.5*self.target_height,
                                         self.target_width, self.target_height,
                                         fill=True, color=(a, a, a))
                self.targets.append((target, label, idx))
                idx += 1
                if idx >= self.size:
                    idx -= self.size
            idx -= 2

    def update(self, dt, decision, selection):
        self.time += dt

        if self.feedback:
            if self.time >= self.feedback_time:
                self.feedback = False
                self.time = 0
            return

        if self.time < self.period:
            return
        self.time = 0
        self.cursor += 1
        if self.cursor >= self.length:
            self.cursor = 0
        for target in self.targets:
            idx = self.cursor + 2*target[2]
            if idx >= self.length:
                idx -= self.length
            a = 255*self.sequence[idx]
            target[0].colors = (a, a, a)*4
            #target[0].colors[:3] = (a,a,a) <- interesting visual effect

        if decision is not None:
            symbol = self.labels[decision-1]
            if symbol == '5':
                text = self.buffer.text[:-2] + '_'
            else:
                text = self.buffer.text[:-1] + symbol + '_'
            self.buffer.text = text
            self.feedback = True
            x = (decision - 1) % (self.cols - 2)
            y = (decision - 1) / (self.cols - 2)
            idx = (y+1)*self.cols + x + 1
            self.targets[idx][0].colors = (255, 255, 0)*4
