__author__ = "Dante Smith"
__copyright__ = "Copyright 2012, Neural Prosthesis Laboratory"
__credits__ = ["Jonathan Brumberg", "Byron Galbraith", "Sean Lorenz", "Anthony Rinaldi"]
__license__ = "GPL"
__version__ = "0.1"
__email__ = "npl@bu.edu"
__status__ = "Development"

from core import UnlockApplication
import numpy as np

class SpectrumScope(UnlockApplication):
    """
    A 2-D plot displaying the relative magnitude of the FFT taken from recorded EEG data

    This program takes in one or multiple channels of voltage data, converts each channel
    from the time domain to the frequency domain, and plots each as a function of Magnitude
    vs. Frequency.

    :param screen:   Window Size
    :param freqs:    The frequencies being used for stimulation.
    :param numchan:  Number of channels expected in output buffer
    :param labels:   Labels for the channels
    :param duration: Sampling time
    :param fs:       Sampling rate
    :param magYlim:  set limits for data channel amplitudes
    :param refresh:  update rate for plotter
    :param mode:     whether to update ylim after every <duration> cycle
    :param debug:    Using real-time data or random data for testing
    :param graph:    Outputs the graph either as power spectrum(pwr) or HSD(hsd)
    :param mag:      Graphs power output as either tha absolute value('abs') or log in decibels ('dB')
    :param decodeInfo: Variables and modules for decoding time-series data
    """

    name = "SpectrumScope"
    gets_samples = True

    def __init__(self, screen, numchan=1, labels=None, dur=2, fs = 256,
                 magYlim = (-90,200), refresh = 5, mode = 'auto', debug =False,
                 graph='pwr', mag='abs', decoder=False):

        super(self.__class__, self).__init__(screen)


        self.width = screen.get_width()
        self.height = screen.get_height()
        self.size = screen.get_size()

        self.white  = (255,255,255)
        self.white2 = (255,255,255,255)
        self.red    = (128,0,0,255)
        self.red2   = (128,0,0)
        self.green  = (0,128,0,255)
        self.green2 = (0,128,0)
        self.blue   = (0,0,255,255)
        self.blue2  = (0,0,255)
        self.gray75 = tuple([x*255. for x in [.75,.75,.75,1.]])

        self.numchan  = numchan
        self.dur      = dur
        self.fs       = fs
        self.numsamp  = dur * fs
        self.y        = np.zeros([self.numchan, self.numsamp])
        self.buf      = np.zeros([self.numchan, self.numsamp])
        self.debug    = debug
        self.decoder  = decoder

        if self.decoder:
            self.h        = self.decoder      #info for HSD decoders
            self.mag      = mag
            self.harmSums = np.zeros(10)
        else:
            self.h        = 0


        self.graph = graph

