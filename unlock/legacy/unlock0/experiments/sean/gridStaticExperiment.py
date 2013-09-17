from apps.grid._textwrap import *
from core import UnlockApplication
import pygame.font; pygame.font.init()
import numpy as np
import copy
import random
import time
import datetime
import socket

class GridStaticExperiment(UnlockApplication):

    name = "Grid Speak Static Experiment"
    gets_samples = True

    def __init__(self,screen):
        super(self.__class__, self).__init__(screen)
        self.screen   = screen
        self.sock     = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        self.sock.settimeout(0.001)

        # IMPORTANT SETTINGS
        subjectNumber       = '0001' # in string format
        self.nTrials        = 3      # number of trials
        self.ISI            = 2.5    # ISI period (in secs)
        self.trialTimeOut   = 90.    # if target isn't reached by n secs, then it skips to the next trial
        self.nRows          = 7
        self.nCols          = 11
        self.box_size       = 80
        grid_font_size      = 15
        self.cueText        = pygame.font.Font(None,72)

        # Other settings/variables
        now                 = datetime.datetime.now()
        self.data_file      = 'gridStatic_runData_'+subjectNumber+'_'+str(now.hour)+str(now.minute)+'.npy'
        self.stats_file     = 'gridStatic_runStats_'+subjectNumber+'_'+str(now.hour)+str(now.minute)+'.npy'
        self.rgb            = {'black': [0,0,0]}
        self.rgb['white']   = [255,255,255]
        self.rgb['iceblue'] = [179,223,245]
        self.rgb['red']     = [204,61,0]
        self.rgb['lineStkClr'] = [67,86,102]
        self.x_radius   = (self.nCols-1)/2
        self.y_radius   = (self.nRows-1)/2
        self.cursor     = [0,0]
        self.lineStk    = 1
        self.gridFont   = pygame.font.SysFont("Arial", grid_font_size)
        self.gridWid    = self.nRows*self.box_size    # The total pixel width of a grid
        self.gridLen    = self.nCols*self.box_size    # The total pixel length of a grid
        self.x_center   = (self.screen.get_width()-self.box_size)/ 2
        self.y_center   = (self.screen.get_height()-self.box_size)/2
        self.x_gridPos  = np.zeros(self.nCols+1)
        self.y_gridPos  = np.zeros(self.nRows+1)
        idx=0
        for i in range(-self.x_radius,self.x_radius+2):
            self.x_gridPos[idx] = self.x_center + i*self.box_size; idx+=1
        idx=0
        for i in range(-self.y_radius,self.y_radius+2):
            self.y_gridPos[idx] = self.y_center + i*self.box_size; idx+=1

        # Load phrases
        filePhraseList = "resource/phrases3_experiment.txt"
        self.phrases = []
        fd = open(filePhraseList, 'r')
        lines = fd.readlines()
        for line in lines:
            el=line.strip().split('\t')
            self.phrases.append(el[0])
        fd.close()
        self.phrases.insert((self.nRows*self.nCols)/2,'MAIN MENU') # Add MAIN MENU to the center

        # Trial info
        self.trial_phrases = copy.deepcopy(self.phrases)
        random.shuffle(self.trial_phrases)
        self.trial_phrases = self.trial_phrases[0:self.nTrials+1]

        # Initializations
        self.trialIdx       = -1
        self.sampleIdx      = 0
        self.trial_nMoves   = 0
        self.runtotaltime   = 0.0
        self.trialtotaltime = -self.ISI
        self.run_data = np.zeros((2,6))  # [[N samples],[trial_idx,runtime,trial_phrase,O1,Oz,O2]]
        self.run_stats = np.zeros((2,3)) # [[N samples],[trial_idx,trial_totalTime,trial_nMoves]]
        self.paused = True
        self.target_phrase = None

    def drawGridLines(self):
        for i in range(self.nRows+1):
            # Horizontal stripes
            pygame.draw.line(self.screen, self.rgb['lineStkClr'],\
                (self.x_gridPos[0],self.y_gridPos[i]),\
                (self.x_gridPos[0]+self.gridLen,self.y_gridPos[i]), self.lineStk)
        for i in range(self.nCols+1):
            # Vertical stripes
            pygame.draw.line(self.screen, self.rgb['lineStkClr'],\
                (self.x_gridPos[i],self.y_gridPos[0]),\
                (self.x_gridPos[i],self.y_gridPos[0]+self.gridWid), self.lineStk)

    def drawSpeechText(self):
        idx=0
        for i in range(self.nRows):
            for j in range(self.nCols):
                text = self.phrases[idx]
                textRect = pygame.Rect((self.x_gridPos[j],self.y_gridPos[i],self.box_size,self.box_size))
                textRendered = render_textrect(text,self.gridFont,textRect,self.rgb['white'],self.rgb['black'], 1)
                self.screen.blit(textRendered, textRect.topleft)
                idx+=1

    def drawBox(self):
        pygame.draw.rect(self.screen, self.rgb['lineStkClr'],
            (self.x_center + self.cursor[0] * self.box_size,
             self.y_center - self.cursor[1] * self.box_size,
             self.box_size, self.box_size), 0)

    def drawCue(self):
        self.target_phrase = self.trial_phrases[self.trialIdx]
        img = self.cueText.render(self.target_phrase, True, self.rgb['white'])
        x = (self.screen.get_width() - img.get_width())  / 2
        y = (self.screen.get_height() - img.get_height()) / 2
        self.screen.blit(img, (x, y))

    def gridNumber(self):
        for i in range(self.nCols):
            if self.cursor[0] == (-self.x_radius) + i: x = i # x coordinate location
        for i in range(self.nRows):
            if self.cursor[1] == self.y_radius - i:    y = i # y coordinate location
        self.phraseListNum = x + self.nCols*y                # phrase list location

    def trialAdvance(self):
        current_stats = [self.trialIdx,self.trialtotaltime,self.trial_nMoves]
        self.run_stats = np.vstack((self.run_stats,current_stats))          # Store trial statistics
        self.trialIdx      += 1                                             # ----- RESETS -----
        self.cursor         = [0,0]
        self.trial_nMoves   = 0
        self.sock.sendto(str(1),('127.0.0.1',33448))
        self.trialtotaltime = -self.ISI

    def targetCheck(self):
        self.gridNumber()                                               # Get the list number
        selected_phrase = self.phrases[self.phraseListNum]              # Get the phrase
        if selected_phrase == self.target_phrase:                       # TARGET ACQUIRED!
            self.trialAdvance()
            # EXIT program and SAVE data to file
            if self.trialIdx == self.nTrials:
 		print "all done"
                np.save(self.data_file, self.run_data)
                np.save(self.stats_file,self.run_stats)
                self.controller.current_stimulus.stop()

    def sample(self,data):
        if data is not None and len(data) > 0:
                for d in data:
                    if self.trialIdx < self.nTrials:
                        # Grab current trial number, run time, current attend direction, and EEG data from O1,Oz,O2
                        current_data = [self.trialIdx,self.runtotaltime,self.trial_phrases[self.trialIdx]] + d[1:4]
                        self.run_data = np.vstack((self.run_data,current_data))

    def runTimer(self):
        now_runtime = time.time()
        self.runtotaltime += now_runtime - self.last_runtime
        self.last_runtime = time.time()

    def trialTimer(self):
        now_trialtime       = time.time()
        self.trialtotaltime += now_trialtime - self.last_trialtime
        self.last_trialtime = time.time()

    def update(self, decision, selection):
        # RUN INITIALIZATION
        if self.trialIdx == -1:
            self.controller.current_stimulus.stop()
            self.last_runtime = time.time()         # initializes run timer
