# -*- coding: utf-8 -*-
# Autor: Bismarck Gomes Souza Junior <bismarckgomes@gmail.com>
# Data: 03/10/2016

import numpy as np
from Forces import *
from Damping import *

N_DIMENSION = 3


class Contact:

    def __init__(self, p0, props={}):
        "Construtor."
        self.p0_ = p0
        self.id_0_ = p0.index()
        self.id_1_ = -1
        self.props_ = props

        # Tempo de contato
        self.contact_time_ = 0.0

    def get_index(self, pos=0):
        "Retorna o índice dos objetos no contato dependendo da posição [pos]."
        return self.id_0_ if pos == 0 else self.id_1_

    def get_contact_time(self):
        "Retorna o tempo de contato."
        return self.contact_time_

    def init_forces(self, mc):
        "Inicia as forças de interação."
        # Forças do contato
        self.force_ = np.zeros(N_DIMENSION)
        self.attractive_force_ = Force_Attractive(self.props_['kn_a'])
        self.repulsive_force_ = Force_Repulsive(self.props_['kn_r'])
        self.shear_force_ = Force_Shear(self.props_['ks'])

        # Forças de amortecimento no contato
        self.damping_shear_ = Damping_Shear(mc, self.props_['ks'], self.props_['beta_s'])
        self.damping_repulsive_ = Damping_Repulsive(mc, self.props_['kn_r'], self.props_['beta_n'])
        self.damping_attractive_ = Damping_Attractive(mc, self.props_['kn_a'], self.props_['beta_n'])

    def update_force(self, dt):
        "Atualiza a força resultante."
        self.contact_time_ += dt
        n = self.normal_vector()
        db = self.distance_border()
        db_vector = n*db

        # Velocidade relativa
        vr = self.relative_velocity()

        # Velocidade relativa normal
        vn = np.dot(vr, n)*n

        # Velocidade relativa cisalhante
        vs = vr - np.dot(vr, n)*n

        # Vetor força resultante
        self.force_ =  np.zeros(N_DIMENSION)

        # Partículas próximas
        if 0 < db < self.props_['db_max']:
            # Anulando tempo de contato
            self.contact_time_ = 0.0

            # Força atrativa
            Fn = self.attractive_force_(db_vector)

            # Força de amortecimento normal
            Fdn = self.damping_attractive_(vn)

            # Força do contato
            self.force_ = Fn + Fdn

            # Forças nulas
            Fs = np.zeros(N_DIMENSION)
            Fds = np.zeros(N_DIMENSION)

        # Partículas sobrepostas
        elif db <= 0:
            # Força repulsiva
            Fn = self.repulsive_force_(db_vector)

            # Força cisalhante
            Fs = self.shear_force_(vs*self.contact_time_)
            norm_Fs = np.linalg.norm(Fs)

            # Força de atrito de Coulomb
            Fat = np.linalg.norm(self.props_['mu']*abs(Fn))

            # Restrição da Lei de atrito de Coulomb
            if (norm_Fs > Fat and norm_Fs != 0):
                Fs *= Fat/norm_Fs

            # Força de amortecimento normal
            Fdn = self.damping_repulsive_(vn)

            # Força de amortecimento cisalhante
            Fds = self.damping_shear_(vs)

            # Força do contato
            self.force_ = Fn + Fs + Fdn + Fds

        else:
            # Forças nulas
            Fn = Fs = Fdn = Fds = np.zeros(N_DIMENSION)

        # Salvando as forças
        self.Fn_ = Fn
        self.Fs_ = Fs
        self.Fdn_ = Fdn
        self.Fds_ = Fds

    def get_specific_force(self, force):
        "Retorna uma força específica."
        if (force == 'Fn'):
            return self.Fn_

        elif (force == 'Fs'):
            return self.Fs_

        elif (force == 'Fdn'):
            return self.Fdn_

        elif (force == 'Fds'):
            return self.Fds_

    def get_force(self, index):
        "Retorna a força resultante no contato"
        F = self.signal(index)*self.force_
        return F

    def has_particle(self, index):
        "Retorna true se a partícula com índice [index] faz parte do contato."
        return self.id_0_ == index

    def signal(self, index):
        "Retorna o sinal do vetor força relativo ao índice [index]."
        pass

    def distance_border(self):
        "Retorna a distância entre as bordas das partículas."
        pass

    def normal_vector(self):
        "Retorna o vetor normal ao contato."
        pass

    def relative_velocity(self):
        "Retorna o vetor velocidade relativa."
        pass


class Contact_Particles(Contact):
    mu_ = 0.0           # Fator de atrito para todos os contatos
    db_max_ = 0.0       # Distância máxima entre as partículas na qual ainda há
                        # força atrativa

    def __init__(self, p0, p1, props):
        "Construtor."
        Contact.__init__(self, p0, props)
        self.p1_ = p1
        self.id_1_ = p1.index()

        if (self.id_0_ > self.id_1_):
            self.p0_, self.p1_ = self.p1_, self.p0_
            self.id_0_, self.id_1_ = self.id_1_, self.id_0_

        # Massa equivalente
        m0, m1 = self.p0_.mass(), self.p1_.mass()
        mc = m0*m1/(m0 + m1)

        # Inicializa as classes das forças
        self.init_forces(mc)

    def signal(self, index):
        "Retorna o sinal do vetor força relativo ao índice [index]."
        if (self.id_0_ == index):
            return 1.0

        elif (self.id_1_ == index):
            return -1.0

        else:
            return 0.0

    def distance_border(self):
        "Retorna a distância entre as bordas das partículas."
        x0, x1 = self.p0_.x(), self.p1_.x()
        db = np.linalg.norm(x1 - x0) - self.p0_.r() - self.p1_.r()

        return db

    def normal_vector(self):
        "Retorna o vetor normal ao contato."
        x0, x1 = self.p0_.x(), self.p1_.x()
        n = (x1 - x0)/np.linalg.norm(x1 - x0)

        return n

    def relative_velocity(self):
        "Retorna o vetor velocidade relativa."
        vr = self.p1_.velocity() - self.p0_.velocity()

        return vr

    def has_particle(self, index):
        "Retorna true se a partícula com índice [index] faz parte do contato."
        return self.id_1_ == index or Contact.has_particle(self, index)


class Contact_Boundary(Contact):

    def __init__(self, p0, boundary):
        "Construtor."
        Contact.__init__(self, p0)
        self.id_1_ = boundary.get_index()
        self.boundary_ = boundary
        self.props_.update(boundary.get_properties())

        # Massa equivalente
        mc = self.p0_.mass()

        # Inicializa as classes das forças
        self.init_forces(mc)

    def signal(self, index):
        "Retorna o sinal do vetor força relativo ao índice [index]."
        return 1.0

    def distance_border(self):
        "Retorna a distância entre as bordas das partículas."
        return self.boundary_.distance(self.p0_) - self.p0_.r()

    def normal_vector(self):
        "Retorna o vetor normal ao contato."
        return self.boundary_.normal_vector(self.p0_)

    def relative_velocity(self):
        "Retorna o vetor velocidade relativa."
        return self.p0_.velocity()

    def has_boundary(self, index):
        "Retorna true se a fronteira com índice [index] faz parte do contato."
        return self.id_1_ == index
