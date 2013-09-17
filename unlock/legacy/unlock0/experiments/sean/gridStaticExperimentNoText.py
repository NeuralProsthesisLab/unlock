from core import UnlockApplication
import numpy as np
import random
import time
import datetime
import socket

class GridStaticExperimentNoText(UnlockApplication):

    name = "Grid Speak Static Experiment No Text"
    gets_samples = True

    def __init__(self, screen, subjectNumber=None, fileLocation=None):
        """
            :Parameters:
                `subjectNumber`: Is a string ID passed by parent script.
                    Example: GridStaticExperimentNoText(screen, subjectNumber = 'SSVEP-P-000x')
                'fileLocation': Is a string file directory passed b parent script.
                    Example: GridStaticExperimentNoText(screen, fileLocation = '/Users/slorenz/Desktop/subjectFolder/')
        """
        super(self.__class__, self).__init__(screen)
        self.screen   = screen

        # IMPORTANT SETTINGS
        self.nTrials        = 3      # number of trials
        self.ISI            = 2.5    # ISI period (in secs)
        self.trialTimeOut   = 240.    # if target isn't reached by n secs, then it skips to the next trial
        self.nRows          = 7      # Grid row number
        self.nCols          = 11     # Grid column number
        self.box_size       = 80     # Pizel widxhgt of each grid square
        #self.cueText        = pygame.font.Font(None,72)

        # Other settings/variables
        self.sock           = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        self.sock.settimeout(0.001)
        now                 = datetime.datetime.now()
        data_file_name      = fileLocation+'gridStatic_runData_'+subjectNumber+'_'+str(now.hour)+str(now.minute)+'.txt'
        self.run_data       = open(data_file_name,'w')
        stats_file_name     = fileLocation+'gridStatic_runStats_'+subjectNumber+'_'+str(now.hour)+str(now.minute)+'.txt'
        self.run_stats      = open(stats_file_name,'w')
        self.x_radius   = (self.nCols-1)/2
        self.y_radius   = (self.nRows-1)/2
        self.cursor     = [0,0]
        self.lineStk    = 1
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
        self.rgb                = {'black': [0,0,0]}
        self.rgb['white']       = [255,255,255]
        self.rgb['move_box']    = (179,223,245)
        self.rgb['target_box']  = (59,181,45)
        self.rgb['lineStkClr']  = [67,86,102]

        # Trial info
        self.trials = np.zeros((self.nTrials,2))
        for trial in range(self.nTrials):
            self.trials[trial,0] = random.randint(-self.x_radius,self.x_radius)
            self.trials[trial,1] = random.randint(-self.y_radius,self.y_radius)

        # Initializations
        self.trialIdx       = -1
        self.sampleIdx      = 0
        self.trial_nMoves   = 0
        self.runtotaltime   = 0.0
        self.trialtotaltime = -self.ISI
        self.paused         = True

        # graphics objects
        self.cue_text = self.screen.drawText('Ready?',
            self.screen.get_width() / 2, self.screen.get_height() / 2)
        self.box = None
        self.target = None

    def drawGridLines(self):
        for i in range(self.nRows+1):
            # Horizontal stripes
            self.screen.drawLine(int(self.x_gridPos[0]),
                                 int(self.y_gridPos[i]),
                                 int(self.x_gridPos[0]+self.gridLen),
                                 int(self.y_gridPos[i]))
        for i in range(self.nCols+1):
            # Vertical stripes
            self.screen.drawLine(int(self.x_gridPos[i]),
                                 int(self.y_gridPos[0]),
                                 int(self.x_gridPos[i]),
                                 int(self.y_gridPos[0]+self.gridWid))

    def drawBoxes(self):
        self.target = self.screen.drawRect(self.x_center, self.y_center,
                                           self.box_size, self.box_size,
                                           color=self.rgb['target_box'])
        self.box = self.screen.drawRect(self.x_center, self.y_center,
                                        self.box_size, self.box_size,
                                        color=self.rgb['move_box'])

    def moveBox(self, box, x_step, y_step):
        if x_step:
            box.vertices[::2] = [i + int(x_step)*self.box_size for i in box.vertices[::2]]
        if y_step:
            box.vertices[1::2] = [i + int(y_step)*self.box_size for i in box.vertices[1::2]]

