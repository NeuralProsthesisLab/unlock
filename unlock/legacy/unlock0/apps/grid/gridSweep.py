from core import UnlockApplication
import pygame
import numpy as np
import random
import time

class GridSweep(UnlockApplication):

    name = "Grid SSVEP Sweep"
    gets_samples = True

    def __init__(self,screen):
        super(self.__class__, self).__init__(screen)
        self.screen   = screen

        # IMPORTANT SETTINGS
        self.trialLen       = 4     # trial length (in secs)
        self.trialPause     = 2     # ISI period (in secs)
        self.nBoxes         = 3     # number of grid box rows/columns
        self.box_size       = 150   # individual box size (in pixels)
        self.cue_size       = 50    # cue box size
        self.offset_amt     = 15    # number of pixels to offset cue box outside grid
        n_freq_reps         = 1     # number of times to show each frequency in freqs_list below
#        freqs_list          = [6.0,7.0,8.0,9.0,10.0,11.0,12.0,13.0,14.0,15.0,16.0,17.0,18.0,19.0]
        freqs_list          = [1.0,30.0,30.0,30.0,30.0]
        self.data_file      = 'data_gridSweep.txt'

        # other settings/variables
        self.rgb            = {'black': [0,0,0]}
        self.rgb['white']   = [255,255,255]
        self.rgb['iceblue'] = [179,223,245]
        self.rgb['red']     = [204,61,0]
        self.rgb['lineStkClr'] = [67,86,102]
        self.rgb['green']   = [0,163,0]
        self.radius     = (self.nBoxes-1)/2
        self.cursor     = [0,0]
        self.lineStk    = 1
        self.gridLen    = self.nBoxes*self.box_size    # The total pixel length of a grid
        self.x_center   = (self.screen.get_width()-self.box_size)/ 2
        self.y_center   = (self.screen.get_height()-self.box_size)/2
        self.xyGridPos  = np.zeros((self.nBoxes+1,2))  # 6x2 matrix of x-y topleft coords
        idx=0
        for edge in range(-self.radius,self.radius+2): # Creates 6 lines from [-2,4]
            self.xyGridPos[idx,0] = self.x_center + edge*self.box_size
            self.xyGridPos[idx,1] = self.y_center + edge*self.box_size
            idx+=1

        # TRIAL INFO
        freqs_list  = sorted(freqs_list*n_freq_reps)
        self.nTrials= len(freqs_list)
        freqs_all   = np.zeros((4,self.nTrials))
        self.attend_direction = np.zeros(self.nTrials)
        self.trials = np.zeros((4,self.nTrials))
        trial_order = range(self.nTrials); random.shuffle(trial_order)
        for i in xrange(self.nTrials):
            self.attend_direction[i] = random.randint(0,3)        # Choose the attended direction
            freqs_all[:,i] = random.sample(freqs_list,4)          # Pick 4 freqs randomly from full list
            freqs_all[self.attend_direction[i],i] = freqs_list[i] # Replace the attended direction trial with new freq
        for i in xrange(self.nTrials):
            self.trials[:,i] = freqs_all[:,trial_order[i]]        # The shuffled version of freqs_all

        # timing initializations
        self.trialIdx = -1
        self.sampleIdx = 0
        self.runtotaltime = 0.0
        self.trialtotaltime = 0.0
        self.run_data = np.zeros((2,5)) # [[N samples],[runtime,trial_attendDirection,O1,Oz,O2]]

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

    def drawBox(self):
        pygame.draw.rect(self.screen, self.rgb['lineStkClr'],
            (self.x_center + self.cursor[0] * self.box_size,
             self.y_center - self.cursor[1] * self.box_size,
             self.box_size, self.box_size), 0)

    def drawCueBox(self):
        current_trial_direction = self.attend_direction[self.trialIdx]
        if current_trial_direction == 0:    # UP
            pygame.draw.rect(self.screen,self.rgb['green'],(self.x_center+
                ((self.box_size-self.cue_size)/2),self.offset_amt,self.cue_size,self.cue_size),0)
        elif current_trial_direction == 1:  # DOWN
            pygame.draw.rect(self.screen,self.rgb['green'],(self.x_center+((self.box_size-self.cue_size)/2),
                self.screen.get_height()-self.cue_size-self.offset_amt,self.cue_size,self.cue_size),0)
        elif current_trial_direction == 2:  # LEFT
            pygame.draw.rect(self.screen,self.rgb['green'],(self.x_center-(self.gridLen/2)+self.offset_amt,
                self.y_center+(self.box_size-self.cue_size)/2,self.cue_size,self.cue_size),0)
        elif current_trial_direction == 3: # RIGHT
            pygame.draw.rect(self.screen,self.rgb['green'],(self.x_center+(self.box_size*2)+self.offset_amt,
                self.y_center+(self.box_size-self.cue_size)/2,self.cue_size,self.cue_size),0)

    def sample(self,data):
        if data:
            # Grab current run time, current attend direction, and EEG data from O1,Oz,O2
            current_data = [self.runtotaltime,self.attend_direction[self.trialIdx]] + data[0:3]
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

        self.runTimer()   # update run timer
        self.trialTimer() # update trial timer

        # ISI period check
        if self.trialtotaltime >= self.trialLen: self.controller.current_stimulus.stop()

        # FREQUENCIES and RESETS for upcoming trial
        if self.trialtotaltime >= (self.trialLen+self.trialPause):
            self.trialIdx += 1
            # RUN next trial
            if self.trialIdx < self.nTrials:
                self.trialtotaltime = 0.0
                self.cursor = [0,0]
                self.controller.current_stimulus.changeFrequencies(self.trials[:,self.trialIdx])
                self.controller.current_stimulus.start()
            # EXIT program and SAVE data to file
            else:
                np.savetxt(self.data_file,self.run_data,fmt="%12.6G")
                self.controller.current_stimulus.changeFrequencies([12,13,14,15])
                self.controller.current_stimulus.start()
                self.close()

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
            if self.cursor == [0,0]: self.close()

    def draw(self):

        # Start timers -- not in update() because draw() called first for some reason!!
        if self.trialIdx == -1:
            self.controller.current_stimulus.stop()    # turn off SSVEP from the main dashboard
            self.last_runtime = time.time()         # initializes run timer
            self.last_trialtime = time.time()       # initializes trial timer
            self.trialtotaltime = self.trialLen+1000

        # Business as usual
        else:
            self.drawGridLines()
            self.drawBox()
            self.drawCueBox()
