from paraview.simple import *
import re, os, sys
import numpy as np
from StringIO import StringIO

PATH = r'/home/bismarck/Downloads/Temp/PyParticle/examples'
TIME_STEP = 0.1
OUT_BAR_WIDTH = 70

sys.path.append(PATH)
sys.path.append(os.path.dirname(PATH))

import IOControl as io

try:
    os.chdir(PATH)
except:
    os.chdir(raw_input('Insira o caminho onde estao os exemplos:'))

list_files = os.listdir('.')
list_files.sort()

filenames = filter(lambda x: x.endswith('.out') and not x.endswith('_forces.out'), list_files)

if not filenames:
    print "No out file in:", PATH
    filename = raw_input('Digite o caminho do arquivo out:')
else:
    filename = filenames[-1]
    print "Reading file", filename, '...'

i = 0
t_old = 0.0
data = {}
times = []
show_indexes = []
for t, m in re.findall("#Time\n(.*)\n\n?#.*\n((?:[^\n]{2,}\n)+)", open(filename, 'r').read()):
    t = float(t)
    times.append(t)
    matrix = np.loadtxt(StringIO(m))
    if (len(matrix.shape) == 1):
        matrix = np.array([matrix])

    data[i] = matrix[:,1:]

    # Time step condition
    if (t-t_old >= TIME_STEP):
        show_indexes.append(i)
        t_old = t

    i += 1

# Adding last simulation time
if (show_indexes[-1] != i-1):
    show_indexes.append(i-1)

# Initializing...
renderView1 = CreateView('RenderView')
scene = GetAnimationScene()

scene.PlayMode = 'Real Time'
scene.Duration = int(times[-1])
scene.EndTime = times[-1]


print 'Creating Planes...'

planes = []

i = 1
while (True):
    data_tmp = io.read_keys_in_section(filename, 'Boundary %d' % i, {}, False)

    if (data_tmp == {}):
        break

    plane = Plane()
    plane.Origin = data_tmp['point0']
    plane.Point1 = data_tmp['point1']
    plane.Point2 = data_tmp['point2']
    planes.append(plane)
    disp = Show()
    # disp.ColorArrayName = [None, '']
    disp.DiffuseColor = [0.0, 0.45, 0.0]
    # disp.GlyphType = 'Arrow'

    i += 1

print 'Creating spheres...'

spheres = []
pattern = ".*\[%s\].*\n(?:#.*\n)+((?:.{2,}\n?)+)"


# Create spheres according initial conditions
filename = filename[:-3] + 'ini'
m = re.search(pattern % "Particles Data", open(filename).read())
if m:
    p_matrix = np.loadtxt(StringIO(m.group(1)))
    if (len(p_matrix.shape) == 1):
        p_matrix = np.array([p_matrix])
    init_condition = data[0]

    for i in range(len(p_matrix)):
        sphere = Sphere(Radius=p_matrix[i, 2], PhiResolution=30, ThetaResolution=30)
        sphere.Center = init_condition[i, 0:3]

        spheres.append(sphere)
        Show()

Render()



print 'Creating animation...'

# Create animation view
cues = []
for s, sphere in enumerate(spheres):
    cues_ = []
    for i in range(3):
        cues_.append(GetAnimationTrack("Center", i, sphere))
        frame = CompositeKeyFrame()
        frame.KeyTime = 0.0
        frame.KeyValues = [data[0][s][i]]
        cues_[-1].KeyFrames.append(frame)

    cues.append(cues_)


# Print bar edges
print '-'*OUT_BAR_WIDTH
last_time = times[-1]

aux1 = aux2 = 0
k = float(OUT_BAR_WIDTH)/len(show_indexes)
# Create frames
for index in show_indexes:
    time = times[index]/last_time

    for s in range(len(spheres)):
        for i in range(3):
            d = data[index][s][i]
            if (d != data[index-1][s][i]):
                frame = CompositeKeyFrame()
                frame.KeyTime = time
                frame.KeyValues = [d]
                cues[s][i].KeyFrames.append(frame)

    # Print bar
    aux1 += 1
    c = int(k*aux1-aux2)
    if (c >= 1):
        sys.stdout.write('|'*c)
        aux2 += c

t = show_indexes[-1]
for s in range(len(spheres)):
    for i in range(3):
        frame = CompositeKeyFrame()
        frame.KeyTime = 1.0
        frame.KeyValues = [data[t][s][i]]
        cues[s][i].KeyFrames.append(frame)


# Print bar edges
print
print '-'*OUT_BAR_WIDTH
print

print dir(scene)

# raw_input()
scene.Loop = 1
# scene.Play()
# WriteAnimation("/home/bismarck/Downloads/Temp/PyParticle/examples/t.avi",Magnification=1, FrameRate=50.0, Compression=True, Quality=2)

# raw_input()
