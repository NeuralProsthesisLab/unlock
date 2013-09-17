from core import UnlockApplication
import numpy as np
import random
import time
import datetime
import socket

class GridHierarchyExperimentNoText(UnlockApplication):

    name = "Grid Speak Hierarchy Experiment No Text"
    gets_samples = True

    def __init__(self, screen, subjectNumber=None, fileLocation=None):
        """
            :Parameters:
                `subjectNumber`: Is a string ID passed by parent script.
                    Example: GridHierarchyExperimentNoText(screen, subjectNumber = 'SSVEP-P-000x')
                'fileLocation': Is a string file directory passed b parent script.
                    Example: GridHierarchyExperimentNoText(screen, fileLocation = '/Users/slorenz/Desktop/subjectFolder/')
        """
        super(self.__class__, self).__init__(screen)
        self.screen   = screen

        # IMPORTANT SETTINGS
        self.nTrials        = 3              # number of trials
        self.ISI            = 2.5            # ISI period (in secs)
        self.trialTimeOut   = 240.           # trial timeout length if target not reached
        #self.cueText        = pygame.font.Font(None,72)
        self.nBoxes         = 5

        # other settings/variables
        self.levels         = ["level1","level2"]
        self.current_level  = self.levels[0]
        self.sock           = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        self.sock.settimeout(0.001)
        self.box_size       = 100
        now                 = datetime.datetime.now()
#        data_file_name      = '../../../gridHierarchy_runData_'+subjectNumber+'_'+str(now.hour)+str(now.minute)+'.txt'
        data_file_name      = fileLocation+'gridHierarchy_runData_'+subjectNumber+'_'+str(now.hour)+str(now.minute)+'.txt'
        self.run_data       = open(data_file_name,'w')
#        stats_file_name     = '../../../gridHierarchy_runStats_'+subjectNumber+'_'+str(now.hour)+str(now.minute)+'.txt'
        stats_file_name     = fileLocation+'gridHierarchy_runStats_'+subjectNumber+'_'+str(now.hour)+str(now.minute)+'.txt'
        self.run_stats      = open(stats_file_name,'w')
        self.radius         = (self.nBoxes-1)/2
        self.cursor         = [0,0]
        self.lineStk        = 1
        self.gridLen        = self.nBoxes*self.box_size    # The total pixel length of a grid
        self.x_center       = (self.screen.get_width()-self.box_size)/ 2
        self.y_center       = (self.screen.get_height()-self.box_size)/2
        self.xyGridPos      = np.zeros((self.nBoxes+1,2))  # 6x2 matrix of x-y topleft coords
        idx=0
        for edge in range(-self.radius,self.radius+2): # Creates 6 lines from [-2,4]
            self.xyGridPos[idx,0] = self.x_center + edge*self.box_size
            self.xyGridPos[idx,1] = self.y_center + edge*self.box_size
            idx+=1
        self.rgb                = {'black': [0,0,0]}
        self.rgb['white']       = [255,255,255]
        self.rgb['move_box']    = (179,223,245)
        self.rgb['target_box']  = (59,181,45)
        self.rgb['lineStkClr']  = [67,86,102]

        # Trial info
        self.trials_level1  = np.zeros((self.nTrials,2))
        self.trials_level2  = np.zeros((self.nTrials,2))
        level1_options      = [[0,1],[0,-1],[-1,0],[1,0]]
        for trial in range(self.nTrials):
            self.trials_level1[trial,:] = level1_options[random.randint(0,3)]
            level2_selection = [random.randint(-self.radius,self.radius),random.randint(-self.radius,self.radius)]
            if level2_selection == [0,0]:
                self.trials_level2[trial,0] = random.randint(-self.radius,self.radius)
                self.trials_level2[trial,1] = random.randint(-self.radius,self.radius)
            else:
                self.trials_level2[trial,:] = level2_selection

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
        for i in range(self.nBoxes+1):
            # Horizontal stripes
            self.screen.drawLine(int(self.xyGridPos[0,0]),
                                 int(self.xyGridPos[i,1]),
                                 int(self.xyGridPos[0,0]+self.gridLen),
                                 int(self.xyGridPos[i,1]))
            # Vertical stripes
            self.screen.drawLine(int(self.xyGridPos[i,0]),
                                 int(self.xyGridPos[0,1]),
                                 int(self.xyGridPos[i,0]),
                                 int(self.xyGridPos[0,1]+self.gridLen))

    def drawBoxes(self):
        self.target = self.screen.drawRect(self.x_center, self.y_center,
                                           self.box_size, self.box_size,
                                           color=self.rgb['target_box'],fill=True)
        self.box = self.screen.drawRect(self.x_center, self.y_center,
                                        self.box_size, self.box_size,
                                        color=self.rgb['move_box'],fill=True)

    def moveBox(self, box, x_step, y_step):
        if x_step:
            box.vertices[::2] = [i + int(x_step)*self.box_size for i in box.vertices[::2]]
        if y_step:
            box.vertices[1::2] = [i + int(y_step)*self.box_size for i in box.vertices[1::2]]

    def trialAdvance(self):
        # ---------------- RESETS --------------- #
        self.moveBox(self.target,
            self.trials_level1[self.trialIdx,0] - self.trials_level2[self.trialIdx-1,0],
            self.trials_level1[self.trialIdx,1] - self.trials_level2[self.trialIdx-1,1])
        self.moveBox(self.box, -self.cursor[0], -self.cursor[1])
        self.cursor         = [0,0]
        self.trial_nMoves   = 0
        self.current_level  = self.levels[0]
        self.sock.sendto(str(1),('127.0.0.1',33448))
        self.trialtotaltime = -self.ISI

    def targetCheck(self):
        print self.cursor
        print self.trials_level1[self.trialIdx,:]

        # MAIN GRID MENU
        if self.current_level == self.levels[0]:
            if self.cursor[0] == int(self.trials_level1[self.trialIdx,0]) and\
               self.cursor[1] == int(self.trials_level1[self.trialIdx,1]):
                self.current_level = self.levels[1]
                self.moveBox(self.target,
                    self.trials_level2[self.trialIdx,0] - self.trials_level1[self.trialIdx,0],
                    self.trials_level2[self.trialIdx,1] - self.trials_level1[self.trialIdx,1])
                self.moveBox(self.box, -self.cursor[0], -self.cursor[1])
                self.cursor = [0,0]
        # ALL OTHER TOPIC GRIDS
        else:
            if self.cursor == [0,0]:
                pass
