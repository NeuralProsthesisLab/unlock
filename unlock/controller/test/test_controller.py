
import unittest

# XXX - if there were any tests, this is where they would go
class UnlockControllerTests(unittest.TestCase):       
    def testUnlockController(self):
        pass
        
def getSuite():
    return unittest.makeSuite(UnlockControllerTests,'test')

if __name__ == "__main__":
    unittest.main()
    