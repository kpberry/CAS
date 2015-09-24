# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 22:57:58 2015

@author: kberry
"""
from function_class import Function
from equation_class import Equation
from parametric_equation_class import ParamEqn
from tkinter import *
from vector_class import Vector
from grapher import graph, graph_par
import re

class Runner:
    
    def __init__(self, master):
        self.master = master
        self.master.minsize(500, 200)
        
        self.entry_line = Entry(master)
        self.entry_line.grid(row = 0, column = 0, columnspan = 4)
        
        self.clearer = Button(master, text = 'Clear', command = self.clear)
        self.clearer.grid(row = 1, column = 0)
        self.enterer = Button(master, text = 'Enter',\
        command = self.manage_input)
        self.enterer.grid(row = 1, column = 1)
        self.grapher = Button(master, text = 'Graph',\
        command = self.graph)
        self.grapher.grid(row = 2, column = 0)
        
        self.funct_display = Label(master, text = 'Enter a function.')
        self.funct_display.grid(row = 1, column = 2)
        self.result_display = Label(master, text = '')
        self.result_display.grid(row = 1, column = 3)        
        
        self.funct = None
    
    def manage_input(self):
        #If there is no entry and the user tries to enter, prompts entry again
        if self.entry_line != None:
            entry = self.entry_line.get()
            if entry == '':
                self.funct_display.config(text = 'Try again.')
        #If there is no function and the user enters a valid input, identifies
        #the type of input, then stores the function and its variables
        if self.funct == None:
            #counts the number of equals signs; 0 = fn, 1 = eqn, 2+ = param
            num = entry.count('=')
            if num == 0:
                self.set_function(entry)
                self.add_variable_entries(\
                list(self.funct.get_variables().keys()))
            if num == 1:
                self.set_equation(entry)
                self.add_variable_entries(\
                list(self.funct[1].get_variables().keys()))
            if num > 1:
                #try catch allows parametric equations to be separated by
                #semi-colons or commas
                try:
                    entries = re.findall('(. *= *.+?)(?:;|,|$)', entry)
                    self.set_parametric_equation(entries)
                    self.add_variable_entries(self.funct.get_variables())
                except IndexError:
                    entries = re.findall('(. *= *.+?)(?:;|$)', entry)
                    self.set_parametric_equation(entries)
                    self.add_variable_entries(self.funct.get_variables())
            #automatically evaluates the input if there are no variables
            if self.var_names == []:
                if type(self.funct) == type(Function('')):
                    self.eval_function({})
                if type(self.funct) == type(ParamEqn()):
                    self.eval_parametric_function({})
            #if there are variables, prompts variable inputs
            else:
                self.result_display.config(\
                text = 'Enter values for evaluation.')
            #if the entry line is not gone, removes it. Ensures that the 
            #input provides a tactile sensation
            if self.entry_line != None:
                self.entry_line.destroy()
                self.entry_line = None
        #if there is a function, identifies it then evaluates it based on
        #the entered variables
        elif type(self.funct) == type(Function('')):
            self.eval_function(self.get_variable_entries())
        elif type(self.funct) == type(ParamEqn()):
            self.eval_parametric_function(self.get_variable_entries())
            
    def set_function(self, entry):
        self.funct = Function(entry)
        self.funct_display.config(text = str(self.funct))
        self.entry_line.delete(0, END)
    
    def set_equation(self, entry):
        self.funct = Equation(entry)[1]
        self.funct_display.config(text = entry)
        self.entry_line.delete(0, END)
    
    def set_parametric_equation(self, entries):
        self.funct = ParamEqn(entries)
        self.funct_display.config(text = str(self.funct))
        self.entry_line.delete(0, END)
    
    def eval_function(self, entry):
        val = self.funct.evaluate(entry)
        if entry == {}:
            self.result_display.config(text = '= ' + str(val))
        else:
            self.result_display.config(text = 'evaluated where ' + \
            str(entry) + ' = ' + str(val))
    
    def eval_parametric_function(self, entry):
        val = self.funct.evaluate(entry, printing = True)
        if entry == {}:
            self.result_display.config(text = '= ' + str(val))
        else:
            self.result_display.config(text = 'evaluated where ' + \
            str(entry) + ' = ' + str(val))
        
    def add_variable_entries(self, variables = []):
        """adds the list of variables and their accompanying entry lines"""
        count = 0
        self.entries = []
        self.labels = []
        while count < len(variables):
            self.labels.append(Label(self.master, text = variables[count]))
            self.labels[count].grid(row = 2 + count // 2,\
            column = 1 + 2 * (count % 2))
            self.entries.append(Entry(self.master))
            self.entries[count].grid(row = 2 + count // 2,\
            column = 2 + 2 * (count % 2))
            count += 1
        self.var_names = variables
            
    def get_variable_entries(self):
        var_values = []
        for i in self.entries:
            var_values.append(i.get())
        return dict(zip(self.var_names, var_values))
    
    def graph(self):
        if type(self.funct) == type(Function('')):
            graph(self.funct)
        elif type(self.funct) == type(Equation('')):
            graph(self.funct[1])
        else:
            graph_par(self.funct)
    
    def clear(self):
        self.funct = None
        self.result_display.config(text = '')
        self.funct_display.config(text = 'Enter a function.')
        self.entry_line = Entry(self.master)
        self.entry_line.grid(row = 0, column = 0, columnspan = 4)
        count = 0
        while count < len(self.labels):
            self.labels[count].destroy()
            self.entries[count].destroy()
            count += 1
    

root = Tk()
calc = Runner(root)
root.mainloop()
try:
    root.destroy()
except GraphicsError:
    root.destroy()
