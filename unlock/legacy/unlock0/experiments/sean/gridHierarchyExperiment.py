from apps.grid._textwrap import *
from core import UnlockApplication
import pygame.font; pygame.font.init()
import numpy as np
import copy
import random
import time
import datetime
import socket

class GridHierarchyExperiment(UnlockApplication):

    name = "Grid Speak Hierarchy Experiment"
    gets_samples = True

    def __init__(self,screen):
        super(self.__class__, self).__init__(screen)
        self.screen   = screen
        self.sock     = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        self.sock.settimeout(0.001)

        # IMPORTANT SETTINGS
        subjectNumber       = '0001' # in string format
        self.nTrials        = 3   # number of trials
        self.ISI            = 2.  # ISI period (in secs)
        self.trialTimeOut   = 30. # if target isn't reached by n secs, then it skips to the next trial
        grid_font_size      = 18  # text font size in an individual grid square
        self.cueText        = pygame.font.Font(None,72)
        filelist            = ['dashboard','feelings','food','smalltalk','urgent']
        self.phraseTopics   = ['MAIN MENU','Feelings & Emotions','Eating & Drinking','Small Talk','Urgent Requests']

        # other settings/variables
        self.nBoxes         = 5
        self.box_size       = 100
        now                 = datetime.datetime.now()
        self.data_file      = 'gridHierarchy_runData_'+subjectNumber+'_'+str(now.hour)+str(now.minute)+'.npy'
        self.stats_file     = 'gridHierarchy_runStats_'+subjectNumber+'_'+str(now.hour)+str(now.minute)+'.npy'
        self.rgb            = {'black': [0,0,0]}
        self.rgb['white']   = [255,255,255]
        self.rgb['iceblue'] = [179,223,245]
        self.rgb['red']     = [204,61,0]
        self.rgb['lineStkClr'] = [67,86,102]         # line stroke color
        self.radius         = (self.nBoxes-1)/2
        self.cursor         = [0,0]
        self.lineStk        = 1
        self.gridFont       = pygame.font.SysFont("Arial", grid_font_size)
        self.gridLen        = self.nBoxes*self.box_size    # The total pixel length of a grid
        self.x_center       = (self.screen.get_width()-self.box_size)/ 2
        self.y_center       = (self.screen.get_height()-self.box_size)/2
        self.xyGridPos      = np.zeros((self.nBoxes+1,2))  # 6x2 matrix of x-y topleft coords
        idx=0
        for edge in range(-self.radius,self.radius+2): # Creates 6 lines from [-2,4]
            self.xyGridPos[idx,0] = self.x_center + edge*self.box_size
            self.xyGridPos[idx,1] = self.y_center + edge*self.box_size
            idx+=1

        # load phrase topic lists
        filePhraseList    = "resource/phrases3_"
        self.currentTopic = self.phraseTopics[0]
        self.phrases      = {}
        phrases_all       = []
        for plist in filelist:
            self.phrases[plist] = []
            fd = open(filePhraseList + plist + '.txt', 'r')
            lines = fd.readlines()
            for line in lines:
                el=line.strip().split('\t')
                self.phrases[plist].append(el[0])
                if plist is not 'dashboard': phrases_all.append(el[0]) # for trial list selection only
            fd.close()
            if plist is not 'dashboard':
                self.phrases[plist].insert(12,'MENU') # Add MENU to the center of each list!
        for i in range(len(self.phrases)):
            self.phrases[self.phraseTopics[i]] = self.phrases.pop(filelist[i])

        # Trial info
        self.trial_phrases = copy.deepcopy(phrases_all)
        random.shuffle(self.trial_phrases)
        self.trial_phrases = self.trial_phrases[0:self.nTrials+1]

        # Initializations
        self.trialIdx       = -1
        self.sampleIdx      = 0
        self.trial_nMoves   = 0
        self.runtotaltime   = 0.0
        self.trialtotaltime = -self.ISI
        self.run_data       = np.zeros((2,6))  # [[N samples],[trial_idx,runtime,attend_direction,O1,Oz,O2]]
        self.run_stats      = np.zeros((2,3)) # [[N samples],[trial_idx,trial_totalTime,trial_nMoves]]
        self.paused         = True
        self.target_phrase  = None

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
                # change the Category of phrases (unless it's an empty item from the main dashboard)
                if self.currentTopic != '':
                    text = self.phrases[self.currentTopic][idx]
                    textRect = pygame.Rect((self.xyGridPos[j,0],self.xyGridPos[i,1],100,100))
                    textRendered = render_textrect(text,self.gridFont,textRect,self.rgb['white'],self.rgb['black'], 1)
                    self.screen.blit(textRendered, textRect.topleft)
                    idx+=1
                else:
                    self.currentTopic = self.phraseTopics[0]
    
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
        # location in x-y coordinates
        for i in range(self.nBoxes):
            if self.cursor[0] == (-self.radius)+i: x = i
            if self.cursor[1] == self.radius-i: y = i
        # location in phrase list
        self.phraseListNum = x + self.nBoxes*y

    def trialAdvance(self):
        current_stats = [self.trialIdx,self.trialtotaltime,self.trial_nMoves]
        self.run_stats = np.vstack((self.run_stats,current_stats))          # Store trial statistics
        self.trialIdx      += 1                                             # ----- RESETS -----
        self.cursor         = [0,0]
        self.trial_nMoves   = 0
        self.sock.sendto(str(1),('127.0.0.1',33448))
        self.trialtotaltime = -self.ISI
        self.currentTopic = self.phraseTopics[0]                            # reset to main dashboard

    def targetCheck(self):
        # MAIN GRID MENU
        if self.currentTopic == self.phraseTopics[0]:
            self.gridNumber()
            self.currentTopic = self.phrases[self.currentTopic][self.phraseListNum]
            self.cursor = [0,0]
        # ALL OTHER TOPIC GRIDS
        else:
            if self.cursor == [0,0]:
                self.currentTopic = self.phraseTopics[0]
            else:
                self.gridNumber()                                                       # Get the list number
                selected_phrase = self.phrases[self.currentTopic][self.phraseListNum]   # Get the phrase
                if selected_phrase == self.target_phrase:                               # TARGET ACQUIRED!
                    self.trialAdvance()
                # EXIT program and SAVE data to file
                if self.trialIdx == self.nTrials:
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
        if decision == 1 and self.cursor[1] < self.radius:
            self.cursor[1] += 1
        elif decision == 2 and self.cursor[1] > -self.radius:
            self.cursor[1] -= 1
        elif decision == 3 and self.cursor[0] > -self.radius:
            self.cursor[0] -= 1
        elif decision == 4 and self.cursor[0] < self.radius:
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
        if (self.trialtotaltime < 0.0) and (self.trialIdx < self.nTrials):
            self.drawCue()
        # GRID
        else:
            self.drawGridLines()
            self.drawBox()
            self.drawSpeechText()
