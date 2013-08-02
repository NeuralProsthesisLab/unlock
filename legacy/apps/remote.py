__author__ = "Dante Smith"
__copyright__ = "Copyright 2012, Neural Prosthesis Laboratory"
__credits__ = ["Jonathan Brumberg", "Byron Galbraith", "Sean Lorenz"]
__license__ = "GPL"
__version__ = "0.1"
__email__ = "npl@bu.edu"
__status__ = "Development"

from unlock.core import UnlockApplication
import serial
import socket

class BCIRemote(UnlockApplication):
    """
    A TV remote interface with buttons for 0-9, power, channel up and down,
    volume up and down, and favorite channel. The menu can be navigated by
    arrow keys for testing and a selection is determined by the space bar.
    These commands send a one character code through a COM port to an Arduino
    IR Remote. currently, our IR code transceivers only function with Sony TV.
    There is also functionality in the Arduino code for servos to move the base
    of the remote for panning and tilting. Full functionality of this feature
    is not done in this version.

    :param screen: Window Size
    :param comP: COM Port+1 where the IR transceiver is plugged in, if any.
    """

    name = "Remote"
    icon = "tv.png"

    def __init__(self,screen, comP=4):

        super(self.__class__, self).__init__(screen)

        self.size=screen.get_size()#dimensions of outerbox
        self.tlC   =  [255,255,255]
        self.curCol=  [0,255,0]
        self.red   =  [255,0,0,255]
        self.state = 'Function'
        self.laserOn = True

