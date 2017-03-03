#!/usr/bin/python
# -*- coding: utf-8 -*-
# Autor: Bismarck Gomes Souza Junior <bismarckgomes@gmail.com>
# Data: 03/10/2016

import os
import numpy as np
import IOControl as io
from Particles import Particles
from Contacts import Contacts
from Boundaries import Boundaries
from PyParticles_View import *

class PyParticles:

    def __init__(self, ini_file, main_dir=''):
        "Construtor."
        self.view_ = PyParticles_View()
        self.contacts_ = Contacts()
        self.particles_ = Particles()
        self.boundaries_ = Boundaries()

        self.ini_file_ = ini_file

        if (main_dir == ''):
            self.main_dir_ = os.path.dirname(ini_file)
        else:
            self.main_dir_ = main_dir

        # Lê o arquivo principal
        self.read_ini_file()

        # Inicializa a visualização
        self.init_view()

    def init_view(self):
        "Inicializa a visualização."
        # Duração da simulação
        Dt = self.time_ + sum(self.dt_)
        self.end_time_ = self.time_ + Dt

        # Inicializa as variáveis da simulação
        self.view_.init_view(self.time_, int(Dt))

        # Criando partículas e fronteiras
        self.view_.create_particles(self.particles_)
        self.view_.create_boundaries(self.boundaries_)

        # Criando frame inicial
        X = self.particles_.get_positions()
        self.view_.create_particle_frame(self.time_, X, X-1.)

        # Configurando a camera
        self.view_.set_camera_parameters(self.camera_position_, self.camera_focus_)

        # Plota a visualização
        self.view_.show()

    def export_results(self):
        "Exporta os resultados da simulação e visualiza."
        # self.view_.export_to_python(self.python_file_)
        self.view_.write_animation(self.video_file_)
        self.view_.play()

    def read_ini_file(self):
        "Lê o arquivo de entrada."
        # Carrega as informações das partículas e dos contatos
        self.particles_.load_data(self.ini_file_)

        # Carrega as informações dos contatos
        self.contacts_.load_data(self.ini_file_)

        # Carrega as informações das fronteiras
        self.boundaries_.load_data(self.ini_file_)

        # Carrega as informações da simulação
        self.load_simulation_data(self.ini_file_)

        # Carrega as informações de saída
        self.load_output_data(self.ini_file_)

    def load_simulation_data(self, filename):
        "Carrega as informações básicas da simulação."
        # Parâmetros default
        default = { 'init_time': 0.0,
                    'a_const': [0.,0.,0.],
                    'time_step': 0.0,
                    'nsteps': 1,
                    'time_steps': [0.0] }

        props = io.read_keys_in_section(filename, 'Simulation Data', default)

        # Tempo inicial da simulação
        self.time_ = props['init_time']
        self.t_old_ = self.time_

        # Forças externas constantes
        self.particles_.set_constant_forces(np.array(props['a_const']))

        # Passo de tempo
        if (props['time_step'] != 0.0):
            self.dt_ = props['nsteps']*[props['time_step']]
        else:
            self.dt_ = props['nsteps']*props['time_steps']

    def load_output_data(self, filename):
        "Carrega as informações de saída do simulador."
        # Parâmetros default
        default = {'out_dir': os.path.basename(self.ini_file_)[:-4],
                   'main_file': os.path.basename(self.ini_file_)[:-4] + '.out',
                   'video_file': os.path.basename(self.ini_file_)[:-4] + '.avi',
                   'python_file': os.path.basename(self.ini_file_)[:-4] + '.py',
                   'contacts_file': os.path.basename(self.ini_file_)[:-4] + '.ctc',
                   'view_step': 0.1,
                   'camera_focus': None,
                   'camera_position': None}

        # Lê a seção Ouput Data
        data = io.read_keys_in_section(filename, 'Output Data', default, False)

        # Diretório de saída
        out_dir = self.main_dir_ + '/' + data['out_dir'].strip() + '/'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        # Arquivo de principal de saída
        self.out_main_file_ = out_dir + data['main_file']

        # Arquivo de contatos
        self.out_contact_file_ = out_dir + data['contacts_file']

        # Passo de tempo da visualização
        self.view_step_ = data['view_step']

        # Arquivo de video
        self.video_file_ = out_dir + data['video_file']

        # Arquivo de visualização
        self.python_file_ = out_dir + data['python_file']

        # Posição da camera
        self.camera_position_ = data['camera_position']

        # Foco da camera
        self.camera_focus_ = data['camera_focus']

    def iterate_t(self, dt):
        "Realiza uma iteração no tempo."
        # Determina os contatos
        self.contacts_.search_contacts(self.particles_, self.boundaries_)

        # Atualiza as forças devido aos novos contatos
        self.contacts_.update_forces(dt)

        if (self.time_ == dt):
            # Primeiro passo de tempo

            # Incrementa as velocidades devido a forças do sistema
            self.particles_.increment_accelerations(dt)

            self.X = self.particles_.get_positions()
            self.V = self.particles_.get_velocities()
            self.A = self.particles_.get_accelerations()

        else:
            self.particles_.update_accelerations(dt)

        # Calcula as novas posições das partículas
        X_new = self.X + self.V*dt + 0.5*self.A*dt**2

        # Atualiza as posições das partículas
        self.particles_.set_positions(X_new)

        # Atualiza as forças devido a mudança de posição
        self.contacts_.update_forces(0.0)

        # Atualiza as acelerações devido ao deslocamento
        self.particles_.update_accelerations(0.0)
        A_new = self.particles_.get_accelerations()
        V_new = self.V + 0.5*(self.A+A_new)*dt

        # Atualiza as velocidades e as acelerações das partículas
        self.particles_.set_velocities(V_new)
        self.particles_.set_accelerations(A_new)

        # Atualiza a visualização
        if (self.time_- self.t_old_ > self.view_step_):
            t = self.time_/self.end_time_
            self.view_.create_particle_frame(t, X_new, self.X)
            self.view_.update_view()
            self.view_.show()
            self.t_old_ = self.time_

        # Update variables in time
        self.X = X_new
        self.V = V_new
        self.A = A_new

    def run(self):
        "Executa o simulador."
        # Abre o arquivo de saída
        self.f = open(self.out_main_file_, 'w')

        # Abre o arquivo de saída de forças
        self.f_forces = open(self.out_contact_file_, 'w')

        # Escreve o header do arquivo de saída
        self.write_output_header()

        for dt in self.dt_:
            # Atualiza o tempo
            self.time_ += dt

            # Executa as iterações
            self.iterate_t(dt)

            # Escreve os dados das partículas
            self.write_output_time()

        # Fecha o arquivo de saída
        self.f.close()

        self.export_results()

        self.f_forces.close()

    def write_output_header(self):
        "Escreve o cabeçalho do arquivo de saída."
        text =  "==============  PyParticles 0.1  ==============\n\n"
        text += "\n% Particles data\n"

        self.f.write(text)
        self.write_output_time()

    def write_output_time(self):
        "Escreve as posições das partículas do tempo atual."
        # Imprime os dados das partículas
        print >> self.f, "#Time\n%E\n" % self.time_,
        print >> self.f, self.particles_

        # Imprime os dados dos contatos
        print >> self.f_forces, "#Time\n%E\n" % self.time_,
        print >> self.f_forces, str(self.contacts_)

if __name__ == '__main__':
    import sys

    try:
        if len(sys.argv) > 1:
            ini_file = sys.argv[1]

        else:
            print 'Arraste uma arquivo ".ini" para o este script.'
            raw_input()

        sim = PyParticles(ini_file)
        sim.run()

    except:
        print sys.exc_info()[0]
        import traceback
        print traceback.format_exc()

    finally:
        raw_input('\nEND')
