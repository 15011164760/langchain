'''
Author: yangdongxu
Date: 2026-11-17 15:07:26
LastEditors: yangdongxu
LastEditTime: 2026-11-17 15:22:34
FilePath: \langchain\test_run_unit.py
'''
from unit_study import calculate
import unittest
class TestCalculate(unittest.TestCase):
    def test_calculate(self):
        self.assertEqual(calculate(3,5),8)
        self.assertEqual(calculate(4,6),10)
    def test_calculate_negative(self):
        self.assertEqual(calculate(-3,-5),-8)
        self.assertEqual(calculate(-4,6),2)