#        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM )
#        self.sock.bind(('localhost',33445))
#        self.sock.settimeout(.01)

        EIGHTBITS=serial.EIGHTBITS
        #check arduino program for port
        try:
            self.port=serial.Serial(port = comP,baudrate=9600,bytesize=EIGHTBITS)
            self.port.write('l')
        except:
            warning='INSERT ARDUINO INTO CORRECT COM PORT!'
            self.screen.drawText(warning, self.size[0]/2, self.size[1]-20, size=14, color=self.red)
            self.port=None

        phraseLoc=self.resource_path

        self.parScr = {'w':self.size[0]/2,
                       'h':self.size[1]*4/5,
                       'sx':self.size[0]/2/3,
                       'sy':self.size[1]*4/5/7,
                       'tw':80,
                       'th':120}#dimensions of images

        self.buffX = (self.size[0]-self.parScr['w'])/2
        self.buffY = (self.size[1]-self.parScr['h'])/2

        textbuffX=self.parScr['sx']*.5
        textbuffY=self.parScr['sy']*.5

        #draw lines
        for i in range(0,self.parScr['w']+self.parScr['sx'],self.parScr['sx']):
            self.screen.drawLine(i+self.buffX,self.buffY,i+self.buffX,self.parScr['h']+self.buffY,self.tlC)
        for i in range(0,self.parScr['h']+self.parScr['sy'],self.parScr['sy']):
            self.screen.drawLine(self.buffX,i+self.buffY,self.parScr['w']+self.buffX,i+self.buffY,self.tlC)

        #draw function cursor
        self.cursor=[1,5]
        self.imhere=16
        self.cur=self.screen.drawRect(self.parScr['sx']*self.cursor[0]+self.buffX+2,self.parScr['sy']*self.cursor[1]+self.buffY+2,self.parScr['sx']-4,self.parScr['sy']-4,self.curCol)
        self.start=self.cur.vertices[:]

        #draw arrows
        self.arrowU=self.screen.loadSprite((phraseLoc + 'Arrow.png'),self.size[0]/2, self.size[1]/2+self.parScr['th'])
        self.arrowD=self.screen.loadSprite((phraseLoc + 'Arrow.png'),self.size[0]/2, self.size[1]/2-self.parScr['th'])
        self.arrowL=self.screen.loadSprite((phraseLoc + 'Arrow.png'),self.size[0]/2+self.parScr['th'], self.size[1]/2)
        self.arrowR=self.screen.loadSprite((phraseLoc + 'Arrow.png'),self.size[0]/2-self.parScr['th'], self.size[1]/2)
        self.center=self.screen.loadSprite((phraseLoc +'LazerToggle.png'),self.size[0]/2, self.size[1]/2)

        self.arrowD.rotation = 180.0
        self.arrowL.rotation = 090.0
        self.arrowR.rotation = 270.0

        self.arrowU.visible = False
        self.arrowD.visible = False
        self.arrowL.visible = False
        self.arrowR.visible = False
        self.center.visible = False

        #draw movement cursor
        self.arrowPos= [0,0]
        self.servo = 5

        #reading in text file
        self.irCodes = {'comm':[],'coord':[],'code':[]}
        self.FileLoc = phraseLoc + 'IRCodes.txt'

        with open(self.FileLoc,'r') as fd:
            for line in fd:
                el=line.strip().split('\t')
                self.irCodes['comm'].append(el[0])
                self.irCodes['coord'].append(tuple((int(el[1]),int(el[2]))))
                self.irCodes['code'].append(el[3]) #phraseLoc + el[3])
                self.irCodes['comm'][0] = 'ENTER'

        self.remoteText=[0]*21

        #Draw Text
        for i in range(0,len(self.irCodes['comm'])):
            comm = self.irCodes['comm'][i]
            coord = self.irCodes['coord'][i]
            xcoord = self.parScr['sx']*(coord[0]) + self.buffX + textbuffX
            ycoord = self.parScr['sy']*(coord[1]) + self.buffY + textbuffY
            self.remoteText[i]=self.screen.drawText(comm, xcoord, ycoord, size=12)

    def update(self, dt, decision, selection):
        """
        Updated with every new decision or selection.

        :param dt: Time step
        :param decision: Decision for the app. Usually 0-3(4 decisions) for directional movement
        :param selection: Either 0 or 1.

        If there is a decision, update checks the current state, and moves the
        cursor around the screen in the appropriate direction for the appropriate state
        If there is a selection, update checks the current state, and activates the function
        or movement that has been selected. This is done by running either the sendCode or
        """
        if decision is not None:
            if self.state == 'Function':
                if decision == 1 and self.cursor[1] < 6:
                    self.cursor[1] += 1
                    self.moveBox(self.cur, 0, 1)
                    self.imhere=self.imhere+3
                elif decision == 2 and self.cursor[1] > 0:
                    self.cursor[1] -= 1
                    self.moveBox(self.cur, 0, -1)
                    self.imhere=self.imhere-3
                elif decision == 3 and self.cursor[0] > 0:
                    self.cursor[0] -= 1
                    self.moveBox(self.cur, -1, 0)
                    self.imhere -= 1
                elif decision == 4 and self.cursor[0] < 2:
                    self.cursor[0] += 1
                    self.moveBox(self.cur, 1, 0)
                    self.imhere += 1
            elif self.state =='Movement':
                pass #Move Arrows


        if selection:
            if self.state == 'Function':
               if self.imhere == 2:
                    self.switchState()
               else:
                    self.sendCode()
            elif self.state == 'Movement':
                if self.servo == 5:
                    self.switchState()
                else:
                    self.moveLazer()

    def moveBox(self, box, x_step, y_step):
        """Moves box by n x_step or y_step. x_step and y_step are
            defined by the height of the grid elements"""
        if x_step:
            box.vertices[::2] = [i + int(x_step)*self.parScr['sx'] for i in box.vertices[::2]]
        if y_step:
            box.vertices[1::2] = [i + int(y_step)*self.parScr['sy'] for i in box.vertices[1::2]]

    def sendCode(self):
        """
        Transmits one character code to COM port designated in beginning of program
        """
        code = self.irCodes['code'][self.imhere]
        if self.imhere !=18:
            if self.port: self.port.write(code)
            if self.imhere == 0 : #enter key
                self.cur.vertices=self.start
                self.cursor=[1,5]
                self.imhere=16
        elif self.imhere == 18 : #Prev Menu
            if self.port: self.port.write('l')
            self.laserOn = True
            self.close()

    def moveLazer(self):
        """When run, checks the value of self.servo and outputs correct arduino command """
        if self.servo==1 :
            self.port.write('U')
        elif self.servo==2 :
            self.port.write('D')
        elif self.servo==3 :
            self.port.write('L')
        elif self.servo==4 :
            self.port.write('R')

    def switchState(self):
        """
        Switch between remote Function state and remote Movement State

        Relies on self.state variable. Turns on and off commands and abilities
        depending on value of self.state.

        """
        if self.state=='Function': #switch to Movement
            newState='Movement'
            self.arrowU.visible = True
            self.arrowD.visible = True
            self.arrowL.visible = True
            self.arrowR.visible = True
            self.center.visible = True

            for i in range(0,len(self.remoteText)):
                self.remoteText[i].visible = False
            self.servo = 5
        else : #switch to Function
            newState ='Function'
            self.arrowU.visible = False
            self.arrowD.visible = False
            self.arrowL.visible = False
            self.arrowR.visible = False
            self.center.visible = False

            for i in range(0,len(self.remoteText)):
                self.remoteText[i].visible = True
        self.state=newState