#    def drawCue(self,the_text):
#        img = self.cueText.render(the_text, True, self.rgb['white'])
#        x = (self.screen.get_width() - img.get_width())  / 2
#        y = (self.screen.get_height() - img.get_height()) / 2
#        self.screen.blit(img, (x, y))

    def trialAdvance(self):
        # ---------------- RESETS --------------- #
        self.moveBox(self.target,
                     self.trials[self.trialIdx,0] - self.trials[self.trialIdx-1,0],
                     self.trials[self.trialIdx,1] - self.trials[self.trialIdx-1,1])
        self.moveBox(self.box, -self.cursor[0], -self.cursor[1])

        self.cursor         = [0,0]
        self.trial_nMoves   = 0
        self.sock.sendto(str(1),('127.0.0.1',33448))
        self.trialtotaltime = -self.ISI

    def targetCheck(self):
        # target acquired check
        if self.cursor[0] == int(self.trials[self.trialIdx,0]) and self.cursor[1] == int(self.trials[self.trialIdx,1]):
            # write TRIAL STATS to file
            current_stats = [self.trialIdx,self.trialtotaltime,self.trial_nMoves]
            self.run_stats.write(str(current_stats)+"\n")
            self.trialIdx += 1
            if self.trialIdx == self.nTrials:
                # EXIT program and SAVE data to file
                self.run_data.close()
                self.run_stats.close()
                self.controller.quit()
            else:
                self.trialAdvance()


    def sample(self,data):
        if data is not None and len(data) > 0:
                for d in data:
                    if self.trialIdx < self.nTrials:
                        # write TRIAL DATA to file
                        current_data = [self.trialIdx,self.runtotaltime,self.trials[self.trialIdx,:]] + d[1:4]
                        self.run_data.write(str(current_data)+"\n")

    def runTimer(self):
        now_runtime = time.time()
        self.runtotaltime += now_runtime - self.last_runtime
        self.last_runtime = time.time()

    def trialTimer(self):
        now_trialtime       = time.time()
        self.trialtotaltime += now_trialtime - self.last_trialtime
        self.last_trialtime = time.time()

    def update(self, dt, decision, selection):
        # RUN INITIALIZATION
        if self.trialIdx == -1:
            self.controller.stimulus.stop()
            self.last_runtime = time.time()
            self.sock.sendto(str(1),('127.0.0.1',33448))
            self.trialIdx+=1

        # RUN timer
        self.runtotaltime += dt
        if self.paused:
            if self.runtotaltime > 3.0:
                self.paused = False
                self.drawGridLines()
                self.drawBoxes()
                self.moveBox(self.target, self.trials[0,0], self.trials[0,1])
                self.cue_text.delete()
                self.controller.stimulus.start()
                self.last_trialtime = time.time()
                self.sock.sendto(str(1),('127.0.0.1',33448))
            else:
                return

        # TRIAL timer
        current_time = self.trialtotaltime
        self.trialtotaltime += dt
        if (current_time < 0.0) and (self.trialtotaltime >= 0.0):
            self.sock.sendto(str(1),('127.0.0.1',33448))

        # increment trial move counter
        if decision:
            self.trial_nMoves+=1
            self.sock.sendto(str(1),('127.0.0.1',33448))

        # DECISION (move)
        if decision == 1 and self.cursor[1] < self.y_radius:
            self.cursor[1] += 1
            self.moveBox(self.box, 0, 1)
        elif decision == 2 and self.cursor[1] > -self.y_radius:
            self.cursor[1] -= 1
            self.moveBox(self.box, 0, -1)
        elif decision == 3 and self.cursor[0] > -self.x_radius:
            self.cursor[0] -= 1
            self.moveBox(self.box, -1, 0)
        elif decision == 4 and self.cursor[0] < self.x_radius:
            self.cursor[0] += 1
            self.moveBox(self.box, 1, 0)

        # SELECTION (click)
        if selection: self.targetCheck()

        # TRIAL TIMEOUT CHECK
        if self.trialtotaltime > self.trialTimeOut: self.trialAdvance()

#    def draw(self):
#        # ISI
#        if self.paused:
#            return
#        # CUE
#        if self.trialtotaltime < 0.0 and self.trialIdx < self.nTrials:
#            self.drawCue("Ready?")
#        # GRID
#        else:
#            if self.trialIdx < self.nTrials:
#                self.drawGridLines()    # grid lines
#                self.drawBoxTarget()    # target box
#                self.drawBox()          # current box
#            else:
#                self.drawCue("Run complete.")
