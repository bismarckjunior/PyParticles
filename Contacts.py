# -*- coding: utf-8 -*-
# Autor: Bismarck Gomes Souza Junior <bismarckgomes@gmail.com>
# Data: 10/10/2016

import numpy as np
import IOControl as io
from Forces import *
from Damping import *
from Contact import *


class Contacts:
    type_ = ''
    def __init__(self):
        self.contacts_particles_ = []
        self.contacts_boundaries_ = []
        self.props_ = {}

        self.nContacts_particles_ = 0
        self.nContacts_boundaries_ = 0


    def __len__(self):
        "Retorna o número de contatos."
        return self.nContacts_particles_ + self.nContacts_boundaries_

    def __str__(self):
        "Retorna um texto que representa as forças no contato."
        if (len(self) > 0):
            # HEADER
            text = '# id0  id1  Type  Time       '

            for F in ['Fn', 'Fs', 'Fdn', 'Fds']:
                for i in ['x', 'y', 'z']:
                    text += '%s[%s]' % (F, i)
                    text += ' '*(8-len(F))

            # DATA
            for type_, contacts  in zip(['P', 'B'], [self.contacts_particles_, self.contacts_boundaries_]):
                for contact in contacts:
                    text += '\n'
                    text += '  %03d' % contact.get_index(0)
                    text += '  %03d' % contact.get_index(1)
                    text += '  %s   ' % type_
                    text += ' %10.3E' % contact.get_contact_time()

                    for F in ['Fn', 'Fs', 'Fdn', 'Fds']:
                        force = contact.get_specific_force(F)
                        for i in range(N_DIMENSION):
                            text += ' %10.3E' % force[i]

            return text + '\n'
        else:
            return ''

    def get_contact_particles(self, index):
        "Retorna o contato entre partículas de índice [index]."
        return self.contacts_particles_[index]

    def get_contact_boundaries(self, index):
        "Retorna o contato, com fronteira, de índice [index]."
        return self.contacts_boundaries_[index]

    def update_forces(self, dt):
        "Atualiza as forças nos contatos."
        for c in self.contacts_particles_ + self.contacts_boundaries_:
            c.update_force(dt)

    def load_data(self, filename):
        "Carrega os dados do contato a partir de um arquivo de texto."
        # Defaults
        default = {'kn': 0.0,
                   'ks': 0.0,
                   'mu': 0.0,
                   'db_max': 0.0,
                   'beta_n': 0.0,
                   'beta_s': 0.0}

        # Lendo dados da seção 'Contacts Data'
        data = io.read_keys_in_section(filename, 'Contacts Data', default, False)

        if ('kn_a' in data and data['kn_a'] !=0 and data['db_max'] == 0.0):
            print 'Ops... Desconsiderando força atrativa!'
            print '  Para considerar a forca atrativa especifique o valor de'
            print '  db_max (distância máxima permitida) em [Contacts Data].'

        data['kn_a'] = data['kn_a'] if 'kn_a' in data else data['kn']
        data['kn_r'] = data['kn_r'] if 'kn_r' in data else data['kn']

        self.props_.update(data)

        return self.props_

    def create_contact_particles(self, p, q):
        "Cria um novo contato entre duas partículas."
        contact = Contact_Particles(p, q, self.props_)
        p.add_contact_particles(q.index(), contact)
        q.add_contact_particles(p.index(), contact)
        self.contacts_particles_.append(contact)
        self.nContacts_particles_ += 1

    def create_contact_boundaries(self, p, boundary):
        "Cria um novo contato entre uma partícula e uma fronteira."
        contact = Contact_Boundary(p, boundary)
        p.add_contact_boundary(boundary.get_index(), contact)
        boundary.add_particle(p)
        self.contacts_boundaries_.append(contact)
        self.nContacts_boundaries_ += 1

    def remove_contact_particles(self, p, q):
        "Remove um contato entre duas partículas."
        id_p, id_q = p.index(),  q.index()

        for i, contact in enumerate(self.contacts_particles_):
            if (contact.has_particle(id_p) and contact.has_particle(id_q)):
                del self.contacts_particles_[i]
                self.nContacts_particles_ -= 1

                p.remove_contact_particles(id_q, contact)
                q.remove_contact_particles(id_p, contact)
                break
        else:
            print 'Erro ao remover contato!'
            return

        del contact

    def remove_contact_boundaries(self, p, boundary):
        "Remove um contato entre uma partícula e uma fronteira."
        id_p = p.index()
        for i, contact in enumerate(self.contacts_boundaries_):
            if (contact.has_particle(id_p)):
                del self.contacts_boundaries_[i]
                self.nContacts_boundaries_ -= 1

                p.remove_contact_boundary(boundary.get_index(), contact)
                boundary.remove_particle(p)
                break
        else:
            print 'Erro ao remover contato!!!'
            return

        del contact

    def search_contacts(self, particles, boundaries):
        "Procura por todos os contatos."
        list_particles = particles.get_particles()
        list_boundaries = boundaries.get_boundaries()
        self.search_contacts_particles(list_particles)
        self.search_contacts_boundaries(list_particles, list_boundaries)

    def search_contacts_particles(self, list_particles):
        "Procura pelos contatos do tipo partícula-partícula."
        nParticles = len(list_particles)
        X = np.empty((nParticles, N_DIMENSION))
        R = np.empty(nParticles)

        # Lista dos índices das partículas
        list_indexes = np.array([p.index() for p in list_particles])

        # Preenche a matriz com as posições das partículas
        for i, p in enumerate(list_particles):
            X[i,:] = p.x()
            R[i] = p.r()

        # Percorre todas as partículas de trás para frente
        for p in list_particles[:-1]:
            x = X[0]
            r = R[0]
            X = np.delete(X, 0, 0)
            R = np.delete(R, 0, 0)

            neighbors = p.get_neighbor_particles()
            neighbors.sort()

            # Vetor de boleanos para a condição |X-X| < R+r
            pos = np.linalg.norm(X-x,axis=1) <= R+r+self.props_['db_max']

            # Procura pelos contatos
            for c in list_indexes[-len(pos):][pos]:
                # Adiciona um contato caso ele não exista
                if (c not in neighbors):
                    index = list(list_indexes).index(c)
                    self.create_contact_particles(p, list_particles[index])
                else:
                    neighbors.remove(c)

            # Remove os contatos que não existem mais
            for c in neighbors[::-1]:
                if (c > p.index()):
                    index = list(list_indexes).index(c)
                    self.remove_contact_particles(p, list_particles[index])

    def search_contacts_boundaries(self, list_particles, list_boundaries):
        "Procura pelos contatos do tipo partícula-fronteira."

        # Percorre todas as partículas de trás para frente
        for p in list_particles:
            neighbors = p.get_neighbor_boundaries()

            for boundary in list_boundaries:
                index = boundary.get_index()

                # O sinal da distância represneta em que lado a partícula está
                # com relação ao plano.
                d = boundary.distance_border(p)

                if (boundary.distance_border(p) <= boundary.props_['db_max']):
                    # Cria um contato caso ele não exista
                    if (index not in neighbors):
                        self.create_contact_boundaries(p, boundary)

                else:
                    # Remove os contatos que não existem mais
                    if (index in neighbors):
                        self.remove_contact_boundaries(p, boundary)
