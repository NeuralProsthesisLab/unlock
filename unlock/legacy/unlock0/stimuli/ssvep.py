import pyglet
import time
import array
from core import UnlockApplication
from math import cos, sin, radians

class SSVEP(UnlockApplication):

    name = "SSVEP"

    def __init__(self, screen, stimuli, trial_length=4.0,
                 rest_length=1.0):
        super(self.__class__, self).__init__(screen)
        self._stimuli = stimuli
        self.trial_length = trial_length
        self.rest_length = rest_length

        self.start()

    def reset(self):
        """
        Resets the stimulus counters
        """
        self._paused = False
        self._trial_time = 0
        self._rest_time = 0
        self._last_time = time.time()
        for stim in self._stimuli:
            stim.reset()

    def start(self):
        """
        Start displaying the stimuli
        """
        self.reset()
        self._running = True


    def stop(self):
        """
        Stop displaying the stimuli
        """
        for stim in self._stimuli:
            stim.stop()
        self._running = False

    def pause(self, duration):
        """
        Pause the stimulus display
        :param duration: number of seconds to pause
        """
        self.reset()
        self._rest_time = duration
        self._paused = True

    def changeFrequencies(self, freqs):
        """
        Change the frequencies of the four stimuli
        :param freqs: freqencies to change
        """
        for i, stimulus in enumerate(self._stimuli):
            stimulus.changeFrequency(freqs[i])
            self.reset()

    def update(self, dt, decision, selection):
        if not self._running:
            return

        self._trial_time += dt

        if self._paused:
            if self._trial_time >= self._rest_time:
                self.reset()
        else:
            if self._trial_time >= self.trial_length and self.rest_length > 0:
                self.pause(self.rest_length)
            else:
                for stim in self._stimuli:
                    stim.update(self._trial_time)


def generateCheckerboard(size, frequencies, duty_cycles, uneven, colors):
    """
    Creates a checkerboard image
    :param size: image width and height
    :param frequencies: spatial frequencies in the x and y directions
    :param duty_cycles: ratio of 'on' to 'off' in the x and y directions
    :param uneven: is the last cycle only half-width or -height?
    :param colors: 'on' and 'off' rgb values
    """
    width = size[0]
    height = size[1]

    w_frequency = frequencies[0]
    if uneven[0]:
        w_frequency -= 0.5
    h_frequency = frequencies[1]
    if uneven[1]:
        h_frequency -= 0.5

    w_duty_cycle = duty_cycles[0]
    h_duty_cycle = duty_cycles[1]

    color_on = colors[0]
    color_off = colors[1]

    cycle_width = int(width / w_frequency)
    cycle_on_width = int(cycle_width * w_duty_cycle + 0.5)
    cycle_off_width = cycle_width - cycle_on_width

    cycle_height = int(height / h_frequency)
    cycle_on_height = int(cycle_height * h_duty_cycle + 0.5)
    cycle_off_height = cycle_height - cycle_on_height

    line_on_string = (color_on * cycle_on_width +
                      color_off * cycle_off_width) * int(w_frequency)
    line_off_string = (color_off * cycle_on_width +
                       color_on * cycle_off_width) * int(w_frequency)
    if uneven[0]:
        line_on_string += color_on * cycle_on_width
        line_off_string += color_off * cycle_on_width

    w_extra = width - len(line_on_string)/3
    if w_extra > 0:
        if uneven[0]:
            line_on_string += color_on * w_extra
            line_off_string += color_off * w_extra
        else:
            line_on_string += color_off * w_extra
            line_off_string += color_on * w_extra

    buffer = (line_on_string * cycle_on_height +
              line_off_string * cycle_off_height) * int(h_frequency)
    if uneven[1]:
        buffer += line_on_string * cycle_off_height

    h_extra = width*height - len(buffer)/3
    if h_extra > 0:
        if uneven[1]:
            buffer += line_on_string * (h_extra / width)
        else:
            buffer += line_off_string * (h_extra / width)

    image = pyglet.image.ImageData(width, height, 'RGB',
                                  array.array('B',buffer).tostring())
    return image.get_texture().get_transform(flip_y=True)

