__author__ = "Dante Smith"
__copyright__ = "Copyright 2012, Neural Prosthesis Laboratory"
__credits__ = ["Jonathan Brumberg", "Byron Galbraith", "Sean Lorenz"]
__license__ = "GPL"
__version__ = "0.1"
__email__ = "npl@bu.edu"
__status__ = "Development"

from unlock.core import UnlockApplication

class FreqButton(UnlockApplication):
    """
    Buttons for selecting frequency of flash rate

    This app takes in a set of frequency rates and arranges them in
    a grid. The technician can select a frequency to be the frequency
    of the stimulus that is presented to the subject. It requires a
    SSVEP stimulus variable to be passed to the script. An optional
    variable for spectrum scope variable can be passed to the script
    so that an indicator moves on the Spectrum Scope

    :param screen: Screen which to draw grid to
    :param freqs: List of frequency values to be displayed as floats
    :param stimulus: The stimulus you wish to control with buttons
    :param spectrum: the spectrum scope object you are using if it includes
              an expected frequency indicator

    """
    name = "Frequency Selector"

    def __init__(self, screen, freqs, stimulus, Spectrum=None):

        super(self.__class__, self).__init__(screen)
        self.x = screen.x + screen.width / 2
        self.y = screen.y + screen.height / 2
        self.stimulus      = stimulus
        self.SpectrumScope = Spectrum
        self.stimulus.stop()
        self.white  = (255,255,255)
        self.white2 = (255,255,255,255)
        self.black  = (0,0,0)
        self.green  = (0,255,0)
        self.red    = (255,0,0,255)

        self.freqs = freqs

        self.fLen      = len(self.freqs) #well used variable
        self.cursor    = [0,1]
        self.imhere    = 0
        self.pastSel   = -1
        self.flashFreq = 0

        self.box_d = 100 #dimension of each box

        self.lbuff = (self.screen.get_width()-self.box_d*5)/2 #change the box position
        self.tbuff = (self.screen.get_height()-self.box_d*2)/2 #change the text position

        self.shR   = 0.45 #change the text H position
        self.shD   = 0.45 #change the text V position

        self.text  = [0]*self.fLen#coordinates of text

        for i in range(0,3):#horizontal lines
            self.screen.drawLine(self.lbuff, self.tbuff+self.box_d*i, self.lbuff+self.box_d*5,self.tbuff+self.box_d*i,
                                self.white)
        for j in range(0,6):#vertical lines
            self.screen.drawLine(self.lbuff+self.box_d*j,self.tbuff,self.lbuff+self.box_d*j, self.tbuff+self.box_d*2,
                                self.white)

        for i in range(0,self.fLen):
            if i<(self.fLen/2):#first row
                self.text[i] = screen.drawText(str(self.freqs[i]),
                            self.lbuff + self.box_d*(i+ self.shR), self.tbuff + self.box_d*(self.shD+1),
                            size=20, color=self.white)
            else:#second row
                self.text[i] = screen.drawText(str(self.freqs[i]),
                            self.lbuff + self.box_d*(i+ self.shR-self.fLen/2), self.tbuff + self.box_d*self.shD,
                            size=20, color=self.white)

        self.curRec = screen.drawRect(self.lbuff+2, self.tbuff+2+self.box_d,self.box_d-4,self.box_d-4,color=self.green)

    def moveBox(self, box, x_step, y_step):
        """
        Moves the square cursor around the grid. Allows items to be selected

        :param box: Variable name of pyglet rectangle to move
        :param x_step: Amount of step sizes to move horizontally. Either positive or negative
        :param y_step: Number of step sizes to move vertically. Either Positive or negative
        """
        if x_step:
            box.vertices[::2]  = [i + int(x_step)*self.box_d for i in box.vertices[::2]]
        if y_step:
            box.vertices[1::2] = [i + int(y_step)*self.box_d for i in box.vertices[1::2]]

    def update(self, dt, decision, selection):
        """Updated with every new decision or selection.

        :param dt: Time step
        :param decision: Decision for the app. Usually 0-3(4 decisions) for directional movement
        :param selection: Either 0 or 1.
        """
        if decision is not None:
            if decision == 1 and self.cursor[1] < 1:
                self.cursor[1] += 1
                self.moveBox(self.curRec, 0, 1)
                self.imhere=self.imhere-5
            elif decision == 2 and self.cursor[1] > 0:
                self.cursor[1] -= 1
                self.moveBox(self.curRec, 0, -1)
                self.imhere=self.imhere+5
            elif decision == 3 and self.cursor[0] > 0:
                self.cursor[0] -= 1
                self.moveBox(self.curRec, -1, 0)
                self.imhere -= 1
            elif decision == 4 and self.cursor[0] < 4:
                self.cursor[0] += 1
                self.moveBox(self.curRec, 1, 0)
                self.imhere += 1

        if selection:
            if self.imhere==self.pastSel :
                self.text[self.imhere].color = self.white2
                self.pastSel=-1
                self.stimulus.stop()
                if self.SpectrumScope is not None:
                    self.SpectrumScope.moveFreqIndi(float(0))
            else:
                self.text[self.pastSel].color = self.white2
                self.text[self.imhere].color  = self.red
                self.pastSel = self.imhere
                self.stimulus.changeFrequencies([float(self.freqs[self.imhere])])
                self.stimulus.start()
                if self.SpectrumScope is not None:
                    self.SpectrumScope.moveFreqIndi(float(self.freqs[self.imhere]))
        return self.flashFreq