#                self.current_level = self.levels[0]
#                self.moveBox(self.target,
#                    self.trials_level1[self.trialIdx,0] - self.trials_level2[self.trialIdx,0],
#                    self.trials_level1[self.trialIdx,1] - self.trials_level2[self.trialIdx,1])
            else:
                # target acquire check!
                if self.cursor[0] == int(self.trials_level2[self.trialIdx,0]) and \
                   self.cursor[1] == int(self.trials_level2[self.trialIdx,1]):
                    # write TRIAL STATS to file
                    current_stats = [self.trialIdx,self.trialtotaltime,self.trial_nMoves]
                    self.run_stats.write(str(current_stats)+"\n")
                    self.trialIdx += 1
                    # EXIT program and SAVE data to file
                    if self.trialIdx == self.nTrials:
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
                    current_data = [self.trialIdx, self.runtotaltime, self.trials_level1[self.trialIdx,:], \
                                    self.trials_level2[self.trialIdx,:]]+ d[1:4]
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
            #self.controller.stimulus.stop()
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
                self.moveBox(self.target, self.trials_level1[0,0], self.trials_level1[0,1])
                self.cue_text.delete()
                #self.controller.stimulus.start()
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
        if decision: self.trial_nMoves+=1

        # DECISION (move)
#        if decision == 1 and self.cursor[1] < 1:
#            self.cursor = [0,0]
##            self.cursor[1] += 1
#            self.moveBox(self.box, 0, 1)
#        elif decision == 2 and self.cursor[1] > -1:
#            self.cursor = [0,0]
##            self.cursor[1] -= 1
#            self.moveBox(self.box, 0, -1)
#        elif decision == 3 and self.cursor[0] > -1:
#            self.cursor = [0,0]
##            self.cursor[0] -= 1
#            self.moveBox(self.box, -1, 0)
#        elif decision == 4 and self.cursor[0] < 1:
#            self.cursor = [0,0]
##            self.cursor[0] += 1
#            self.moveBox(self.box, 1, 0)
        if self.current_level == self.levels[0]:
            if decision==1:
                if self.cursor == [0,0]:
                    self.moveBox(self.box, 0, 1)
                elif self.cursor == [0,-1]:
                    self.moveBox(self.box, 0, 2)
                elif self.cursor == [-1,0]:
                    self.moveBox(self.box, 1, 1)
                elif self.cursor == [1,0]:
                    self.moveBox(self.box, -1, 1)
                self.cursor = [0,1]
            if decision==2:
                if self.cursor == [0,0]:
                    self.moveBox(self.box, 0, -1)
                elif self.cursor == [1,0]:
                    self.moveBox(self.box, -1, -1)
                elif self.cursor == [-1,0]:
                    self.moveBox(self.box, 1, -1)
                elif self.cursor == [0,1]:
                    self.moveBox(self.box, 0, -2)
                self.cursor = [0,-1]
            if decision==3:
                if self.cursor == [0,0]:
                    self.moveBox(self.box, -1, 0)
                elif self.cursor == [0,1]:
                    self.moveBox(self.box, -1, -1)
                elif self.cursor == [1,0]:
                    self.moveBox(self.box, -2, 0)
                elif self.cursor == [0,-1]:
                    self.moveBox(self.box, -1, 1)
                self.cursor = [-1,0]
            if decision==4:
                if self.cursor == [0,0]:
                    self.moveBox(self.box, 1, 0)
                elif self.cursor == [0,1]:
                    self.moveBox(self.box, 1, -1)
                elif self.cursor == [-1,0]:
                    self.moveBox(self.box, 2, 0)
                elif self.cursor == [0,-1]:
                    self.moveBox(self.box, 1, 1)
                self.cursor = [1,0]
                print self.cursor
                print "yo"

        elif self.current_level == self.levels[1]:
            if decision == 1 and self.cursor[1] < self.radius:
                self.cursor[1] += 1
                self.moveBox(self.box, 0, 1)
            elif decision == 2 and self.cursor[1] > -self.radius:
                self.cursor[1] -= 1
                self.moveBox(self.box, 0, -1)
            elif decision == 3 and self.cursor[0] > -self.radius:
                self.cursor[0] -= 1
                self.moveBox(self.box, -1, 0)
            elif decision == 4 and self.cursor[0] < self.radius:
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
#        if (self.trialtotaltime < 0.0) and (self.trialIdx < self.nTrials):
#            self.drawCue("Ready?")
#        # GRID
#        else:
#            if self.trialIdx < self.nTrials:
#                self.drawGridLines()
#                self.drawBoxTarget()
#                self.drawBox()
#            else:
#                self.drawCue("Run complete.")