#        self.freqs    = freqs

        self.index    = 0
        self.space    = {'x':0.05,'y':0.10}

        ## x range values
        self.freqRange = [0,30]
        self.dataRange = [0,self.numsamp]

        ##y range values
        PhaYlim      = [-np.pi,np.pi]
        self.magYlim = magYlim

        self.xlim   = (self.space['x']*self.size[0],(1-self.space['x'])*self.size[0])
        self.xpixL  = self.xlim[1]-self.xlim[0]
        self.xLength   = self.freqRange
        #self.xLength=[self.freqRange, self.dataRange]

        self.ylim   = (self.space['y']*self.size[1],(1-self.space['y'])*self.size[1])
        self.ypixL  = self.ylim[1]-self.ylim[0]
        self.yLength = [self.magYlim, PhaYlim]

        self.axisH = self.ylim[0]+10
        self.yTick = [self.axisH-10, self.axisH+10]
        self.yText = self.yTick[0]-10

        self.dataLbl   = ['Ch 1:', 'Ch 2:', 'Ch 3:']
        self.dataLblcolor = [self.red, self.green, self.blue ]
        self.datacolor = [self.red2, self.green2, self.blue2]

        self.indicatorW  = 10
        self.indicatorH  = 20
        self.selYloc     = self.axisH-self.indicatorH/2
        self.selectorhv  = [30, 20, 10]

        self.refresh      = refresh
        self.mode         = mode
        self.refresh_time = 0
        self.scale_time   = 0
        self.scale        = 1
        self.shift        = 0
        self.rescale      = 100.0
        #==============================
        self.minfreq = []
        self.sumavg  = []
        #==============================

        #draw axes
        self.screen.drawLine(self.xlim[0], self.axisH, self.xlim[1], self.axisH, self.white)
        for i in range(self.xLength[0],self.xLength[1]+1,1):
            self.screen.drawLine(self.screenMapX(i),self.yTick[0], self.screenMapX(i),self.yTick[1], color= self.white)

        #draw tick mark text
        for i in range(self.xLength[0],self.xLength[1]+1,self.xLength[1]/15):
            self.screen.drawText(str(i), self.screenMapX(i),self.yText, size=10, color=self.white)

        #draw selected frequency marker
        self.freqIndi=self.screen.drawRect(self.xlim[0]-self.indicatorW/2,self.selYloc,self.indicatorW, self.indicatorH,self.white, fill=True)

        #draw data labels
        self.peakVal=np.zeros(self.numchan)
        for i in range(self.numchan):
            self.screen.drawText(self.dataLbl[i],self.size[0]/(self.numchan+1)*(i+1), self.ylim[1],size=15, color=self.dataLblcolor[i])
#            self.peakVal[i]=self.screen.drawText('0.00',self.size[0]/(self.numchan+1)*(i+1)+30, self.ylim[1],size=15, color=self.dataLblcolor[i])

        #draw data
        self.plots = []
        if labels is None:
            labels = map(str,range(1,numchan+1))
        for i in range(numchan):
            if self.h:
                trace = zip(self.screenMapX(self.h.f[0:60]),self.screenMapY(self.buf[i][0:60],i))
            else:
                trace = np.zeros([2,60])

            self.plots.append(screen.drawLinePlot([point for points in trace for point in points],color=self.datacolor[i]))

        # draw max value indicator
#        self.stimVal = self.screen.drawText('0.00',self.width/3,   20, size=15)
#        self.peakVal = np.zeros(len(self.numsamp))

    def screenMapX(self,x):
        """Sets scale for length of data with number of pixels on screen

        :param x: x-coordinate(s) of data value. Can be list of x values, or a single value.
        :returns: Converted x-coordinates to pixels on screen"""
        xlim= self.xLength
        rat = self.xpixL/float(xlim[1]-xlim[0])
        try:
            return [xi*rat + self.xlim[0] for xi in x]
        except TypeError:
            return x*rat + self.xlim[0]
        except:
            return x

    def screenMapY(self,y, ii=0):
        """Sets scale for length of data with number of pixels on screen

        :param y: y-coordinate(s) of data value. Can be list of x values, or a single value.
        :param ii: optional. integer spacing for multiple data values
        :returns: Converted y-coordinates to pixels on screen"""
        off = self.space['y']*self.height
        h=(self.height-(self.numchan+1)*off)#/float(self.numchan)
        rat = h/float(self.ylim[1]-self.ylim[0])

        yoff = off+self.axisH+25
        try:
            if self.mode == 'auto':
                y = (y - self.shift) / self.scale
            return [yi*rat + yoff for yi in y]
            #return map(lambda yi: (yi)*rat + yoff-h/2., y)
        except TypeError:
            return y*rat + yoff
        except:
            return y

    def pushBuffer(self,data):
        """ Pushes incoming data onto the plotting buffer.

        :param data: incoming data, assumed to be interleaved
        """
        if data is None:
            return
            # Get length of incoming data
        length = len(data) / self.numchan
#        self.logger.debug('Packet length: %d (%d chan, %d samp)' %
#                          (len(data),self.numchan,length))

        # create index list for buffers (internal buffer is circular)
        idx = [x % self.numsamp for x in range(self.index,self.index+length)]

        # Check if data lengths per expected channels match
        if length * self.numchan != len(data):
            pass #self.logger.warning('Incoming data does not have correct shape, not updated')
        else:
