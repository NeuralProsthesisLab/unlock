from .. import *
import unittest

class CommandTests(unittest.TestCase):
    """Test suite for the command module"""
    def testCommand(self):
        bc = Command(-1, -2, -3, [-1])
        self.assertEquals(-1, bc.delta)
        self.assertEquals(-2, bc.decision)
        self.assertEquals(-3, bc.selection)
        self.assertEquals([-1], bc.data)
        binary_bc = Command.serialize(bc)
        bc1 = Command.deserialize(binary_bc)
        self.assertEquals(bc.delta, bc1.delta)
        self.assertEquals(bc.decision, bc1.decision)
        self.assertEquals(bc.selection, bc1.selection)        
        self.assertEquals(bc.data, bc1.data)
        
    def testCommandReceiverInterface(self):
        pass
            
    def testDatagramCommandReceiver(self):
        pass
            
    def testInlineCommandReceiver(self):
        icr = InlineCommandReceiver()
        command = icr.next_command()
        self.assertEquals(None, command)
        bc = Command(-1, -2, -3, [-1])
        bc1 = Command(0, 1, 2, [0])
        bc2 = Command(1, 2, 3, [1])
        bc3 = Command(2, 3, 4, [5])
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
