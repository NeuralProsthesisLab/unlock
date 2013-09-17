from apps.grid._textwrap import *
from core import UnlockApplication
import pygame.font; pygame.font.init()
import numpy as np
import sys

# Check OS for speech synthesizer import
speechOS = sys.platform
if speechOS == 'win32':
	pass
    # import speech
else:
    import os

class GridStatic(UnlockApplication):

    name = "Grid Speak Static"

    def __init__(self,screen):
        super(self.__class__, self).__init__(screen)
        self.screen   = screen
        self.speechOS = speechOS

        # IMPORTANT SETTINGS
        self.nBoxes         = 11
        self.box_size       = 50
        font_size           = 6
        filelist            = ['feelings','food','nonurgent','smalltalk','urgent']
        self.currentTopic   = 'singlelist'

        # other settings/variables
        self.rgb            = {'black': [0,0,0]}
        self.rgb['white']   = [255,255,255]
        self.rgb['iceblue'] = [179,223,245]
        self.rgb['red']     = [204,61,0]
        self.rgb['lineStkClr'] = [67,86,102]
        self.radius     = (self.nBoxes-1)/2
        self.cursor     = [0,0]
        self.lineStk    = 1
        self.gridFont   = pygame.font.SysFont("Helvetica", font_size) # Set the grid text font and size
        self.gridLen    = self.nBoxes*self.box_size    # The total pixel length of a grid
        self.x_center   = (self.screen.get_width()-self.box_size)/ 2
        self.y_center   = (self.screen.get_height()-self.box_size)/2
        self.xyGridPos  = np.zeros((self.nBoxes+1,2))  # 6x2 matrix of x-y topleft coords
        idx=0
        for edge in range(-self.radius,self.radius+2): # Creates 6 lines from [-2,4]
            self.xyGridPos[idx,0] = self.x_center + edge*self.box_size
            self.xyGridPos[idx,1] = self.y_center + edge*self.box_size
            idx+=1

        # Text/phrase stuff
        filePhraseList      = "resource/phrases2_"
#        filePhraseList      = "resource/phrases_"
        self.phrases        = {}
        self.phrases[self.currentTopic] = []
        for plist in filelist:
            fd = open(filePhraseList + plist + '.txt', 'r')
            lines = fd.readlines()
            for line in lines:
                el=line.strip().split('\t')
                self.phrases[self.currentTopic].append(el[0])
            fd.close()
        self.phrases[self.currentTopic].insert((self.nBoxes**2)/2,'MAIN MENU') # Add MAIN MENU as the center grid box item text

    def drawGridLines(self):
        for i in range(self.nBoxes+1):
            # Horizontal stripes
            pygame.draw.line(self.screen, self.rgb['lineStkClr'],\
                (self.xyGridPos[0,0],self.xyGridPos[i,1]),\
                (self.xyGridPos[0,0]+self.gridLen,self.xyGridPos[i,1]), self.lineStk)
            # Vertical stripes
            pygame.draw.line(self.screen, self.rgb['lineStkClr'],\
                (self.xyGridPos[i,0],self.xyGridPos[0,1]),\
                (self.xyGridPos[i,0],self.xyGridPos[0,1]+self.gridLen), self.lineStk)

    def drawSpeechText(self):
        idx=0
        for i in range(self.nBoxes):
            for j in range(self.nBoxes):
                text = self.phrases[self.currentTopic][idx]
                textRect = pygame.Rect((self.xyGridPos[j,0],self.xyGridPos[i,1],self.box_size,self.box_size))
                textRendered = render_textrect(text,self.gridFont,textRect,self.rgb['white'],self.rgb['black'], 1)
                self.screen.blit(textRendered, textRect.topleft)
                idx+=1

    def drawBox(self):
        pygame.draw.rect(self.screen, (67,86,102),
            (self.x_center + self.cursor[0] * self.box_size,
             self.y_center - self.cursor[1] * self.box_size,
             self.box_size, self.box_size), 0)

    def gridNumber(self):
        # location in x-y coordinates
        for i in range(self.nBoxes):
            if self.cursor[0] == (-self.radius) + i:
                x = i
            if self.cursor[1] == self.radius - i:
                y = i
        # location in phrase list
        self.phraseListNum = x + self.nBoxes*y

    def selectSwitch(self):
        if self.cursor == [0,0]:
            self.close()
        else:
            # Get the current grid element number
            self.gridNumber()
            # Mac or Windows speech synthesizer output
            if self.speechOS == 'win32':
				pass
                # speech.say(self.phrases[self.currentTopic][self.phraseListNum])
            else:
                os.system('say ' + self.phrases[self.currentTopic][self.phraseListNum])

    def update(self, decision, selection):
        # DECISION (move)
        if decision == 1 and self.cursor[1] < self.radius:
            self.cursor[1] += 1
        elif decision == 2 and self.cursor[1] > -self.radius:
            self.cursor[1] -= 1
        elif decision == 3 and self.cursor[0] > -self.radius:
            self.cursor[0] -= 1
        elif decision == 4 and self.cursor[0] < self.radius:
            self.cursor[0] += 1
        # SELECTION (click)
        if selection:
            self.selectSwitch()

    def draw(self):
        self.drawGridLines()
        self.drawBox()
        self.drawSpeechText()