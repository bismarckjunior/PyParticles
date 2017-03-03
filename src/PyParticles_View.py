# -*- coding: utf-8 -*-
# Autor: Bismarck Gomes Souza Junior <bismarckgomes@gmail.com>
# Data: 05/11/2016


try:
    from Boundary import *
    import paraview.simple as pv
    import os, sys


    class Paraview():

        def __init__(self):
            "Construtor."
            self.objects_ = {'tracks': {}}
            self.id_ = 0

        def create_view(self):
            "Inicialização da visualização."
            self.objects_['render'] = pv.CreateView('RenderView')

        def create_scene(self, start, end, duration, mode='Real Time', loop=True):
            "Inicializa a visualização da animação."
            scene = pv.GetAnimationScene()
            scene.EndTime = end
            scene.Duration = duration
            scene.StartTime = start
            scene.PlayMode = mode
            scene.Loop = int(loop)

            self.objects_['scene'] = scene

        def create_plane(self, origin, P1, P2, color_RGB=[0., 0.45, 0.]):
            "Cria um plano."
            plane = pv.Plane()
            plane.Origin = origin
            plane.Point1 = P1
            plane.Point2 = P2

            disp = pv.Show()
            disp.DiffuseColor = color_RGB

            self.id_ += 1
            self.objects_ [self.id_] = plane

            return self.id_

        def create_sphere(self, r, center, color_RGB=[1.,1.,1.], phiRes=30, thetaRes=30):
            "Cria uma esfera."
            sphere = pv.Sphere(Radius=r, PhiResolution=phiRes, ThetaResolution=thetaRes)
            sphere.Center = center

            disp = pv.Show()
            disp.DiffuseColor = color_RGB

            self.id_ += 1
            self.objects_[self.id_] = sphere

            return self.id_

        def add_frame_to_track(self, track, time, value):
            "Adiciona um frame a uma propriedade."
            frame = pv.CompositeKeyFrame()
            frame.KeyTime = time
            frame.KeyValues = [value]
            track.KeyFrames.append(frame)

        def create_tracks_for_sphere(self, id_sphere):
            "Cria os tracks para uma esfera de índice [id_sphere]."
            sphere = self.objects_[id_sphere]
            tracks = []
            for i in range(3):
                tracks.append(pv.GetAnimationTrack("Center", i, sphere))

            self.objects_['tracks'][id_sphere] = tracks

        def set_camera_parameters(self, position, focus):
            "Configura os parametros da camera."
            r = self.objects_['render']
            if (position is not None):
                r.CameraPosition = position

            if (focus is not None):
                r.CameraFocalPoint = focus

        def update_view(self):
            "Atualiza a visualização para uma mudança de tempo."
            self.objects_['scene'].GoToLast()

        def show(self):
            "Gera a visualização."
            pv.Render()

        def play(self):
            "Anima a visualização."
            self.objects_['scene'].Play()

        def write_animation(self, filename, frameRate=100.0):
            "Salva a animação."
            # sys.stderr = open(os.devnull, "w")
            pv.WriteAnimation(filename, Magnification=1, Quality=2, Compression=True,
                              FrameRate=frameRate)
            # sys.stderr = sys.__stdout__

        # def export_to_python(self, filename):
        #     "Exporta a visualização para um arquivo python ou psvm."
        #     pv.servermanager.SaveState(filename)


    class PyParticles_View(Paraview):
        "Classe que gerencia a visualização do simulador PyParticles."

        def init_view(self, t0, dt):
            "Inicia a visualização."
            self.create_view()
            self.create_scene(t0, t0+dt, dt)

        def create_particles(self, particles):
            "Cria as partículas."
            self.id_particles_ = []

            for p in particles.get_particles():
                id_ = self.create_sphere(p.r(), p.x())
                self.create_tracks_for_sphere(id_)
                self.id_particles_.append(id_)

        def create_boundaries(self, boundaries):
            "Cria as fronteiras."
            self.id_boundaries_ = []

            for b in boundaries.get_boundaries():
                if (b.__class__ == Boundary_Plane):
                    props = b.get_properties()
                    id_ = self.create_plane(props['point0'], props['point1'], props['point2'])
                    self.id_boundaries_.append(id_)

        def create_particle_frame(self, time, X_new, X_old):
            "Cria um frame para cada partícula que mudou de posição."
            for i, id_ in enumerate(self.id_particles_):
                for j in range(3):
                    x = X_new[i][j]
                    if (x != X_old[i][j]):
                        track = self.objects_['tracks'][id_][j]
                        self.add_frame_to_track(track, time, x)

except ImportError:
    print 'Não foi possível encontrar o Paraview instalado.'
    raw_input('Deseja continuar?')

    class PyParticles_View():

        def init_view(self, t0, dt):
            "Inicia a visualização."
            pass

        def create_particles(self, particles):
            "Cria as partículas."
            pass

        def create_boundaries(self, boundaries):
            "Cria as fronteiras."
            pass

        def create_particle_frame(self, time, X_new, X_old):
            "Cria um frame para cada partícula que mudou de posição."
            pass

        def show(self):
            "Gera a visualização."
            pass

        def play(self):
            "Anima a visualização."
            pass

        def write_animation(self, filename, frameRate=100.0):
            "Salva a animação."
            pass

        def set_camera_parameters(self, position, focus):
            "Configura os parametros da camera."
            pass

        def update_view(self):
            "Atualiza a visualização para uma mudança de tempo."
            pass
