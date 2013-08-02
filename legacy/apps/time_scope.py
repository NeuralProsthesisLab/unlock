from unlock.core import UnlockApplication
import numpy as np

class TimeScope(UnlockApplication):
    """ Class to output contents of a multidimensional list [chan x time]
    to a line plot - yvals are inverted

    :param screen: Window Size
    :param numchan: number of channels expected in output buffer
    :param labels: Labels for the channels
    :param duration: Sampling time in seconds
    :param fs:       Sampling rate of data
    :param ylim:     set limits for data channel amplitudes
    :param refresh:  update rate for plotter
    :param mode:     whether to update ylim after every <duration> cycle
    :param debug:    Using real-time data or random data for testing
     """
    name = "Time Scope"
    gets_samples = True

    def __init__(self, screen, numchan=1, labels=None, duration=2, fs=256,
                 ylim=(-100,100), refresh=33, mode='auto', debug=False):
        """TimeScope initialization"""

        super(self.__class__, self).__init__(screen)

        self.width = screen.get_width()
        self.height = screen.get_height()
        self.black = (0,0,0,1)
        self.gray25 = tuple([x*255. for x in [.75,.75,.75,1.]])
        self.gray50 = (127,127,127,255)
        self.gray75 = tuple([x*255. for x in [.75,.75,.75]])
        self.white = (255,255,255,255)
        self.red = (255,0,0)

        self.numchan = numchan
        self.dur = duration
        self.fs = fs
        self.numsamp = duration * fs
        self.buf = np.zeros((numchan, self.numsamp))
        self.debug = debug

        self.index = 0

        self.space = {'x':0.05,'y':0.05}

        self.xlim = (self.space['x']*self.width,(1-self.space['x'])*self.width)
        self.ylim = ylim
        self.refresh = refresh
        self.mode = mode
        self.refresh_time = 0
        self.scale_time = 0
        self.scale = 1
        self.shift = 0
        self.rescale = 100.0

        self.cursor = screen.drawLine(self.screenMapX(self.index%self.numsamp),
                                      self.space['y']*self.height,
                                      self.screenMapX(self.index%self.numsamp),
                                      (1-self.space['y'])*self.height,
                                      color=self.red)

        self.plots = []
        if labels is None:
            labels = map(str,range(1,numchan+1))
        for i in range(numchan):
            trace = zip(self.screenMapX(range(0,self.numsamp)),self.screenMapY(self.buf[i][:],i))
            self.plots.append(screen.drawLinePlot([point for points in trace for point in points],color=(192,192,192)))
            screen.drawText(labels[i], self.screenMapX(-20),
                            self.screenMapY(0,i), size=16)

#    def onOpen(self, kwargs):
#        self.controller.current_stimulus.stop()
    def screenMapX(self,x):
        """Sets scale for length of data with number of pixels on screen

        :param x: x-coordinate(s) of data value. Can be list of x values, or a single value.
        :returns: Converted x-coordinates to pixels on screen"""
        xlim = (0,self.numsamp)
        rat = (self.xlim[1]-self.xlim[0])/float(xlim[1]-xlim[0])
        try:
            return [xi*rat + self.xlim[0] for xi in x]
            #return map(lambda xi: xi*rat + self.xlim[0], x)
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
        h=(self.height-(self.numchan+1)*off)/float(self.numchan)
        rat = h/float(self.ylim[1]-self.ylim[0])

        yoff = self.height-(ii+1)*off-ii*h
        try:
            if self.mode == 'auto':
                y = (y - self.shift) / self.scale
            return [yi*rat + yoff-h/2. for yi in y]
            #return map(lambda yi: (yi)*rat + yoff-h/2., y)
        except TypeError:
            return y*rat + yoff-h/2.
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
            for i in range(0,self.numchan):
                lidx = range(i,len(data),self.numchan)
                for j in range(0,length):
                    self.buf[i][idx[j]] = data[lidx[j]]

            self.index += length

    def update(self, dt, decision, selection):
        """Updated with every new decision or selection.

        :param dt: Time step
        :param decision: Decision for the app. Usually 0-3(4 decisions) for directional movement
        :param selection: Either 0 or 1.
        """

        self.refresh_time += dt
        if self.refresh_time > 1.0/self.refresh:
            self.cursor.vertices[::2] = [self.screen.x + self.screenMapX(self.index%self.numsamp) for i in self.cursor.vertices[::2]]
            for i in range(self.numchan):
                self.plots[i].updateData(self.screenMapY(self.buf[i][:],i))
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

#        if selection:
#            self.close()

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


#    def draw(self):
#        # restrict frame rate
#        #self.clock.tick(self.refresh) # max 33 updates per second
#        self.screen.fill(self.black)
#
#        # do drawing of each channel
#        for chanidx in range(0,self.numchan):
#            pygame.draw.aalines(self.screen, self.gray75, False,
#                                zip(self.screenMapX(range(0,self.numsamp)),
#                                    self.screenMapY(self.buf[chanidx][:],
#                                                    chanidx)),1)
#            pygame.draw.aaline(self.screen, self.red,
#                               (self.screenMapX(self.index%self.numsamp),
#                                self.space['y']*self.height),
#                               (self.screenMapX(self.index%self.numsamp),
#                                (1-self.space['y'])*self.height),1)
#
#            text = self.chanfont.render(self.chanLabels[chanidx],True,self.white)
#            self.screen.blit(text,[self.screenMapX(-15),
#                                   self.screenMapY(0,chanidx)])
#            #text = self.timefont.render("0",True,self.white)
#            #self.screen.blit(text,[self.space['x']*self.width,
#            #                       self.height-self.space['y']*.5*self.height])
#            #text = self.timefont.render(str(self.dur),True,self.white)
#            #self.screen.blit(text,[(1-self.space['x'])*self.width,
#            #                       self.height-self.space['y']*.5*self.height])
