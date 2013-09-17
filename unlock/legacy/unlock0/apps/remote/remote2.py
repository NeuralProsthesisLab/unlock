from settings import *
from core import UnlockApplication
import pygame
import serial
import socket

pygame.init()

class BCIRemote(UnlockApplication):

    name = "Remote"

    def __init__(self,screen):
        self.screen = screen 
        self.bg= [0,0,0]
        self.tlC= [255,255,255]
        self.curCol=[0,255,0]
        self.state_selector = -1
        self.control=2

        #self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM )
        #self.sock.bind(('localhost',33445))
        #self.sock.settimeout(.01)
        
        #phraseLoc='C:\Users\Dante\Documents\Python\Remote\IRCodes\\'
        phraseLoc='resource/'

        self.size=[screenWid,screenHgt]#dimensions of outerbox
        
        self.parScr = {'w':360, 'h':560, 'sx':120, 'sy':80,
                       'tw':80, 'th':120}#dimensions of images
        
        self.buffX = 400
        self.buffY = 230

        self.arrow=pygame.image.load(phraseLoc + 'Arrow.png')
        self.arrowS=pygame.image.load(phraseLoc + 'ArrowSel.png')
        
        self.arrowU=self.arrow
        self.arrowD=pygame.transform.rotate(self.arrow,180)
        self.arrowL=pygame.transform.rotate(self.arrow,90)
        self.arrowR=pygame.transform.rotate(self.arrow,270)

        #coordiantes of'FAV' for starting location
        self.cursorS=[self.parScr['sx']+self.buffX,self.parScr['sy']+self.buffY,self.parScr['sx'],self.parScr['sy']]

        self.cursor=pygame.Rect(self.cursorS) # generalt coordinates for cursor

        EIGHTBITS=serial.EIGHTBITS
        arduino=4 #check arduino program for port
        try:
            self.port=serial.Serial(port=arduino,baudrate=9600,bytesize=EIGHTBITS)
        except:
            print 'Insert Arduino into USB Port and restart program'
            self.port=None
        self.port.write('l')
        #reading in text file
        self.irCodes = {'comm':[],'coord':[],'code':[]}
        self.FileLoc = phraseLoc + 'IRCodes.txt'
        self.font=pygame.font.Font(None,25)
        self.recList=[0]*21

        with open(self.FileLoc,'r') as fd:
            for line in fd:
                el=line.strip().split('\t')
                self.irCodes['comm'].append(el[0])
                self.irCodes['coord'].append(tuple((int(el[1]),int(el[2]))))
                self.irCodes['code'].append(el[3]) #phraseLoc + el[3])
                self.irCodes['comm'][0] = 'PREV MENU'
                          
        self.commdraw = list(self.irCodes['comm'])
        self.commdims = list(self.irCodes['comm'])

        for i in range(0,len(self.irCodes['comm'])):
            comm = self.irCodes['comm'][i]
            coord = self.irCodes['coord'][i]
            xcoord = self.parScr['sx']*(coord[0]) + self.buffX
            ycoord = self.parScr['sy']*(coord[1]) + self.buffY
            commvec = (xcoord + .13*self.parScr['sx'], ycoord + .35*self.parScr['sy'],.5*self.parScr['sx'],.5*self.parScr['sy'])
            self.commdims[i] = commvec
            self.commdraw[i] = self.font.render(comm,True,self.tlC)
        
        #create custom rectangles to know where things intersect
        count=0   
        for i in range(0,(self.parScr['w']/self.parScr['sx'])):
            for j in range(0,(self.parScr['h']/self.parScr['sy'])):
                self.recList[count]=pygame.Rect(i*self.parScr['sx']+self.buffX,j*self.parScr['sy']+self.buffY,self.parScr['sx'],self.parScr['sy'])
                count=count+1

        self.laserOn = True
        
    def drawLines(self):
        for i in range(self.parScr['sx'],self.parScr['w'],self.parScr['sx']):
            pygame.draw.line(self.screen,self.tlC,[i+self.buffX,self.buffY],[i+self.buffX,self.parScr['h']+self.buffY],1)
        for i in range(self.parScr['sy'],self.parScr['h'],self.parScr['sy']):
            pygame.draw.line(self.screen,self.tlC,[self.buffX,i+self.buffY],[self.parScr['w']+self.buffX,i+self.buffY],1)

        pygame.draw.rect(self.screen,self.tlC,[self.buffX,self.buffY,self.parScr['w'],self.parScr['h']],2)

    def drawArrows(self):
        self.uptri=pygame.Surface.blit(self.screen, self.arrowU, [self.size[0]/2+2*self.parScr['th']+self.parScr['tw']/4, self.size[1]/2-self.parScr['th']*3/2])
        self.dotri=pygame.Surface.blit(self.screen, self.arrowD, [self.size[0]/2+2*self.parScr['th']+self.parScr['tw']/4, self.size[1]/2+self.parScr['th']/2])
        self.letri=pygame.Surface.blit(self.screen, self.arrowL, [self.size[0]/2+self.parScr['th'], self.size[1]/2-self.parScr['tw']/2])
        self.ritri=pygame.Surface.blit(self.screen, self.arrowR, [self.size[0]/2+3*self.parScr['th'], self.size[1]/2-self.parScr['tw']/2])    

    def drawCursor(self):
        pygame.draw.rect(self.screen,self.curCol,self.cursor,2)

    def drawText(self):
        for i in range(0,len(self.commdraw)):
            self.screen.blit(self.commdraw[i], self.commdims[i])

    def draw(self):
        self.drawLines()
        self.drawArrows()
        self.drawCursor()
        self.drawText()  

    def move(self,trialDecision):       
        if trialDecision==1 and self.cursor[1]>self.buffY+4: #Move Up
            self.cursor[1]=self.cursor[1]-self.parScr['sy']
        if trialDecision==2 and self.cursor[1]<self.parScr['h']-self.parScr['sy']+self.buffY-2: #Move Down
            self.cursor[1]=self.cursor[1]+self.parScr['sy']
        if trialDecision==3 and self.cursor[0]>self.buffX+4: # Move Left
            self.cursor[0]=self.cursor[0]-self.parScr['sx']
        if trialDecision==4:
            if self.cursor[0]<self.parScr['w']-self.parScr['sx']+self.buffX-2: #Move Right
                self.cursor[0]=self.cursor[0]+self.parScr['sx']
            elif self.cursor[0]>=self.parScr['w']-self.parScr['sx']+self.buffX-2:
		self.control=3
                self.arrowL=pygame.transform.rotate((self.arrowS),90)
                self.servo=3
                self.lastMove=3
                self.curCol=[255,255,255]
                
    def sendCode(self):
        ind=self.cursor.collidelist(self.recList)
        print "code idx:" + str(ind)
        code = self.irCodes['code'][ind]        
        if ind !=0: 
            if self.port:self.port.write(code)            
            if ind == 6 or ind == 20 : #enter keys
                self.cursor=pygame.Rect(self.cursorS)
        elif ind == 0 : #Prev Menu
            self.port.write('l')
            self.laserOn = True
            self.close()
            

    def Lazer(self,classData):
        if classData == 1:#Up
            self.arrowU=self.arrowS###
            self.arrowD=pygame.transform.rotate(self.arrow,180)
            self.arrowL=pygame.transform.rotate(self.arrow,90)
            self.arrowR=pygame.transform.rotate(self.arrow,270)
            self.servo=1
        elif classData == 2: #Down
            self.arrowU=self.arrow
            self.arrowD=pygame.transform.rotate(self.arrowS,180)###
            self.arrowL=pygame.transform.rotate(self.arrow,90)
            self.arrowR=pygame.transform.rotate(self.arrow,270)
            self.servo=2
        elif classData == 3: #Left
            self.arrowU=self.arrow
            self.arrowD=pygame.transform.rotate(self.arrow,180)
            self.arrowL=pygame.transform.rotate(self.arrowS,90)###
            self.arrowR=pygame.transform.rotate(self.arrow,270)
            self.servo=3
            if self.lastMove==3 :
                self.control=2
                self.arrowL=pygame.transform.rotate((self.arrow),90)
                self.curCol=[0,255,0]
        elif classData == 4: #Right
            self.arrowU=self.arrow
            self.arrowD=pygame.transform.rotate(self.arrow,180)
            self.arrowL=pygame.transform.rotate(self.arrow,90)
            self.arrowR=pygame.transform.rotate(self.arrowS,270)###
            self.servo=4
            
        self.lastMove=classData
        
    def moveLazer(self):
        if self.servo==1 :
            self.port.write('U')
        elif self.servo==2 :
            self.port.write('D')
        elif self.servo==3 :
            self.port.write('L')
        elif self.servo==4 :
            self.port.write('R')
        
        
    def update(self, decision, selection):
        if self.laserOn == True:
            self.port.write('l')
            self.laserOn = False       
        if self.control==2 :
            self.move(decision)
            if selection==1:
                self.sendCode()
        elif self.control==3 :
            if decision: self.Lazer(decision)
            if selection==1 and self.port:
                self.moveLazer()
                        
    def switch(self):
        if self.state_selector != -1:
            new_state = self.state_selector
            #self.state_selector = -1
            return new_state
        else:
            return -1            
    
        
if __name__ == "__main__":
    screen = pygame.display.set_mode((screenWid,screenHgt))
    
    screen.fill(rgb['black'])
    remote=BCIRemote(screen)

    while exitLoop == False:

        screen.fill(rgb['black'])
        remote.draw()
        remote.switch()
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE: exitLoop=True
                if event.key==pygame.K_UP: remote.update(1,0)
                if event.key==pygame.K_DOWN: remote.update(2,0)
                if event.key==pygame.K_LEFT: remote.update(3,0)
                if event.key==pygame.K_RIGHT: remote.update(4,0)
                if event.key==pygame.K_RETURN: remote.update(0,1)

    pygame.quit()
                    
    
    
