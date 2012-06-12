import unittest
from mFunctions import *

class TestmFunctions(unittest.TestCase):
    def setUp(self):
        self.testString="Mary^Smith^123 Anywhere St.;nowhere;AK;12345"
    
    def test_mExtract(self):
        result = mFunctions.mExtract(self.testString,2)
        self.assertEqual(result,"a")
        result = None
        result = mFunctions.mExtract(self.testString,5)
        self.assertEqual(result,"^")

    def test_mPiece(self):
        result = mFunctions.mPiece(self.testString,"^",1)
        self.assertEqual(result,"Mary")
        result = None
        result = mFunctions.mPiece(self.testString,"^",3)
        self.assertEqual(result,"123 Anywhere St.;nowhere;AK;12345")
        result2 = mFunctions.mPiece(result,";")
        self.assertEqual(result2,"123 Anywhere St.")

if __name__ == '__main__':
    unittest.main()

