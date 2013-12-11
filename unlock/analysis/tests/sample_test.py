import unittest
import os
import filecmp
import subprocess
import unlock.analysis.sample

class SampleTest(unittest.TestCase):

    def test_plot_lin_regress(self):
        outputFile = "lin_regress_plot_output.png";
        if (os.path.exists(outputFile)):
            os.remove(outputFile)
    
        runProc = subprocess.Popen("python sample.py tests/lin_regress_plot_input.csv -export tests/"+outputFile, cwd="../")
        runProc.wait()
        
        self.assertTrue(filecmp.cmp(outputFile, "lin_regress_plot_expected_output.png", shallow=False),
                        "Exported graph is incorrect")
        
        os.remove(outputFile)

if __name__ == '__main__':
    unittest.main()