class SSVEPStimulus():
    """ Loads the checkerboard image, positions on the screen, and handles
        flickering
    """
    def __init__(self, screen, rate, location, rotation=0, x_offset=0,
                 y_offset=0, width=600, height=100, x_freq=6, y_freq=1,
                 x_duty=0.5, y_duty=0.5, x_uneven=False, y_uneven=False,
                 color1=(0,0,0), color2=(255,255,255),
                 filename=None, filename_reverse=None):
        self.screen = screen
        self.flick_rate = 0.5/rate
        self.flick_time = 0

        self.x_offset = x_offset
        self.y_offset = y_offset

        pattern = None
        if filename is None:
            pattern = generateCheckerboard((width,height),(x_freq,y_freq),
                (x_duty,y_duty),(x_uneven,y_uneven),(color1,color2))
        else:
            pattern = pyglet.image.load(filename)
        pattern.anchor_x = pattern.width / 2
        pattern.anchor_y = pattern.height / 2

        self.image = pyglet.sprite.Sprite(pattern, batch=screen.batch)
        self.image.rotation = rotation

        angle = abs(radians(rotation))
        box_width = (self.image.width * cos(angle) +
                     self.image.height * sin(angle))
        box_height = (self.image.width * sin(angle) +
                      self.image.height * cos(angle))
        
        if location == "north":
            self.x = self.screen.width / 2
            self.y = self.screen.height - box_height / 2
        elif location == "south":
            self.x = self.screen.width / 2
            self.y = box_height / 2
        elif location == "west":
            self.x = box_width / 2
            self.y = self.screen.height / 2
        elif location == "east":
            self.x = self.screen.width - box_width / 2
            self.y = self.screen.height / 2
        elif location == "northwest":
            self.x = box_width / 2
            self.y = self.screen.height - box_height / 2
        elif location == "northeast":
            self.x = self.screen.width - box_width / 2
            self.y = self.screen.height - box_height / 2
        elif location == "southwest":
            self.x = box_width / 2
            self.y = box_height / 2
        elif location == "southeast":
            self.x = self.screen.width - box_width / 2
            self.y = box_height / 2
        elif location == "center":
            self.x = self.screen.width / 2
            self.y = self.screen.height / 2
        else:
            # this should raise an invalid anchor point exception
            self.x = 0
            self.y = 0
        self.image.x = self.x + self.x_offset
        self.image.y = self.y + self.y_offset
        self.image.visible = False

        self.image_reverse = None
        if filename_reverse is not None:
            pattern = pyglet.image.load(filename_reverse)
            pattern.anchor_x = pattern.width / 2
            pattern.anchor_y = pattern.height / 2
            self.image_reverse = pyglet.sprite.Sprite(pattern, batch=screen.batch)
            self.image_reverse.rotation = rotation
            self.image_reverse.x = self.x + self.x_offset
            self.image_reverse.y = self.y + self.y_offset
            self.image_reverse.visible = False


    def changeFrequency(self, freq):
        self.flick_rate = 0.5 / freq
        self.image.visible = False
        if self.image_reverse is not None:
            self.image_reverse.visible = True
        self.flick_time = 0


    def update(self, trial_time):
        if trial_time > self.flick_time:
            self.flick_time += self.flick_rate
            self.image.visible = not self.image.visible
            if self.image_reverse is not None:
                self.image_reverse.visible = not self.image_reverse.visible


    def reset(self):
        self.image.visible = False
        if self.image_reverse is not None:
            self.image_reverse.visible = True
        self.flick_time = 0

    def stop(self):
        self.image.visible = False
        if self.image_reverse is not None:
            self.image_reverse.visible = False