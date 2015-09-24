# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 00:33:00 2015

@author: kberry
"""

import re
import eqn_helper
from vector_class import *
operator = re.compile(\
'(e\-|e|\*\*\-|\*\-|\/\-|\*+|\/|\+|(?<!(?:\*|\/))\-|\%|cross|dot)')

class RawEvaluator:
    def __init__(self, phrase):
        self.phrase = re.sub('(?<!\*\*)(?<!e)\-', '-1*', phrase)
        self.phrase = eqn_helper.make_friendly(self.phrase)
        self.operators = self.init_operators()
        self.secondary_terms = []
        self.terms = self.init_terms()
        
    def init_operators(self):
        """gets all of the operators outside of parentheses in a phrase"""
        operators = []
        i = 0
        if len(self.phrase) > 0 and self.phrase[0] == '-':
            i += 1
        while i < len(self.phrase):
            #tacks on phrases within parentheses to be dealt
            #with at the evaluation stage
            if self.phrase[i] == '(':
                parens = 1
                i += 1
                while parens > 0:
                    if self.phrase[i] == '(':
                        parens += 1
                    if self.phrase[i] == ')':
                        parens -= 1
                    i += 1
                i -= 1
            if self.phrase[i] == '<':
                parens = 1
                i += 1
                while parens > 0:
                    if self.phrase[i] == '<':
                        parens += 1
                    if self.phrase[i] == '>':
                        parens -= 1
                    i += 1
                i -= 1
            else:
                match = operator.match(self.phrase[i:])
                if match:
                    operators.append(match.groups(0)[0])
                    i += len(match.groups(0)[0]) - 1
            i += 1
        return operators
    
    def evaluate(self):
        """recursively iterates through all parentheses, evaluating the \
        innermost parenthetical phrase first and working its way back \
        to the outermost"""
        try:
            return float(self.phrase)
        except ValueError:
            while self.has_parenthesis():
                index = self.get_nested_index()
                if str(self.terms[index][0]) == "-":
                    #there may be some issues with the type casting here
                    try:
                        self.terms[index] = -1 * \
                        (float(RawEvaluator(eqn_helper.unshell(\
                        self.terms[index])).evaluate()))
                    except ValueError:
                        self.terms[index] = -1 * \
                        (complex(RawEvaluator(eqn_helper.unshell(\
                        self.terms[index])).evaluate()))
                else:
                    self.terms[index] = \
                    RawEvaluator(eqn_helper.unshell(self.terms[index])).evaluate()
            index = 0
            terms = self.terms.copy()
            operators = self.operators.copy()
            #iterates through the term and operator equations,
            #trimming them as it goes
            while len(terms) > 1 and len(operators) > 0:
                index = self.get_op_index(operators)
                terms[index] = self.operate(operators[index], terms[index],\
                terms[index+1])
                if index < len(terms):
                    del(terms[index+1])
                del(operators[index])
            #returns the last remaining dreg of the term equation
            return terms[0]
    
    def init_terms(self):
        """gets all of the terms in an evaluator"""
        #makes sure that the first term is added as a negative if it's negative
        #this is more difficult to handle than makes reasonable sense
        if self.phrase[0] == '-':
            temp = '-'
            i = 1
        else:
            temp = ''
            i = 0
        terms = []
        parens = 0
        while i < len(self.phrase):
            if re.match(eqn_helper.symbol_pattern, self.phrase[i]):
                #adds on complex unit if complex, keeps searching otherwise
                if self.phrase[i] == 'j':
                    temp = temp + 'j'
                if self.phrase[i] == 'e':
                    terms.append(temp)
                    self.secondary_terms.append(temp)
                    temp = ''
                else:
                    self.secondary_terms.append(self.phrase[i])
            elif self.phrase[i] == '(':
                temp, parens = temp + '(', 1
                i += 1
                while parens > 0:
                    if self.phrase[i] == '(':
                        parens += 1
                    if self.phrase[i] == ')':
                        parens -= 1
                    temp = temp + self.phrase[i]
                    i += 1
                i -= 1
                terms.append(temp)
                self.secondary_terms.append(temp)
                temp = ''
            elif self.phrase[i] == '<':
                parens = 1
                i += 1
                while parens > 0:
                    if self.phrase[i] == '<':
                        parens += 1
                    if self.phrase[i] == '>':
                        parens -= 1
                    temp = temp + self.phrase[i]
                    i += 1
                temp = temp[:len(temp)-1]
                i -= 1
                terms.append(Vector(eval(temp)))
                self.secondary_terms.append(Vector(eval(temp)))
                temp = ''
            #keeps adding non-operators to temp
            elif not operator.match(self.phrase[i]):
                temp = temp + self.phrase[i]
            #adds temp to terms upon finding an operator, then repeats
            else:
                if len(temp) > 0:
                    terms.append(temp)
                    self.secondary_terms.append(temp)
                temp = ''
            i += 1
        if len(temp) > 0:
            terms.append(temp)
            self.secondary_terms.append(temp)
        return terms
    
    def operate(self, operator, t1, t2):
        """returns the result of an operation performed on two terms"""
        #casts strings to the appropriate type
        if type(t1) == type(''):
            try:
                t1 = float(t1)
            except ValueError:
                try:
                    t1 = complex(eval(t1))
                #I wrote my own method for complex casting because Python's
                #native type cast relies on very specific pre-formatting
                except ValueError:
                    t1 = eqn_helper.make_complex(t1)
        if type(t2) == type(''):
            try:
                t2 = float(t2)
            except ValueError:
                try:
                    t2 = complex(eval(t2))
                except ValueError:
                    t2 = eqn_helper.make_complex(t2)
        try:
        #makes sure that if one term is a vector, both terms become vectors
            if type(t2) == type(Vector()) and type(t1) != type(Vector()):
                t1 = Vector(t1)
            if operator == '+':
                return t1 + t2
            if operator == '-':
                return t1 - t2
            if operator == '*':
                return t1 * t2
            if operator == '/':
                return t1 / t2
            if operator == '**':
                return t1 ** t2
            if operator == '*-':
                return t1 * -t2
            if operator == '/-':
                return t1 / -t2
            if operator == '**-':
                return 1 / t1 ** t2
            if operator == 'e':
                return t1 * 10 ** t2
            if operator == 'e-':
                return t1 * 10 ** -t2
            if operator == 'dot':
                return t1.dot(t2)
            if operator == 'cross':
                return t1.cross(t2)
            if operator == '%':
                return t1 % t2
        except OverflowError:
            print('OverflowError. Value too large.')
            return 0
        #no default return because not returning signifies an error elsewhere
            
    def get_op_index(self, operators):
        """gets the index of the next operator to be evaluated."""
        for i in range(len(operators)):
            if operators[i] == "**" or operators[i] == "**-"\
            or operators[i] == "e" or operators[i] == "e-":
                return i
        for i in range(len(operators)):
            if operators[i] == "*" or operators[i] == "/"\
            or operators[i] == "%" or operators[i] == "/-"\
            or operators[i] == "*-" or operators[i] == 'dot'\
            or operators[i] == "cross":
                return i
        for i in range(len(self.operators)):
            if operators[i] == "+" or operators[i] == "-":
                return i
    
    def has_parenthesis(self):
        """Returns true if there is a parenthesis in the evaluator's terms"""
        for i in self.terms:
            i = str(i)
            if re.match('\(', str(i)):
                if i.count('(') == 1 and i.count('j') > 0 \
                and i.count(')') == 1:
                    pass
                else:
                    return True
        return False
    
    def get_nested_index(self):
        """Gets the index of the first parenthetical item to be evaluated"""
        for i in range(len(self.terms)):
            if re.match('\(', str(self.terms[i])):
                if str(self.terms[i]).count('(') == 1 and \
                str(self.terms[i]).count('j') > 0 \
                and str(self.terms[i]).count(')') == 1:
                    pass
                else:
                    return i
        return -1
                
    def fp(self):
        """full print"""
        print('Phrase:', self.phrase)
        print('Operators:', self.operators)
        print('Terms:', self.terms)
    
    def __repr__(self):
        return self.phrase
    
    def __str__(self):
        return self.phrase
    
    @staticmethod
    def eval_tapes(terms, ops, order):
        i = 0
        output = 0
        while i < len(ops):
            print(terms)
            print('Output:', output)
            print(terms[order[i]])
            print(ops[order[i]])
            print(terms[order[i]+1])
            temp = RawEvaluator.operate(RawEvaluator, ops[order[i]], \
            terms[order[i]], terms[order[i]+1])
            terms[order[i]] = temp
            terms[order[i]+1] = 0
            output += temp
            temp = 0
            i += 1
        return output

def evaluate_numbers(phrase):
    """creates an evaluator for a phrase and automatically evaluates it."""
    temp = RawEvaluator(phrase).evaluate()
    if type(temp) != type(''):
        return temp
    else:
        try:
            #FIX THIS
            return eval(temp)
        except (ValueError, TypeError):
            try:
                return complex(temp)
            except (TypeError, ValueError):
                try:
                    return eqn_helper.make_complex(temp)
                except (TypeError, ValueError):
                    return Vector(temp)

def eval_test():
    evaluators = []
    evaluators.append(Evaluator('-11 + 2*-3 -4 -((4/5 + 5)/6 + 1/9*6)'))
    evaluators.append(Evaluator('<2, 3(3*0)> + 2 - (2<2, 2>2)'))
    evaluators.append(Evaluator('2<2, 2>'))
    evaluators.append(Evaluator('<2, 3(3*0)> + (2<2, 2>2)'))
    evaluators.append(Evaluator('2j+2'))
    evaluators.append(Evaluator('<2, 3, 4> / 1j / 21**-2'))
    evaluators.append(Evaluator('2(2+1j)^3+1/((2+1j)^2)'))
    return evaluators