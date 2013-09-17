import pygame
import random
from core import UnlockApplication
import time
import datetime
import numpy as np
import socket

class UDLR(UnlockApplication):

    name = "UDLR Experiment"
    gets_samples = True

    def __init__(self, screen, subjectNumber=None, fileLocation=None):
        """
            :Parameters:
                `subjectNumber`: Is a string ID passed by parent script.
                    Example: UDLR(screen, subjectNumber = 'SSVEP-P-000x')
                'fileLocation': Is a string file directory passed b parent script.
                    Example: UDLR(screen, fileLocation = '/Users/slorenz/Desktop/subjectFolder/')
        """
        super(self.__class__, self).__init__(screen)
        self.screen   = screen

        # IMPORTANT SETTINGS
        n_direction_reps    = 1                # times to show each attended direction
        self.cue_time       = 2.0               # trial end time for cue
        self.stim_time      = 6.0               # trial end time for stimulus
        self.pred_time      = 8.0               # trial end time for prediction
        self.pred_color_correct = (2,193,47)    # Correct prediction color
        self.pred_color_wrong   = (239,48,0)    # Wrong prediction color

        # other settings
        self.thumbs_up      = pygame.image.load("resource/thumbs_up.png")
        self.thumbs_down    = pygame.image.load("resource/thumbs_down.png")
        self.sock           = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        self.sock.settimeout(0.001)
        self.directions     = ['up','down','left','right']
        self.nTrials        = len(self.directions)*n_direction_reps
        self.text           = pygame.font.Font(None,150)
        self.cue_color      = (255,255,255)
        self.predictions    = np.zeros((self.nTrials,2))
        now                 = datetime.datetime.now()
        data_file_name      = fileLocation+'udlr_runData_'+subjectNumber+'_'+str(now.hour)+str(now.minute)+'.txt'
        self.run_data       = open(data_file_name,'w')
        stats_file_name     = fileLocation+'udlr_runStats_'+subjectNumber+'_'+str(now.hour)+str(now.minute)+'.txt'
        self.run_stats      = open(stats_file_name,'w')

        # trials
        self.trials = range(4)*n_direction_reps
        random.shuffle(self.trials)

        # timing initializations
        self.trialIdx       = -1
        self.runtotaltime   = 0.0
        self.trialtotaltime = 0.0
        self.paused         = True
        self.pred_text      = self.text.render('', True, self.pred_color_correct)

    def sample(self,data):
        if data is not None and len(data) > 0:
            for d in data:
                if self.trialIdx < self.nTrials:
                    # Grab current trial number, run time, current attend direction, and EEG data from O1,Oz,O2
                    current_data = [self.trialIdx,self.runtotaltime,self.trials[self.trialIdx]] + d[1:4]
                    self.run_data.write(str(current_data)+"\n")

    def runTimer(self):
        now_runtime = time.time()
        self.runtotaltime += now_runtime - self.last_runtime
        self.last_runtime = time.time()

    def trialTimer(self):
        now_trialtime       = time.time()
        self.trialtotaltime += now_trialtime - self.last_trialtime
        self.last_trialtime = time.time()

    def postRunClassCorrect(self):
        print self.predictions
        # show the final percent correct
        trial_correct = 0.
        for i in range(self.nTrials):
            if self.predictions[i][0] == self.predictions[i][1]:
                trial_correct +=1.
        print "Percent of correct trials: " + str((trial_correct/self.nTrials)*100) + '%'
        # show the percent correct for each direction
        up_correct=0.; down_correct=0.; left_correct=0.; right_correct=0.
        for i in range(self.nTrials):
            if self.trials[i] == 0 and self.predictions[i][0] == self.predictions[i][1]:
                up_correct +=1.
            if self.trials[i] == 1 and self.predictions[i][0] == self.predictions[i][1]:
                down_correct +=1.
            if self.trials[i] == 2 and self.predictions[i][0] == self.predictions[i][1]:
                left_correct +=1.
            if self.trials[i] == 3 and self.predictions[i][0] == self.predictions[i][1]:
                right_correct +=1.
        print 'Up: ', str(up_correct*100), '% correct'
        print 'Down: ', str(down_correct*100), '% correct'
        print 'Left: ', str(left_correct*100), '% correct'
        print 'Right: ', str(right_correct*100), '% correct'

    def update(self, decision, selection):

        # RUN INITIALIZATION
        if self.trialIdx == -1:
            if decision is not None: decision = None
            self.sock.sendto(str(1),('127.0.0.1',33448))
            self.display.current_stimulus.stop()
            self.current_state = "cue"
            self.last_runtime = time.time()
            self.trialIdx+=1

        # UPDATE TIMERS
        self.runTimer()
        if self.paused:
            if self.runtotaltime > 3.0:
                self.paused = False
                self.display.current_stimulus.start()
                self.sock.sendto(str(1),('127.0.0.1',33448))
                self.last_trialtime = time.time()
            else:
                return
        self.trialTimer()

        # TRIAL STATE SWITCH
        current_state = self.current_state
        if (current_state == "prediction") and (self.trialtotaltime < self.cue_time):
            self.current_state = "cue"
        elif (current_state == "cue") and (self.cue_time <= self.trialtotaltime):
            self.current_state = "stimulus"
        elif (current_state == "stimulus") and (decision is not None):
            self.current_state = "prediction"
        elif self.trialtotaltime > self.pred_time:
            self.trialtotaltime = 0.0
            self.trialIdx+=1
            # EXIT program if that was the last trial
            if self.trialIdx == self.nTrials:
                self.display.current_stimulus.stop()
                self.postRunClassCorrect()
                self.run_data.close()
                self.run_stats.close()
        # clear the 4s decoder buffer if switching states
        if current_state != self.current_state: self.sock.sendto(str(1),('127.0.0.1',33448))

        # DECISION
        if decision:
            decision -= 1 # make it 0-3 not 1-4!
            # show prediction feedback!
            if decision == self.trials[self.trialIdx]:
                self.pred_thumb = self.thumbs_up
            else:
                self.pred_thumb = self.thumbs_down
            # add prediction to output file
            if self.trialIdx < self.nTrials:
                # store 1) trial class ground truth and 2) decoder prediction
                self.run_stats.write(str([self.trials[self.trialIdx],decision])+"\n")
                self.predictions[self.trialIdx,:] = [self.trials[self.trialIdx],decision]

    def draw(self):

        # Check for cue pause
        if self.paused:
            return

        # Draw according to the current state
        if self.trialIdx < self.nTrials:
            # CUE (2s)
            if self.current_state == "cue":
                cue_text = self.text.render(self.directions[self.trials[self.trialIdx]], True, self.cue_color)
                x = (self.screen.get_width() - cue_text.get_width())  / 2
                y = (self.screen.get_height() - cue_text.get_height()) / 2
                self.screen.blit(cue_text, (x, y))
            # STIMULUS (4s)
            elif self.current_state == "stimulus":
                self.screen.fill((0,0,0))
            # PREDICTION (2s)
            elif self.current_state == "prediction":
                x = (self.screen.get_width() - self.pred_thumb.get_width())  / 2
                y = (self.screen.get_height() - self.pred_thumb.get_height()) / 2
                self.screen.blit(self.pred_thumb,(x,y))
#                self.screen.blit(self.pred_text, (x, y))