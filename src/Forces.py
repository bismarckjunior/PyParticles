# -*- coding: utf-8 -*-
# Autor: Bismarck Gomes Souza Junior <bismarckgomes@gmail.com>
# Data: 03/10/2016

import numpy as np

N_DIMENSION = 3

class Force:

    def __init__(self, k=0.0, const=np.zeros(N_DIMENSION)):
        "Construtor."
        self.k_ = k
        self.const_ = const

    def __call__(self, dx):
        "Operador (). Retorna o vetor força."
        return self.k_*dx + self.const_


class Force_Constant(Force):

    def __init__(self, const=0.0):
        self.const_ = const

    def __call__(self, dx):
        "Operador (). Retorna o vetor força."
        return np.copy(self.const_)


class Force_Repulsive(Force):
    pass


class Force_Attractive(Force):
    pass


class Force_Shear(Force):
    pass