
from .. import *
import unittest
import threading
import time


class CommandTests(unittest.TestCase):
    """Test suite for the command module"""
    def testCommand(self):
        c = Command(-1, -2, -3, [-1])
        self.assertEquals(-1, c.delta)
        self.assertEquals(-2, c.decision)
        self.assertEquals(-3, c.selection)
        self.assertEquals([-1], c.data)
        binary_c = Command.serialize(c)
        c1 = Command.deserialize(binary_c)
        self.assertEquals(c.delta, c1.delta)
        self.assertEquals(c.decision, c1.decision)
        self.assertEquals(c.selection, c1.selection)        
        self.assertEquals(c.data, c1.data)
        
    def testCommandSenderReceiverInterface(self):
        cr = CommandReceiverInterface()
        ex = False
        try:
            cr.next_command()
        except:
            ex = True
        self.assertTrue(ex)
        ex = False
        try:
            cr.stop()
        except:
            ex = True
        self.assertTrue(ex)
        
        cs = CommandSenderInterface()
        ex = False
        try:
            cr.send('')
        except:
            ex = True
        self.assertTrue(ex)
        ex = False
        try:
            cs.stop()
        except:
            ex = True
        self.assertTrue(ex)
            
    def testDatagramCommandSenderReceiver(self):
        receiver = DatagramCommandReceiver.create(socket_timeout=2)
        sender = DatagramCommandSender.create()
        c = Command(-1, -2, -3, [-1])
        def async_sendto():
            print 'c deltal = ', c.delta
            sender.send(c)
        
        t = threading.Thread(target = async_sendto, args = ())
        t.start()
        time.sleep(1)
        
        c1 = receiver.next_command()
        self.assertEquals(c.delta, c1.delta)
        self.assertEquals(c.decision, c1.decision)
        self.assertEquals(c.selection, c1.selection)        
        self.assertEquals(c.data, c1.data)
            
    def testInlineCommandReceiver(self):
        icr = InlineCommandReceiver()
        command = icr.next_command()
        self.assertEquals(None, command)
        c = Command(-1, -2, -3, [-1])
        c1 = Command(0, 1, 2, [0])
        c2 = Command(1, 2, 3, [1])
        c3 = Command(2, 3, 4, [5])
        icr.put(c)
        icr.put(c1)
        icr.put(c2)
        icr.put(c3)
        c = icr.next_command()
        
        self.assertEquals(c,c)
        c = icr.next_command()
        self.assertEquals(c1,c)
        c = icr.next_command()
        self.assertEquals(c2,c)
        c = icr.next_command()
        self.assertEquals(c3,c)
        c = icr.next_command()
        self.assertEquals(None,c)     
            
            
def getSuite():
    return unittest.makeSuite(CommandTests,'test')

if __name__ == "__main__":
    unittest.main()
