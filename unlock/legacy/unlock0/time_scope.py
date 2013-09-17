import pygame
from core import UnlockDisplay
from stimuli import SSVEP
from apps import TimeScope

# INITIALIZE DISPLAY
pygame.display.init()
screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
app_screen = screen.subsurface(pygame.Rect(100, 100, screen.get_width() - 200, screen.get_height() - 200))

# INITIALIZE STIMULUS
stimuli = []
stimulus = SSVEP(screen, stimuli)

app = TimeScope(app_screen, numchan=3, ylim=(-200,200))

## Initialize the display, attach the stimulus and initial app, and run
display = UnlockDisplay(screen, stimulus, app)
display.run()

pygame.quit()