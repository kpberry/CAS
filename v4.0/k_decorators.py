# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 16:33:08 2015

@author: Kevin
"""

from datetime import datetime

number_pattern = r'(\-?[\d]+\.?[\d]*(e[\d\-]+(\.?[\d])?)?)'

def timed(function):
    """prints a function's execution time upon execution"""
    def result(*args):
        t = datetime.now()
        ret = function(*args)
        print(function.__name__, 'took', (datetime.now() - t), 'seconds.')
        return ret
    return result