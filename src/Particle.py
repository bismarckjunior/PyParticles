# -*- coding: utf-8 -*-
# Autor: Bismarck Gomes Souza Junior <bismarckgomes@gmail.com>
# Data: 03/10/2016

from Forces import *
import numpy as np

N_DIMENSION = 3


class Particle:

    def __init__(self, index, m=0.0, r=0.0, x=None, v=None, a=None):
        "Construtor."
        self.m_ = m
        self.x_ = np.zeros(N_DIMENSION)
        self.r_ = 0.0
        self.id_ = int(index)
        self.velocity_ = np.zeros(N_DIMENSION)
        self.neighbors_particles_ = []
        self.neighbors_boundaries_ = []
        self.acceleration_ = np.zeros(N_DIMENSION)
        self.contacts_particles_ = []
        self.contacts_boundaries_ = []
        self.ext_force_ = Force_Constant(0.0)

        self.set_data(m, r, x, v, a)

    def set_data(self, m=0.0, r=0.0, x=None, v=None, a=None):
        "Atribui os valores das variáveis."
        if m:
            self.m_ = m

        if r:
            self.r_ = r

        if x is not None:
            self.x_ = x

        if v is not None:
            self.velocity_ = v

        if a is not None:
            self.acceleration_ = a

    def index(self):
        "Retorna o índice."
        return self.id_

    def r(self):
        "Retorna o raio."
        return self.r_

    def x(self):
        "Retorna a posição da partícula."
        return self.x_

    def velocity(self):
        "Retorna a velocidade da partícula."
        return self.velocity_

    def acceleration(self):
        "Retorna a aceleração da partícula."
        return self.acceleration_

    def mass(self):
        "Retorna a massa da partícula."
        return self.m_

    def add_contact_particles(self, index, contact):
        "Adiciona um contato à partícula."
        self.contacts_particles_.append(contact)
        self.neighbors_particles_.append(index)

    def remove_contact_particles(self, index, contact):
        "Remove o contato [contact]."
        if contact in self.contacts_particles_:
            self.contacts_particles_.remove(contact)
            self.neighbors_particles_.remove(index)
            return True
        else:
            return False

    def add_contact_boundary(self, index, contact):
        "Adiciona um contato à partícula."
        self.contacts_boundaries_.append(contact)
        self.neighbors_boundaries_.append(index)

    def remove_contact_boundary(self, index, contact):
        "Remove o contato [contact]."
        if contact in self.contacts_boundaries_:
            self.contacts_boundaries_.remove(contact)
            self.neighbors_boundaries_.remove(index)
            return True
        else:
            return False

    def get_neighbor_particles(self):
        "Retorna uma lista com as partículas vizinhas (em contato)."
        return self.neighbors_particles_[:]

    def get_neighbor_boundaries(self):
        "Retorna uma lista com as partículas vizinhas (em contato)."
        return self.neighbors_boundaries_[:]

    def set_external_force(self, force):
        "Atribui uma força externa"
        self.ext_force_ = force

    def update_acceleration(self):
        "Atualiza o valor da aceleração da partícula."
        # Forças externas
        force = self.ext_force_(self.x_)

        # Forças de contato
        for c in self.contacts_particles_ + self.contacts_boundaries_:
            force += c.get_force(self.id_)

        self.acceleration_ = force/self.m_

    def increment_acceleration(self):
        "Incrementa o valor da aceleração da partícula devido as forças do sistema."
        # Forças externas
        force = self.ext_force_(self.x_)

        # Forças de contato
        for c in self.contacts_particles_ + self.contacts_boundaries_:
            force += c.get_force(self.id_)

        self.acceleration_ += force/self.m_


class Particle_ByPass(Particle):
    "Partícula não influenciada por outras partículas."

    def set_data(self, m=0.0, r=0.0, x=None, v=None, a=None):
        "Atribui os valores das variáveis."
        if m and not self.m_:
            self.m_ = m

        if r and not self.r_:
            self.r_ = r

        if x is not None:
            self.x_ = x

        if v is not None and (self.velocity_ == np.zeros(N_DIMENSION)).all():
            self.velocity_ = v

        if a is not None and (self.acceleration_ == np.zeros(N_DIMENSION)).all():
            self.acceleration_ = a

    def update_acceleration(self):
        "Atualiza o valor da aceleração da partícula."
        return

    def increment_acceleration(self):
        "Incrementa o valor da aceleração da partícula devido as forças do sistema."
        return