# -*- coding: utf-8 -*-
"""
Created on Sun Sep  6 19:12:37 2015

@author: Kevin
"""

import re
from math import sin, cos, tan, log, asin, acos, atan, sinh, cosh, tanh,\
asinh, acosh, atanh, floor, ceil, factorial
import cmath
function_pattern =\
r'((?:a*(?:(sin|cos|tan|csc|cot|sec)h*|bs))' + \
r'|(?:l(?:og|n))|inf|sum|fact|cbrt|sqrt|dot|cross|norm|floor|ceil|point)'
number_pattern = r'(\-?\+?[\d]+\.?[\d]*(e[\d\-]+(\.?[\d])?)?)'
symbol_pattern = r'[a-zA-Zα-ωΑ-ΩЀ-ӿ]'

def get_sub_function(phrase, mode = 'function', opener = '(', closer = ')'):
    try:
        start = phrase.index(opener)
    except ValueError:
        return -1
    index = start + 1
    parens = 1
    while parens > 0:
        if phrase[index] == opener:
            parens += 1
        elif phrase[index] == closer:
            parens -= 1
        index += 1
    mode = mode.lower()
    if mode == 'function' or mode == 'fn':
        return phrase[start + 1:index - 1]
    if mode == 'indices':
        return [start, index - 1]
    if mode == 'all':
        return [phrase[start + 1:index - 1], start, index - 1]
    #returns the length of the sub-function
    if mode == 'length' or mode == 'width':
        return index - start

def has_sub_function(phrase, trigger = '('):
    return re.search('\\' + trigger, phrase)

def get_terms(phrase):
    index = 0
    stride = 0
    terms = []
    phrase_length = len(phrase)
    while index + stride < phrase_length:
        if re.match('[+-]', phrase[index+stride]):
            terms.append(phrase[index:index+stride])
            index = index + stride
            stride = 1
        elif re.match('[(<]', phrase[index+stride]):
            skip = get_sub_function(phrase[index+stride:], 'length')
            terms.append(phrase[index:index+stride+skip])
            index = index + stride + skip
            stride = 1
        else:
            stride += 1
    terms.append(phrase[index:index+stride])
    if terms[0] == '':
        del terms[0]
    elif terms[0][0] != '+':
        terms[0] = '+' + terms[0]
    if terms[len(terms)-1] == '':
        del terms[len(terms)-1]
    return terms

def replace_values(phrase, values):
    for i in values:
        phrase = phrase.replace(i, str(values[i]))
    return phrase

def replace_vectors(phrase):
    while has_sub_function(phrase, '<'):
        temp = get_sub_function(phrase, 'all', '<', '>')
        phrase = phrase[:temp[1]]\
        + 'Vector(' + temp[0]\
        + ')' + phrase[temp[2]+1:]
    return phrase

def replace_variables(phrase, values):
    """Replaces all instances of a named variable in a phrase with a 
    replacement, 'x' by default."""
    for var in values:
        i = 0
        while i < len(phrase):
            match = re.match(function_pattern, phrase[i:])
            if match:
                i += len(match.groups(0)[0])
            if re.match(var, phrase[i:]):
                phrase = phrase[:i]+str(values[var])+phrase[i+len(var):]
                i += 2 + len(str(values[var]))
            else:
                i += 1
    return phrase

def make_friendly(phrase, constants = [], cpx = True):
    """handles implicit multiplication, converts double signs into single ones,
    ensures that complex numbers work, deals with exponential terms like 2e8"""
    phrase = re.sub('\s', '', phrase)
    phrase = phrase.replace('--', '+')
    phrase = phrase.replace('+-', '-')
    phrase = phrase.replace('++', '+')
    phrase = phrase.replace('^', '**')
    if len(phrase) > 0 and phrase[0] == '+':
        phrase = phrase[1:]
    #handles exponential terms; replaces them with a dollar sign to be 
    #back-converted later
    phrase = re.sub(\
    r'(\d|'+symbol_pattern+')e(-?)(?:0*)(\d+)', r'\1$\2\3', phrase)
    if cpx:
        phrase = re.sub('([\d\)])(?!j)((?:\(|\<)|'+symbol_pattern+')', r'\1*\2', phrase)
        #converts a single j into 1j to agree with python's complex numbers
        phrase = re.sub('(?<!\d)j', '1j', phrase)
    else:
        phrase = re.sub('([\d\)])(\(|'+symbol_pattern+')', r'\1*\2', phrase)
    #both of these handle implicit multiplication
    phrase = re.sub('((?:\)|\>)|'+symbol_pattern+')(\d)', r'\1*\2', phrase)
    phrase = re.sub(r'(\d)('+function_pattern+')', r'\1*\2', phrase)
    #handles each instance of implicit multiplication of variables and functions
    phrase = implicit_multiply_variables(phrase, constants)
    #makes the dollar sign from earlier proper
    phrase = phrase.replace('$', 'e')
    while has_sub_function(phrase, '<'):
        phrase = replace_vectors(phrase)
    return phrase

def implicit_multiply_variables(phrase, constants = []):
    """finds instances where variables are implicitly multiplied and
    explicitly multiplies them. Makes sure to ignore strings of characters
    that form one of the pre-defined functions"""
    i = 0
    temp = phrase
    while i < len(phrase):
        temp = phrase[i:]
        if re.match(function_pattern, temp):
            i += len(re.match(function_pattern, temp).groups(0)[0])
        elif re.match(symbol_pattern+'{2}', temp):
            phrase = phrase[:i] + temp[0] + '*' + temp[1:]
            i += 1
        elif re.match(symbol_pattern+'\(', temp)\
        and not re.match(r'(\d|'+symbol_pattern+')e(-?)(?:0*)(\d+)', temp):
            phrase = phrase[:i] + temp[0] + '*' + temp[1:]
            i += 1
        elif re.match(symbol_pattern+'\<', temp)\
        and not re.match(r'(\d|'+symbol_pattern+')e(-?)(?:0*)(\d+)', temp):
            phrase = phrase[:i] + temp[0] + '*' + temp[1:]
            i += 1
        """
        elif re.match(constant_pattern, temp):
            i += len(re.match(constant_pattern, temp).groups(0)[0])
        """
        i += 1
    return phrase       

def get_variables(eqn, cpx = True):
    """returns an ordered list of distinct variable names within a function.
    Skips j to avoid conflicts with imaginary numbers."""
    variables = []
    #finds all characters surrounded by numbers or other non words
    variables = re.findall(r'(?<=[\W\d\b])([a-df-zA-Zα-ωΑ-Ω])(?=[\W\d\b])', \
    eqn)
    #finds variables at the end of the string specifically; necessary
    #because of the way Python handles String boundaries
    match = re.search(r'[\W\d\b]('+symbol_pattern+')$', eqn)
    if match:
        variables.append(match.groups(0)[0])
    #finds variables at the beginning of the string
    match = re.search(r'^('+symbol_pattern+')[\W\d\b]', eqn)
    if match:
        variables.insert(0, match.groups(0)[0])
    #matches a variable if it's the only thing in the string
    match = re.search(r'^('+symbol_pattern+')$', eqn)
    if match:
        variables.append(match.groups(0)[0])
    #creates a list and appends non-duplicate variables
    result = []
    for i in range(len(variables)):
        if cpx:
             if variables.index(variables[i]) == i and variables[i] != 'j':
                result.append(variables[i])
        else:
            if variables.index(variables[i]) == i:
                result.append(variables[i])
    return result

def is_number(phrase):
    return re.match('^' + number_pattern + '$', phrase)
    