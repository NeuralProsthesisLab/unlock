""" Set your global parameters"""

import pygame
pygame.display.init()
import pygame.font; pygame.font.init()
pygame.mixer.init()

### MAIN SETTINGS ###
#dirSpeechMale   = '/Users/bgalbraith/Dropbox/BCIEnviroDemo/Male/'
dirSpeechMale   = '/Users/slorenz/Dropbox/Shared/BCIEnviroDemo/Male/'
fileSpeechList  = dirSpeechMale+'phrases.txt'
udpIP      = 'localhost'
udpPortClass    = 33445
udpPortClick    = 33446
udpPortData     = 33447
tSecs           = 4.0                         # 4.0 for HSD; 2.0 (or less ) for CCA
stimHz          = [12.0, 13.0, 14.0, 15.0]    # Stimulating frequencies
imgOffset       = 150                         # Amount to keep images away from window edge
nBoxes          = 5                           # number of boxes in one row or column
boxWid          = 100                         # grid box width
lineStk         = 1                           # Line stroke width
screenWid       = pygame.display.Info().current_w - 0  # Screen window width
screenHgt       = pygame.display.Info().current_h - 50 # Screen window height
gridFont        = pygame.font.SysFont("Helvetica", 18)     # Set the grid text font and size
tPause          = 500                     # CUE PERIOD PAUSE in milliseconds
flickRates      = [0.5/i for i in stimHz]

# RGB VALUE COLORS
rgb             = {'black': [0,0,0]}
rgb['white']    = [255,255,255]
rgb['iceblue']  = [179,223,245]
rgb['red']      = [204,61,0]
rgb['lineStkClr'] = [67,86,102]         # line stroke color

### INITIALIZATION SETTINGS ###
gLoc            = 0
data            = -1

# JUNK THAT SHOULD BE HOPEFULLY MOVED OUTTA HERE
allPacketsReceived = False
exitLoop        = False
classData       = 4
clickData       = 0
state_selector  = 4