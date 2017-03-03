# -*- coding: utf-8 -*-
# Autor: Bismarck Gomes Souza Junior <bismarckgomes@gmail.com>
# Data: 05/10/2016

import numpy as np
import IOControl as io
from Boundaries import Boundaries
from collections import OrderedDict
from Forces import *
from Contacts import *
from Particle import *

N_DIMENSION = 3


class Particles:
    "Classe que gerencia as partículas."

    def __init__(self):
        "Construtor."
        self.nParticles_ = 0
        self.particles_ = OrderedDict()

    def __len__(self):
        "Retorna o número de partículas."
        return self.nParticles_

    def __str__(self):
        "Função que permite que seja usada a função print na classe."
        h_vars = ('x', 'y', 'z', 'vx', 'vy', 'vz', 'ax', 'ay', 'az')

        text = "#id   "+ ("%-11s"*len(h_vars)) % h_vars + "\n"

        data_format = "{:11.3E}"*len(h_vars) + "\n"
        for p in self.particles_.values():
            text += "%03d " % p.index()
            x, v, a = p.x(), p.velocity(), p.acceleration()
            text += data_format.format(x[0], x[1], x[2], v[0], v[1], v[2], *a)

        return text

    def get_particle(self, index):
        "Retorna a partícula referente ao índice [index]."
        return self.particles_[index]

    def get_particles(self):
        "Retorna uma lista com todas as partícula."
        return self.particles_.values()

    def create_particle(self, index, m=0.0, r=0.0, x=None, v=None, a=None):
        "Cria uma partícula."
        if (index in self.particles_):
            print 'Erro: Duplicidade na criação da partícula', index
            raw_input()

        self.particles_[index] = Particle(index, m, r, x, v, a)
        self.nParticles_ += 1

    def get_positions(self):
        "Retorna um vetor com as posições de todas as partículas."
        X = np.empty((self.nParticles_, N_DIMENSION))
        for i, p in enumerate(self.particles_.values()):
            X[i,:] = p.x()

        return X

    def get_velocities(self):
        "Retorna um vetor com as velocidades de todas as partículas."
        V = np.empty((self.nParticles_, N_DIMENSION))
        for i, p in enumerate(self.particles_.values()):
            V[i,:] = p.velocity()

        return V

    def get_accelerations(self):
        "Retorna um vetor com as acelerações de todas as partículas"
        A = np.empty((self.nParticles_, N_DIMENSION))
        for i, p in enumerate(self.particles_.values()):
            A[i,:] = p.acceleration()

        return A

    def set_positions(self, X):
        "Atribui as posições de todas as partículas."
        for i, p in enumerate(self.particles_.values()):
            p.set_data(x=X[i,:])

    def set_velocities(self, V):
        "Atribui as velocidades de todas as partículas."
        for i, p in enumerate(self.particles_.values()):
            p.set_data(v=V[i,:])

    def set_accelerations(self, A):
        "Atribui as acelerações de todas as partículas."
        for i, p in enumerate(self.particles_.values()):
            p.set_data(a=A[i,:])

    def increment_accelerations(self, dt):
        "Incrementa o valor da aceleração das partículas devido as forças do sistema."
        for p in self.particles_.values():
            p.increment_acceleration()

    def update_accelerations(self, dt):
        "Atualiza o valor da aceleração das partículas devido as forças do sistema."
        for p in self.particles_.values():
            p.update_acceleration()

    def load_data(self, filename):
        "Carrega as partículas a partir de um arquivo de texto."

        # Carrega as informações das partículas (massa e raio)
        self.read_basic_data(filename)

        # Carrega as condições iniciais
        self.read_ini_conditions(filename)

    def read_basic_data(self, filename):
        "Lê as informações das partículas (massa e raio)."

        matrix = io.read_table_in_section(filename, 'Particles Data')

        for i in range(len(matrix)):
            self.create_particle(index = int(matrix[i,0]),
                                 m = matrix[i, 1],
                                 r = matrix[i, 2])

        # Alternano o tipo das partículas bypass
        props = io.read_keys_in_section(filename, 'Simulation Data', {'bypass': []})
        for index in props['bypass']:
            self.particles_[index].__class__ = Particle_ByPass

    def read_ini_conditions(self, filename):
        "Lê a condição inicial das partículas (x e v)."

        matrix = io.read_table_in_section(filename, 'Initial Conditions')
        indexes = []
        for i in range(len(matrix)):
            index = int(matrix[i, 0])
            if (index in indexes):
                print  'Erro: Duplicidade na condição inicial para partícula', index
                raw_input()
            else:
                indexes.append(index)

            try:
                self.particles_[index].set_data(x = matrix[i, 1:4],
                                                v = matrix[i, 4:7],
                                                a = matrix[i, 7:10])
            except KeyError:
                print 'Erro: Partícula', index, 'não foi definida em [Particles Data].'
                raw_input()

    def set_constant_forces(self, acceleration):
        "Lê as informações das forças constantes."

        for p in self.particles_.values():
            m = p.mass()
            F = Force_Constant(m*acceleration)
            p.set_external_force(F)
