# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 11:55:59 2015

@author: Kevin
"""

class Symbol:
    
    def __init__(self, name, value):
        self.name = name
        self.__value = value
    
    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, value):
        self.__value = value