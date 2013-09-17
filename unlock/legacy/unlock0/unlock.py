import pygame
from core import UnlockDisplay
from stimuli import SSVEP, SSVEPStimulus
import argparse
import serial

# COMMAND LINE ARGUMENTS
parser = argparse.ArgumentParser(description="Main Unlock Program")
parser.add_argument("--mode",action='store',default="experiments",help="Mode for operation [experiments | apps]")
parser.add_argument("--exp_app",action='store',default="udlr",help="App to run, if mode == experiments")
parser.add_argument("--subjectNumber", action='store',default="expdemo",help="Subject Identifier")
parser.add_argument("--fileLocation", action='store',default="",help="Directory to write data files to")
args = parser.parse_args()

# EXPERIMENT OR APP MODE SWITCH
main_mode = args.mode           # Options: 1) experiments, 2) apps
experiment_app = args.exp_app   # Options: 1) alpha, 2) eog, 3) sweep, 4) udlr, 5) static grid, 6) hierarchy grid
ssvep_mode = "led"              # Options: 1) monitor, 2) led

# INITIALIZE DISPLAY
pygame.display.init()
#screen = pygame.display.set_mode((600,400))
screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
app_screen = screen.subsurface(pygame.Rect(100, 100, screen.get_width() - 200, screen.get_height() - 200))

# INITIALIZE STIMULUS
stimuli = [
    SSVEPStimulus(screen, 12.0, 'north'),
    SSVEPStimulus(screen, 13.0, 'south'),
    SSVEPStimulus(screen, 14.0, 'west', rotation=90),
    SSVEPStimulus(screen, 15.0, 'east', rotation=90),
    ]
stimulus = SSVEP(screen, stimuli)

## Experiment mode setup
if main_mode == "experiments":
    if experiment_app == "alpha":
        from experiments.sean import Alpha
        app = Alpha(app_screen, subjectNumber=args.subjectNumber, fileLocation=args.fileLocation)
    elif experiment_app == "eog":
        from experiments.sean import EOG
        app = EOG(app_screen, subjectNumber=args.subjectNumber, fileLocation=args.fileLocation)
    elif experiment_app == "sweep":
        stimulus = SSVEP(screen,stimuli,trial_length=5.0,rest_length=0.0)
        from experiments.sean import Sweep
        app = Sweep(app_screen, subjectNumber=args.subjectNumber, fileLocation=args.fileLocation)
    elif experiment_app == "udlr":
        if ssvep_mode == "led":
            ser = serial.Serial('/dev/ttyACM0',9600)
#            ser = serial.Serial('/dev/cu.usbmodem411',9600)
            ser.write('0')
        elif ssvep_mode == "monitor":
            stimulus = SSVEP(screen,stimuli,trial_length=4.0,rest_length=0.0)
        from experiments.sean import UDLR
        app = UDLR(app_screen, subjectNumber=args.subjectNumber, fileLocation=args.fileLocation)
    elif experiment_app == "static grid":
        stimulus = SSVEP(screen,stimuli,trial_length=4.0,rest_length=0.0)
        from experiments.sean import GridStaticExperimentNoText
        app = GridStaticExperimentNoText(app_screen, subjectNumber=args.subjectNumber, fileLocation=args.fileLocation)
    elif experiment_app == "hierarchy grid":
        stimulus = SSVEP(screen,stimuli,trial_length=4.0,rest_length=0.0)
        from experiments.sean import GridHierarchyExperimentNoText
        app = GridHierarchyExperimentNoText(app_screen, subjectNumber=args.subjectNumber, fileLocation=args.fileLocation)

## App mode setup
if main_mode == "apps":
    stimulus = SSVEP(screen,stimuli,trial_length=4.0,rest_length=0.0)
    from apps import dashboard, GridHierarchy
    app = dashboard(app_screen)
    app.attach(GridHierarchy(app_screen))

## Initialize the display, attach the stimulus and initial app, and run
display = UnlockDisplay(screen, stimulus, app)
display.run()

## Quit things
pygame.quit()
if ssvep_mode == "led":
    ser.write('0')
    ser.close()
