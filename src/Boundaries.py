# -*- coding: utf-8 -*-
# Autor: Bismarck Gomes Souza Junior <bismarckgomes@gmail.com>
# Data: 28/10/2016

import numpy as np
import IOControl as io
from Boundary import *
from Contacts import Contacts
from collections import OrderedDict


class Boundaries:

    def __init__(self):
        "Construtor."
        self.boundaries_ = OrderedDict()
        self.nBoundaries_ = 0

    def __str__(self):
        "Retorna o texto referente aos dados das fronteiras."
        if (self.get_nBoundaries() == 0):
            return ''

        text = '% Boundary Data\n'

        for boundary in self.boundaries_.values():
            text += str(boundary) + '\n'

        return text

    def get_nBoundaries(self):
        "Retorna o número de fronteiras."
        return self.nBoundaries_

    def get_boundaries(self):
        "Retorna uma lista com todas as fronteiras."
        return self.boundaries_.values()

    def get_boundary(self, index):
        "Retorna a fronteira de índice [index]."
        return self.boundaries_[index]

    def add_boundary(self, index, boundary):
        "Adiciona uma condição de fronteira."
        if (index in self.boundaries_):
            print 'Erro: Duplicidade de fronteiras. A fronteira', index, 'já existe.'
            raw_input()

        self.boundaries_[index] = boundary
        self.nBoundaries_ += 1

    def read_boundary_properties(self, filename, id_boundary):
        "Lê as propriedades da fronteira especificada."
        # Lendo dados da seção 'Contacts Data'
        data = Contacts().load_data(filename)
        data.update({'type': 'plane',
                     'x_lim': [0., 0.],
                     'y_lim': [0., 0.]})

        # Atualiza com as informações do contorno
        props = io.read_keys_in_section(filename, 'Boundary %s' % id_boundary, data, False)

        if ('kn_a' in props and props['kn_a'] !=0 and props['db_max'] == 0.0):
            print 'Ops... Desconsiderando força atrativa!'
            print '  Para considerar a forca atrativa especifique o valor de'
            print '  db_max (distância máxima permitida) em [Contacts props].'

        if (props['kn'] != 0.0 and props['kn_a'] == 0.0):
            props['kn_a'] = props['kn']

        if (props['kn'] != 0.0 and props['kn_r'] == 0.0):
            props['kn_r'] = props['kn']

        return props


    def load_data(self, filename):
        "Carrega os dados das fronteiras a partir de um arquivo de texto."

        indexes = []
        for line in io.read_lines_in_section(filename, 'Boundary Conditions', 0):
            id_boundary, equation = line.split(':')

            if (id_boundary not in indexes):
                indexes.append(id_boundary.strip())
            else:
                print 'Erro: Índices iguais nas condições de contorno.'
                raw_input()

            # Lê as propriedades do contato
            props = self.read_boundary_properties(filename, id_boundary)

            if (props['type'].lower() == 'plane'):
                self.create_boundary_plane(id_boundary, equation, props)

            else:
                print "Erro: Não existe a condição de contorno especificada!"
                print "Tipo:", props['type']
                print line
                raw_input()

    def create_boundary_plane(self, id_boundary, text_equation, props):
        "Carrega os dados da fronteira considerando como um plano."
        index = int(id_boundary)
        boundary = Boundary_Plane(index)
        boundary.load_data(text_equation)

        n = boundary.get_normal()
        c = boundary.get_constant()

        def plane(x,y):
            return - (np.dot([x,y], n[:2]) + c)/n[2]

        x0, x1 = tuple(props['x_lim'])
        y0, y1 = tuple(props['y_lim'])
        z00 = plane(x0, y0)
        z10 = plane(x1, y0)
        z01 = plane(x0, y1)

        props['point0'] = [x0, y0, z00]
        props['point1'] = [x1, y0, z10]
        props['point2'] = [x0, y1, z01]

        boundary.update_properties(props)
        self.add_boundary(index, boundary)
