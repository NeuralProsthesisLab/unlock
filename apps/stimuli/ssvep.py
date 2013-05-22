import pyglet
import time
import array
import socket
from core import UnlockApplication
from math import cos, sin, radians

class SSVEP(UnlockApplication):

    name = "SSVEP"

    def __init__(self, screen, stimuli, trial_length=4.0,
                 rest_length=1.0, trigger_addr=None):
        super(SSVEP, self).__init__(screen)
        self._stimuli = stimuli
        self.trial_length = trial_length
        self.rest_length = rest_length

        self.trigger_addr = trigger_addr
        if trigger_addr is not None:
            self._trigger_socket = socket.socket(type=socket.SOCK_DGRAM)
            self._trigger_socket.settimeout(0.001)
            for stim in self._stimuli:
                stim.send_trigger = True

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
        :param freqs: frequencies to change
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
                send_trigger = False
                for stim in self._stimuli:
                    send_trigger |= bool(stim.update(self._trial_time))
                if self.trigger_addr is not None and send_trigger:
                    self._trigger_socket.sendto('1',self.trigger_addr)


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
    """
    An SSVEP stimulus is characterized by a repeating pattern of flickering
    images, typically rectangular checkerboards. In some cases, a single image
    is flashed on and off, while in others, two images toggle back and forth.

    This class provides a means to specify the properties of a checkerboard
    stimulus or provide custom stimulus images. It handles the display and
    state management of the stimulus.

    Note: As this is intended to only be used in conjunction with the general
    SSVEP Unlock Application, it may better to have a generator function
    inside SSVEP rather than require users to explicitly instantiate objects
    only to pass them immediately to an SSVEP instance.
    """
    def __init__(self, screen, rate, location, rotation=0, x_offset=0,
                 y_offset=0, width=600, height=100, x_freq=6, y_freq=1,
                 x_duty=0.5, y_duty=0.5, x_uneven=False, y_uneven=False,
                 color1=(0,0,0), color2=(255,255,255), filename=None,
                 filename_reverse=None, sequence=(1,0)):
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
            if filename_reverse is True:
                pattern = generateCheckerboard((width,height),(x_freq,y_freq),
                    (x_duty,y_duty),(x_uneven,y_uneven),(color2,color1))
            else:
                pattern = pyglet.image.load(filename_reverse)
            pattern.anchor_x = pattern.width / 2
            pattern.anchor_y = pattern.height / 2
            self.image_reverse = pyglet.sprite.Sprite(pattern, batch=screen.batch)
            self.image_reverse.rotation = rotation
            self.image_reverse.x = self.x + self.x_offset
            self.image_reverse.y = self.y + self.y_offset
            self.image_reverse.visible = False

        # for m-sequence support
        self.sequence = sequence
        self.sequence_index = 0
        self.send_trigger = False
        self.trigger = False


    def changeFrequency(self, freq):
        """
        Allows for the flicker frequency of the stimulus to be changed at
        runtime.
        """
        self.flick_rate = 0.5 / freq
        self.reset()


    def update(self, trial_time):
        """
        Updates the stimulus image to the next state in the presentation
        sequence if the elapsed trial time exceeds the next flicker time.

        If a trigger signal has been requested, a value of True is returned
        at the start of the state sequence.
        """
        if trial_time > self.flick_time:
            self.flick_time += self.flick_rate
            self.sequence_index += 1
            if self.sequence_index >= len(self.sequence):
                self.sequence_index = 0
                if self.send_trigger:
                    self.trigger = True
            self.image.visible = bool(self.sequence[self.sequence_index])
            if self.image_reverse is not None:
                self.image_reverse.visible = not bool(self.sequence[self.sequence_index])
            if self.trigger:
                self.trigger = False
                return True


    def reset(self):
        """
        Resets the stimulus flicker timer to 0.
        Displays the reversal stimulus image if defined.
        """
        self.image.visible = False
        if self.image_reverse is not None:
            self.image_reverse.visible = True
        self.flick_time = 0

    def stop(self):
        """
        Hides all stimulus images.
        """
        self.image.visible = False
        if self.image_reverse is not None:
            self.image_reverse.visible = False

class DefaultSSVEP(SSVEP):
    """
    Convenience class for quickly generating the default stimuli setup for
    four-choice Harmonic Sum Decision SSVEP.
    """
    def __init__(self, screen):
        stimuli = [
            SSVEPStimulus(screen, 12.0, 'north'),
            SSVEPStimulus(screen, 13.0, 'south'),
            SSVEPStimulus(screen, 14.0, 'west', rotation=90),
            SSVEPStimulus(screen, 15.0, 'east', rotation=90),
            ]
        super(DefaultSSVEP, self).__init__(screen, stimuli)