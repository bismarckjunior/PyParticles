# -*- coding: utf-8 -*-
# Autor: Bismarck Gomes Souza Junior <bismarckgomes@gmail.com>
# Data: 19/10/2016

import numpy as np
from Forces import *

N_DIMENSION = 3


class Damping():

    def __init__(self, mc, k, beta):
        "Construtor."
        self.const_ = -2.*beta*np.sqrt(mc*k)

    def __call__(self, v):
        "Operador (). Retorna o vetor força de amortecimento."
        return self.const_*v


class Damping_Shear(Damping):
    pass


class Damping_Repulsive(Damping):
    pass


class Damping_Attractive(Damping):
    pass
