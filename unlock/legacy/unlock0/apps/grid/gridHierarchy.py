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

class GridHierarchy(UnlockApplication):

    name = "Grid Speak Hierarchy"

    def __init__(self,screen):
        super(self.__class__, self).__init__(screen)
        self.screen   = screen
        self.speechOS = speechOS

        # IMPORTANT SETTINGS
        self.nBoxes     = 5
        self.box_size   = 100
        font_size       = 18
        filelist        = ['dashboard','feelings','food','nonurgent','smalltalk','urgent']
        self.phraseTopics = ['MAIN MENU','Feelings & Emotions','Eating & Drinking','Non-Urgent Requests', \
                             'Small Talk','Urgent Requests']

        # other settings/variables
        self.rgb             = {'black': [0,0,0]}
        self.rgb['white']    = [255,255,255]
        self.rgb['iceblue']  = [179,223,245]
        self.rgb['red']      = [204,61,0]
        self.rgb['lineStkClr'] = [67,86,102]         # line stroke color
        self.radius     = (self.nBoxes-1)/2
        self.cursor     = [0,0]
        self.lineStk    = 1
        self.gridFont   = pygame.font.SysFont("Arial", font_size)
        self.gridLen    = self.nBoxes*self.box_size    # The total pixel length of a grid
        self.x_center   = (self.screen.get_width()-self.box_size)/ 2
        self.y_center   = (self.screen.get_height()-self.box_size)/2
        self.xyGridPos  = np.zeros((self.nBoxes+1,2))  # 6x2 matrix of x-y topleft coords
        idx=0
        for edge in range(-self.radius,self.radius+2): # Creates 6 lines from [-2,4]
            self.xyGridPos[idx,0] = self.x_center + edge*self.box_size
            self.xyGridPos[idx,1] = self.y_center + edge*self.box_size
            idx+=1

        # load phrase topic lists
        filePhraseList    = "resource/phrases2_"
        self.currentTopic = self.phraseTopics[0]
        self.phrases      = {}
        for plist in filelist:
            self.phrases[plist] = []
            fd = open(filePhraseList + plist + '.txt', 'r')
            lines = fd.readlines()
            for line in lines:
                el=line.strip().split('\t')
                self.phrases[plist].append(el[0])
            fd.close()
            if plist is not 'dashboard':
                self.phrases[plist].insert(12,'MENU') # Add MENU to the center of each list!
        for i in range(len(self.phrases)):
            self.phrases[self.phraseTopics[i]] = self.phrases.pop(filelist[i])

    def drawGridLines(self):
        for i in range(self.nBoxes+1):
            # Horizontal stripes
            pygame.draw.line(self.screen, self.rgb['lineStkClr'], \
                (self.xyGridPos[0,0],self.xyGridPos[i,1]), \
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
                textRect = pygame.Rect((self.xyGridPos[j,0],self.xyGridPos[i,1],100,100))
                textRendered = render_textrect(text,self.gridFont,textRect,self.rgb['white'],self.rgb['black'], 1)
                self.screen.blit(textRendered, textRect.topleft)
#                img = self.gridFont.render(text, True, (255,255,255)) # TEST WITHOUT WRAPPING!
#                self.screen.blit(img,(100,100))                       # TEST WITHOUT WRAPPING!
                idx+=1
    
    def drawBox(self):
        pygame.draw.rect(self.screen, (67,86,102),
            (self.x_center + self.cursor[0] * self.box_size,
             self.y_center - self.cursor[1] * self.box_size,
             self.box_size, self.box_size), 0)

    def gridNumber(self):
        if self.radius == 2:
            # x -- HARD CODED
            if self.cursor[0]==-2: x = 0
            elif self.cursor[0]==-1: x = 1
            elif self.cursor[0]==0: x = 2
            elif self.cursor[0]==1: x = 3
            elif self.cursor[0]==2: x = 4
            # y -- HARD CODED
            if self.cursor[1]==2: y = 0
            elif self.cursor[1]==1: y = 1
            elif self.cursor[1]==0: y = 2
            elif self.cursor[1]==-1: y = 3
            elif self.cursor[1]==-2: y = 4
            # phrase location number in list
            self.phraseListNum = x + self.nBoxes*y
        else:
            print "WARNING: Speech phrase choices restricted to 5x5 grid only (for now)!"

    def selectSwitch(self):
        # MAIN GRID MENU
        if self.currentTopic == self.phraseTopics[0]:
            if self.cursor == [0,0]:
                self.close()
            else:
                self.gridNumber()
                self.currentTopic = self.phrases[self.currentTopic][self.phraseListNum]
                self.cursor = [0,0]
        # ALL OTHER TOPIC GRIDS - pick the center OR speak!
        else:
            if self.cursor == [0,0]:
                self.currentTopic = self.phraseTopics[0]
            else:
                self.gridNumber()
                # Mac or Windows speech synthesizer
                if self.speechOS == 'win32':
                    pass
					# speech.say(self.phrases[self.currentTopic][self.phraseListNum])
                else:
                    os.system('say '+ self.phrases[self.currentTopic][self.phraseListNum])

    def trials(self):
        nTrials         = 20 # total trial number...make it a divisor of nBoxes, please.
        trialsX         = np.array(range(nBoxes)*(nTrials/nBoxes)); random.shuffle(trialsX)
        trialsY         = copy.copy(trialsX); random.shuffle(trialsY)
        trials          = zip(trialsX,trialsY)
        for trial in trials:
            if trials[trial] == gridMid:
                print 'oops'
        targetAcquireTime = np.zeros(nTrials)
        targetNumberMoves = np.zeros(nTrials)

    def update(self, decision, selection):

        if self.controller.current_stimulus._trial_time > 4.0:
            self.controller.current_stimulus.changeFrequencies([1.0,12.0,6.0,15.0])

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