#            self.logger.debug('Writing new packet')
            self.y = np.roll(self.y,-length,axis=1)
            for i in range(0,self.numchan):
                lidx = range(i,len(data),self.numchan)
                for j in range(0,length):
                    self.y[i][-length:] = data[lidx[j]]
                if self.h:
                    self.buf[i,:] = self.h.decode(self.y[i],self.mag)


#                trialSeg = self.h.preproc(self.y[i])        # Trial segment signal preprocessing
#                if self.mag == 'abs':
#                    self.buf[i,:]  = np.abs(np.fft.fft(trialSeg,self.h.nfft)) # abs of FFT
#                elif self.mag == 'dB':
#                    self.buf[i,:]  = 10*np.log(abs(np.fft.fft(trialSeg,self.h.nfft))) # abs of FFT
#

            self.index += length


    def update(self, dt, decision, selection):
        """Updated with every new decision or selection.

        :param dt: Time step
        :param decision: Decision for the app. Usually 0-3(4 decisions) for directional movement
        :param selection: Either 0 or 1.
        """

        self.refresh_time += dt
        if self.refresh_time > 1.0/self.refresh:
#            self.cursor.vertices[::2] = [self.screen.x + self.screenMapX(self.index%self.numsamp) for i in self.cursor.vertices[::2]]
            for i in range(self.numchan):
                if self.graph == 'pwr':
                    self.plots[i].updateData(self.screenMapY(self.buf[i][0:60],i))
#                self.peakVal[i].text=str(self.h.f[np.argmax(self.buf[i,0:self.fs/2])])
            self.refresh_time = 0

        self.scale_time += dt
        if self.scale_time > self.dur:
            max = np.max(self.buf)
            scale = np.round(0.5*(max - np.min(self.buf)),2)
            shift = max - scale
            if scale != 0:
                if 0.9*self.scale < scale/self.rescale < 1.1*self.scale:
                    pass
                else:
                    self.scale = scale/self.rescale
                if 0.9*self.shift < shift < 1.1*self.shift:
                    pass
                else:
                    self.shift = shift

            self.scale_time = 0


    def sample(self, data):
        """
        Collects data from socket, and sends it to pushBuffer. If debug mode is turned on
        generates random test data

        :param data: data collected by socket buffer.
        """
        if self.debug:
            self.pushBuffer(np.random.random(self.numchan))
            return

        if data is None:
            return

        data = [sample for samples in data for sample in samples]
        self.pushBuffer(data)

    def moveFreqIndi(self,freq):
        """
        Graphical representation of current stimulating frequency.

        :param freq: the frequency currently being outputed by the frequency selector
        """
        newSpot=self.screenMapX(freq )
        oldSpot=self.freqIndi.vertices[0]
        self.moveBox(self.freqIndi,(newSpot-oldSpot),0)

    def moveBox(self, box, x_step, y_step):
        """
        Moves the frequency slider along the X axis

        :param box: name of pygame rectangle to be moved
        :x_step
        """
        if x_step:
            box.vertices[::2] = [i + int(x_step) + self.screen.x - self.indicatorW/2 for i in box.vertices[::2]]
        if y_step:
            box.vertices[1::2] = [i + int(y_step) for i in box.vertices[1::2]]



#    def drawGuess(self):
#        self.minfreq = []
#        for i in range(self.numchan):
#            ten30=self.buf[i,40:120]
#            mini=np.argmin(ten30)+40
##            mini = min(xrange(len(ten30)), key=ten30.__getitem__)+40
#            #======================
#            self.minfreq.append(self.basicfft.f[mini])
##            self.minfreq = self.minfreq + self.basicfft.f[mini]
#            #======================
##            if i==0:
##                print self.basicfft.f[mini]
#            guessRec=pygame.Rect(self.screenMapX(self.basicfft.f[mini],1)-self.selectorW/2, self.selYloc ,self.selectorW, self.selectorhv[i])
#            pygame.draw.rect(self.screen,self.datacolor[i],guessRec)
