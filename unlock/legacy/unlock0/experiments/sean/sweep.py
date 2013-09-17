from core import UnlockApplication
import pyglet
import numpy as np
import random
import time
import datetime

class Sweep(UnlockApplication):

    name = "Sweep Experiment"
    gets_samples = True

    def __init__(self, screen, subjectNumber=None, fileLocation=None):
        """
            :Parameters:
                `subjectNumber`: Is a string ID passed by parent script.
                    Example: Sweep(screen, subjectNumber = 'SSVEP-P-000x')
                'fileLocation': Is a string file directory passed b parent script.
                    Example: Sweep(screen, fileLocation = '/Users/slorenz/Desktop/subjectFolder/')
        """
        super(self.__class__, self).__init__(screen)
        self.screen   = screen

        # IMPORTANT SETTINGS
        self.trialLen       = 5.0    # trial length (in secs)
        self.cue_time       = 2.0    # ISI period (in secs)
        n_freq_reps         = 5      # number of times to show each frequency in freqs_list below
        freqs_range 	    = [6.67, 7., 7.5, 8., 8.57, 12., 13., 14., 15., 16.]
        #self.cue_text       = pygame.font.Font(None,200)

        # other settings
        self.rgb            = {'black': [0,0,0]}
        self.rgb['white']   = [255,255,255]
        self.cue_directions = ['up','down','left','right']
        now                 = datetime.datetime.now()
        now                 = datetime.datetime.now()
        data_file_name      = fileLocation+'sweep_runData_'+subjectNumber+'_'+str(now.hour)+str(now.minute)+'.txt'
        self.run_data       = open(data_file_name,'w')
        trials_file_name    = fileLocation+'sweep_runFreqs_'+subjectNumber+'_'+str(now.hour)+str(now.minute)+'.txt'
        self.run_trials     = open(trials_file_name,'w')

        # TRIAL INFO
        self.nTrials        = len(freqs_range)*n_freq_reps
        self.trials         = np.zeros((4,self.nTrials))
        freqs_list          = sorted(freqs_range*n_freq_reps); random.shuffle(freqs_list)
        n_dir_reps          = self.nTrials / 4.
        dir_list            = range(4)*np.ceil(n_dir_reps)
        del dir_list[self.nTrials-len(dir_list):]
        random.shuffle(dir_list)
        self.attend_direction = np.array(dir_list)
        for i in range(self.nTrials):
            self.trials[dir_list[i],i] = freqs_list[i]
            dirs = np.setdiff1d(range(4),[dir_list[i]])
            freqs = random.sample(np.setdiff1d(freqs_list,[freqs_list[i]]),3)
            self.trials[dirs,i] = freqs

        self.cue_text = pyglet.text.Label('',
            font_name='Helvetica', font_size=72,
            x=self.screen.x+self.screen.get_width()/2, y=self.screen.y+self.screen.get_height()/2,
            anchor_x='center', anchor_y='center',batch=screen.batch)

        # timing initializations
        self.trialIdx = -1
        self.sampleIdx = 0
        self.runtotaltime = 0.0
        self.trialtotaltime = 0.0
        self.paused = True

#    def drawCue(self):
#        img = self.cue_text.render(self.cue_directions[int(self.attend_direction[self.trialIdx])], True, self.rgb['white'])
#        x = (self.screen.get_width() - img.get_width())  / 2
#        y = (self.screen.get_height() - img.get_height()) / 2
#        self.screen.blit(img, (x, y))

    def sample(self,data):
        if data is not None and len(data) > 0:
            for d in data:
                if self.trialIdx < self.nTrials:
                    # Grab current trial number, run time, current attend direction, and EEG data from O1,Oz,O2
                    current_data = [self.trialIdx,self.runtotaltime,self.attend_direction[self.trialIdx]] + d[1:4]
                    self.run_data.write(str(current_data)+"\n")

    def runTimer(self):
        now_runtime = time.time()
        self.runtotaltime += now_runtime - self.last_runtime
        self.last_runtime = time.time()

    def trialTimer(self):
        now_trialtime       = time.time()
        self.trialtotaltime += now_trialtime - self.last_trialtime
        self.last_trialtime = time.time()

    def pauseTimer(self):
        pausetimer = 0.0
        last_pausetime = time.time()
        while pausetimer < self.cue_time*2:
            now_pausetime = time.time()
            pausetimer += now_pausetime - last_pausetime
            last_pausetime = time.time()

    def update(self, dt, decision, selection):
        # RUN INITIALIZATION
        if self.trialIdx == -1:
            self.controller.stimulus.stop()
            self.current_state = "stimulus"
            self.last_runtime = time.time()
            self.trialIdx+=1

        # UPDATE TIMERS
        self.runtotaltime += dt
        if self.paused:
            if self.runtotaltime > 3.0:
                self.paused = False
                self.controller.stimulus.start()
                self.last_trialtime = time.time()
            else:
                return
        self.trialtotaltime += dt

        # TRIAL STATE SWITCH
        current_state = self.current_state
        if (current_state == "stimulus") and (self.trialtotaltime < self.cue_time):
            self.current_state = "cue"
            self.cue_text.text = self.cue_directions[int(self.attend_direction[self.trialIdx])]
        elif (current_state == "cue") and (self.cue_time <= self.trialtotaltime):
            self.current_state = "stimulus"
            self.cue_text.text = ''
        elif self.trialtotaltime >= (self.trialLen+self.cue_time):
            self.trialIdx += 1
            # RUN next trial
            if self.trialIdx < self.nTrials:
                self.trialtotaltime = 0.0
                self.controller.stimulus.changeFrequencies(self.trials[:,self.trialIdx])
            # EXIT program and SAVE data to file
            else:
                self.run_data.close()
                self.run_trials.write(str(self.trials))
                self.run_trials.close()
                self.controller.quit()

#    def draw(self):
#        if self.trialtotaltime <= self.cue_time:
#            self.drawCue()