#            self.last_trialtime = time.time()       # initializes trial timer
            self.sock.sendto(str(1),('127.0.0.1',33448))
            self.trialIdx+=1

        # RUN timer
        self.runTimer()   # update run timer
        if self.paused:
            if self.runtotaltime > 3.0:
                self.paused = False
                self.controller.current_stimulus.start()
                self.last_trialtime = time.time()       # initializes trial timer
                self.sock.sendto(str(1),('127.0.0.1',33448))
            else:
                return

        # TRIAL timer
        current_time = self.trialtotaltime
        self.trialTimer() # update trial timer
        if (current_time < 0.0) and (self.trialtotaltime >= 0.0):
            self.sock.sendto(str(1),('127.0.0.1',33448))

        # increment trial move counter
        if decision: self.trial_nMoves+=1

        # DECISION (move)
        if decision == 1 and self.cursor[1] < self.y_radius:
            self.cursor[1] += 1
        elif decision == 2 and self.cursor[1] > -self.y_radius:
            self.cursor[1] -= 1
        elif decision == 3 and self.cursor[0] > -self.x_radius:
            self.cursor[0] -= 1
        elif decision == 4 and self.cursor[0] < self.x_radius:
            self.cursor[0] += 1

        # SELECTION (click)
        if selection: self.targetCheck()

        # TRIAL TIMEOUT CHECK
        if self.trialtotaltime > self.trialTimeOut: self.trialAdvance()

    def draw(self):
        # ISI
        if self.paused:
            return
        # CUE
        if self.trialtotaltime < 0.0 and self.trialIdx < self.nTrials:
            self.drawCue()
        # GRID
        else:
            self.drawGridLines()
            self.drawBox()
            self.drawSpeechText()
