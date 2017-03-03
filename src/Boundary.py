# -*- coding: utf-8 -*-
# Autor: Bismarck Gomes Souza Junior <bismarckgomes@gmail.com>
# Data: 03/10/2016

import re
import numpy as np

N_DIMENSION = 3


class Boundary:
    type_ = ''

    def __init__(self, index):
        "Construtor."
        self.id_ = index
        self.props_ = {'constraint': 'True'}
        self.particles_ = []

    def __str__(self):
        "Retorna o texto referente aos dados da fronteira."
        text =  '[Boundary %d]\n' % self.id_
        text += 'type = "%s"\n' % self.type_

        cons = self.props_['constraint']
        if (cons != 'True'):
            text += 'constraint = "%s"\n' % cons

        return text

    def get_index(self):
        "Retorna o índice da fronteira."
        return self.id_

    def add_particle(self, p):
        "Adiciona uma partícula em contato com a fronteira."
        self.particles_.append(p)

    def remove_particle(self, p):
        "Remove a partícula da lista das partículas em contato com a fronteira."
        self.particles_.remove(p)

    def has_particle(self, p):
        "Retorna true se a partícula [p] faz contato com a fronteira."
        return p in self.particles_

    def constraint(self):
        "Retorna a restrição da fronteira."
        return self.props_['constraint']

    def normal_vector(self, p):
        "Retorna o vetor normal referente ao contato."
        pass

    def load_constaint(self, text_constraint):
        "Carrega as restrições da equação."
        a = np.zeros(N_DIMENSION)

        test_constraint = text_constraint

        # Modificando a restrição para o teste
        for var, array in zip(['x', 'y', 'z'], ['a[0]', 'a[1]', 'a[2]']):
            test_constraint = test_constraint.replace(var, array)

        try:
            # Testando a restrição
            eval(test_constraint)
            self.props_['constraint'] = text_constraint.strip()

        except:
            print 'Erro na restrição', text_constraint
            raw_input()

    def update_properties(self, props):
        "Atualiza as propriedades da fronteira."
        self.props_.update(props)

    def distance_border(self, p0):
        "Distância entre a borda da partícula e a fronteira."
        return self.distance(p0) - p0.r()

    def get_properties(self):
        "Retorna as propriedades da fronteira."
        return self.props_.copy()

    def get_property(sef, key):
        "Retorna o valor de uma propriedade."
        return self.props_[key]

    def distance(self, p0):
        "Distância entre o centro da partícula e a fronteira."
        pass

    def load_data(self, text_equation):
        "Carrega os dados da condição de contorno."
        pass


class Boundary_Plane(Boundary):
    type_ = 'plane'

    def __init__(self, index):
        "Construtor."
        Boundary.__init__(self, index)

        self.normal_ = np.zeros(N_DIMENSION)
        self.const_ = 0.0
        self.side_ = 1

    def get_normal(self):
        "Retorna o vetor normal do plano."
        return np.copy(self.normal_)

    def get_constant(self):
        "Retorna a constante do plano."
        return self.const_

    def __str__(self):
        "Retorna o texto referente aos dados da fronteira."
        text =  Boundary.__str__(self)
        text += 'normal = %s\n' % str(list(self.normal_))
        text += 'constant = %f\n' % self.const_

        for i in range(3):
            point = 'point%d' % i
            text += '%s = %s\n' % (point, self.props_[point])

        return text

    def distance(self, p):
        "Distância entre a centro da partícula [p] e a fronteira."
        return abs(self.distance_signed(p))

    def distance_signed(self, p):
        """Distância entre a centro da partícula [p] e a fronteira. Retorna um
        número positivo se o vetor normal e o centro da partícula estiverem no
        mesmo lado do plano. Retorna um número negativo, caso contrário."""
        return np.dot(p.x(), self.normal_) + self.const_

    def normal_vector(self, p):
        "Retorna o vetor normal ao contato referente a partícula [p]."
        if (self.distance_signed(p) > 0):
            # Neste caso a partícula está do mesmo lado do plano (ref. normal)
            return -self.normal_

        else:
            # Neste caso a partícula está do lado oposto ao plano (ref. normal)
            return self.normal_


    def load_data(self, text_equation):
        "Carrega os dados da condição de contorno, considerando um plano."

        if '|' in text_equation:
            equation, constraint = tuple(text_equation.split('|'))

            # Carrega a restrição
            self.load_constaint(constraint)

        else:
            equation = text_equation

        # Remove os espaços em branco
        equation = equation.replace(' ', '')

        m = re.search("(?:[-+]?[\d.]*\*?[xyz])+([-+][\d.]*)?=([-+]?[\d.]*)", equation)

        # Verifica se a equação do plano está correta
        if m:
            # Constante do lado direito
            self.const_ = - float(m.group(2))

            # Constante do lado esquerdo
            if m.group(1):
                self.const_ += float(m.group(1))

            self.normal_ = np.zeros(N_DIMENSION)

            # Dicionário de transformação
            d = {'x': 0, 'y': 1, 'z': 2}

            # Carregando o vetor normal
            for value, var in re.findall("([-+]?[\d.]*)\*?([xyz])", equation):
                if value == '' or value == '+':
                    self.normal_[d[var]] = 1.0

                elif value == '-':
                    self.normal_[d[var]] = -1.0

                else:
                    self.normal_[d[var]] = float(value)

            norm = np.linalg.norm(self.normal_)

            self.normal_ /= norm
            self.const_ /= norm

        else:
            print 'Erro na equação do plano:', text_equation
            raw_input()
