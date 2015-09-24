# -*- coding: utf-8 -*-
"""
Created on Sun Sep  6 12:36:21 2015

@author: Kevin
"""

class Fraction:
    
    def __init__(self, num = 0, denom = 1, denom_limit = 1e16):
        if type(num) == type(''):
            halves = num.split('/')
            self.__num = float(halves[0])
            if len(halves) == 2:
                self.__denom = float(halves[1])
            else:
                self.__denom = 1
        else:
            self.__num = num
            self.__denom = denom
        self.__val = self.__num / self.__denom
        try:
            self.reduce(denom_limit)
        except:
            pass
    
    @property
    def val(self):
        return self.__val
        
    @property
    def num(self):
        try:
            return int(self.__num)
        except:
            return self.__num
    
    @num.setter
    def num(self, num):
        self.__num = num
    
    @property
    def denom(self):
        try: 
            return int(self.__denom)
        except:
            return self.__denom
    
    @denom.setter
    def denom(self, denom):
        self.__denom = denom
        
    def reduce(self, denom_limit = 1e16):
        while int(self.__num) != self.__num and self.__denom < denom_limit:
            self.__num *= 10
            self.__denom *= 10
        while int(self.__denom) != self.__denom and self.__denom < denom_limit:
            self.__num *= 10
            self.__denom *= 10
        
        #euclid's algorithm to find the least common denominator
        a = self.__num
        b = self.__denom
        t = a
        while b != 0:
            t = b
            b = a % b
            a = t
        self.num /= a
        self.denom /= a
    
    def ld(self, denom_limit = 1e16):
        num_and_denom = self.n_min(lambda x, y: abs((x / y) - self.val),
                          [1, 1],[denom_limit, denom_limit], len(str(self.val)))
        self.num = int(num_and_denom[0])
        self.denom = int(num_and_denom[1])
    
    def n_min(self, f, lows = [0], ups = [100], precision = 10):
    
        #opposite of n_max
       
        #number of dimensions in the functions
        dims = len(ups)
        #this is the list of center coordinates; the tested points will be mutually
        #orthogonal and equidistant from the omnidimensional point described by 
        #this list
        #indices[0] represents x, indices[1] represents y, etc.
        indices = [(ups[i]+lows[i])/2 for i in range(dims)]
        #distance between testing points and the center
        steps = [(ups[i]-lows[i])/2 for i in range(dims)]
        #values less than their corresponding value in indices
        low_is = [0] * dims
        #values greater than their correspoinding value in indices
        up_is = [0] * dims
        #list of lists of 1s and 0s representing the different testing points
        #e.g., for a 3 dimensional case, if we are checking a point closer to
        #zero in the x direction but closer to the upper limit in the y direction,
        #that point's permutation entry would be ['0', '1']
        permutations = [list(bin(i)[3:]) for i in range(2**dims, 2**(dims+1))]
        #temporary list to store the low_is and up_is values corresponding to 1s
        #and 0s in permutations
        #a 1 is an index from up_is and a 0 is an index from low_is
        params = []
        #current list of values that have been tested; cleared and repopulated each
        #time the checking depth increases
        vals = []
        #self explanatory
        minimum = f(*indices)
        #makes sure that the previous minimum cannot be confused for the current
        prev_minimum = -minimum 
        temp_min = 0
        last_indices = indices
        count = 0
        #flag that indicates that the last iteration of the algorithm increased the
        #precision of the calculation of the max; if it did not increase, the 
        #algorithm continues until it does 
        increased_precision = False
        #continues checking and decreasing the check distance for a number of 
        #layers equal to that specified by precision
        #cuts the algorithm off if it ends up in an infinite loop 
        while ((round(prev_minimum, precision) != round(minimum, precision))\
            or not increased_precision) and count < 100:
            vals = []
            prev_minimum = minimum
            steps = [i/2 for i in steps]
            low_is = [indices[i] - steps[i] for i in range(dims)]
            up_is = [indices[i] + steps[i] for i in range(dims)]
            for i in permutations:
                for j in range(len(i)):
                    if i[j] == '0':
                        params.append(low_is[j])
                    else:
                        params.append(up_is[j])
                vals.append(f(*params))
                params = []
            if True in [i < minimum for i in vals]:
                temp_min = min(vals)
                index = vals.index(temp_min)
                for i in range(len(permutations[index])):
                    if permutations[index][i] == '0':
                        indices[i] = low_is[i]
                        up_is[i] = indices[i]
                    else:
                        indices[i] = up_is[i]
                        low_is[i] = indices[i]
                minimum = temp_min
                last_indices = indices
                increased_precision = True
            else:
                increased_precision = False
            count += 1
        return last_indices
    
    def __add__(self, other):
        if not isinstance(other, Fraction): other = Fraction(other)
        factor = Fraction(self.denom, other.denom)
        return Fraction(self.num * factor.denom + other.num * factor.num, 
                        self.denom * factor.denom)
    
    def __sub__(self, other):
        if not isinstance(other, Fraction): other = Fraction(other)
        factor = Fraction(self.denom, other.denom)
        return Fraction(self.num * factor.denom - other.num * factor.num,
                        self.denom * factor.denom)
    
    def __mul__(self, other):
        if not isinstance(other, Fraction): other = Fraction(other)
        return Fraction(self.num * other.num, self.denom * other.denom)
    
    def __truediv__(self, other):
        if not isinstance(other, Fraction): other = Fraction(other)
        return Fraction(self.num * other.denom, self.denom * other.num)
    
    def __iadd__(self, other):
        return self + other
    
    def __isub__(self, other):
        return self - other
    
    def __imul__(self, other):
        return self * other
    
    def __itrue_div(self, other):
        return self / other
    
    def __str__(self):
        if (self.denom == 1):
            return str(self.num)
        return str(self.num) + '/' + str(self.denom)
    
    def __repr__(self):
        return str(self)
        