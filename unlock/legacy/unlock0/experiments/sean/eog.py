from core import UnlockApplication
import pygame
import numpy as np
import random
import time
import datetime

class EOG(UnlockApplication):

    name = "EOG Experiment"
    gets_samples = True

    def __init__(self, screen, subjectNumber=None, fileLocation=None):
        """
            :Parameters:
                `subjectNumber`: Is a string ID passed by parent script.
                    Example: EOG(screen, subjectNumber = 'SSVEP-P-000x')
                'fileLocation': Is a string file directory passed b parent script.
                    Example: EOG(screen, fileLocation = '/Users/slorenz/Desktop/subjectFolder/')
        """
        super(self.__class__, self).__init__(screen)
        self.screen   = screen

        # IMPORTANT SETTINGS
        self.nTrials        = 20                # number of total trials per run
        self.ISI            = 1.5               # blank ISI period (in secs)
        self.cue_time       = 2.5               # time (in secs) to show the "blink"/"double blink" cue
        self.cue_choices    = ["single blink","double blink"]
        self.cue_text       = pygame.font.Font(None,120)

        # other settings
        now                 = datetime.datetime.now()
        data_file_name      = fileLocation+'eog_runData_'+subjectNumber+'_'+str(now.hour)+str(now.minute)+'.txt'
        self.run_data       = open(data_file_name,'w')

        # trial info - use to tell duration of each trial's time to close eyes
        self.trials         = np.zeros(self.nTrials)
        for trial in range(self.nTrials):
            self.trials[trial]   = random.randint(0,1)

        # timing initializations
        self.trialIdx       = -1
        self.sampleIdx      = 0
        self.paused         = True
        self.trialtotaltime = 0

    def drawCue(self,the_text):
        img = self.cue_text.render(the_text, True, (255,255,255))
        x = (self.screen.get_width() - img.get_width())  / 2
        y = (self.screen.get_height() - img.get_height()) / 2
        self.screen.blit(img, (x, y))

    def sample(self,data):
        if data is not None and len(data) > 0:
            for d in data:
                if self.trialIdx < self.nTrials:
                    # write TRIAL DATA to file
                    current_data = str([self.trialIdx,self.trials[self.trialIdx],d[0]])
                    self.run_data.write(current_data + "\n")

    def trialTimer(self):
        now_trialtime       = time.time()
        self.trialtotaltime += now_trialtime - self.last_trialtime
        self.last_trialtime = time.time()

    def update(self, decision, selection):

        # run initialization
        if self.trialIdx == -1:
            self.controller.current_stimulus.stop()
            self.trialIdx += 1
            self.last_trialtime = time.time()

        # trial timer
        self.trialTimer()

        # ISI
        if self.paused:
            if self.trialtotaltime > self.ISI:
                self.paused = False
                self.trialtotaltime = 0.0
            else:
                return

        # end of trial
        if self.trialIdx < self.nTrials:
            if self.trialtotaltime > self.cue_time:
                # resets
                self.trialIdx      += 1
                self.trialtotaltime = 0.0
                self.paused         = True

    def draw(self):

        # ISI
        if self.paused:
            pass
        # CUE
        else:
            if self.trialIdx < self.nTrials:
                trial_cue = self.cue_choices[int(self.trials[self.trialIdx])]
                self.drawCue(trial_cue)
            else:
                self.drawCue("Run complete.")
                self.run_data.close()