from .. import *
import unittest

class CommandTests(unittest.TestCase):
    """Test suite for the command module"""
    def testBaseCommand(self):
        bc = BaseCommand(-1, -2, -3, [-1])
        self.assertEquals(-1, bc.delta)
        self.assertEquals(-2, bc.decision)
        self.assertEquals(-3, bc.selection)
        self.assertEquals([-1], bc.data)
            
            
    def testCommandReceiverInterface(self):
        pass
            
    def testDatagramCommandReceiver(self):
        pass
            
    def testInlineCommandReceiver(self):
        icr = InlineCommandReceiver()
        command = icr.next_command()
        self.assertEquals(None, command)
        bc = BaseCommand(-1, -2, -3, [-1])
        bc1 = BaseCommand(0, 1, 2, [0])
        bc2 = BaseCommand(1, 2, 3, [1])
        bc3 = BaseCommand(2, 3, 4, [5])
        icr.put(bc)
        icr.put(bc1)
        icr.put(bc2)
        icr.put(bc3)
        c = icr.next_command()
        
        self.assertEquals(bc,c)
        c = icr.next_command()
        self.assertEquals(bc1,c)
        c = icr.next_command()
        self.assertEquals(bc2,c)
        c = icr.next_command()
        self.assertEquals(bc3,c)
        c = icr.next_command()
        self.assertEquals(None,c)     
            
            
def getSuite():
    return unittest.makeSuite(CommandTests,'test')

if __name__ == "__main__":
    unittest.main()
