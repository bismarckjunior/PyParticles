# PyParticles
Projeto destinado ao desenvolvimento de um simulador numérico de partículas
totalmente desenvolvido em Python 2.7.

## 1. Instalação
As dependências do simulador são: [Python 2.7][1] e [Paraview 5.0.1][2]. O Python
é necessário para a compilação do programa e o Paraview é uma interface de
visualização para os arquivos de saída. Caso o Paraview não esteja instalado a
visualização gráfica dos resultados não será possível.



## 2. Arquivo de Entrada
O arquivo de entrado do simulador possui extensão ".ini". Este arquivo é dividido
em seções. Existem 6 seções principais: 'Simulation Data', 'Output Data',
'Particles Data', 'Initial Conditions', 'Contacts Data' e 'Boundary Conditions'.

As seções podem conter chaves e valores, uma tabela ou um texto. Cada seção tem
uma forma de escrita diferente e serão detalhadas a seguir.

#### [Simulation Data]
Nesta seção existem chaves e valores, conforme o exemplo abaixo.

```text
[Simulation Data]
init_time = 0.0         # [Opcional] Tempo inicial da simulação [s]
time_step = 0.005       # Passo de tempo [s]
nSteps =  10000         # Número de passos de tempo [-]
a_const = [0.,0.,-10.]  # [Opcional] Aceleração externa [m/s²]
```

O tempo inicial de simulação (*init_time*) é opcional e por padrão é nulo.
Outro valor opcional é a aceleração externa (*a_const*) que atua em todas as
partículas durante toda a simulação e por padrão é nula.

Uma forma de introduzir os passos de tempo da simulação é utilizando as chaves
*time_step* e *nSteps*. Porém, uma forma alternativa é através de um vetor
com os passos de tempo, conforme o exemplo abaixo.

```text
[Simulation Data]
time_steps = [0.001]*300 + [0.005]*400
```

Neste exemplo, foi utilizado 300 passos de tempo de 0.001 segundos, seguidos de
400 passos de tempo de 0.005 segundos.

#### [Output Data]
Esta seção é **opcional** e serve para gerenciar os arquivos de saída e a visualização
da simulação. Ela contém chaves e valores, conforme o exemplo abaixo.

```text
[Output Data]
out_dir = "exemplo_5"            # [Opcional] Pasta na qual será inserido os arquivos de saída
main_file = "exemplo_5.out"      # [Opcional] Nome do arquivo principal de saída
video_file = "exemplo_5.avi"     # [Opcional] Nome do arquivo de vídeo
contacts_file = "exemplo_5.ctc"  # [Opcional] Nome do arquivo de forças nos contatos
view_step = 0.5                  # [Opcional] Passo de tempo para criação do vídeo
camera_position = [0., 0., 5.]   # [Opcional] Posição da camera
camera_focus = [0., 0., 0.]      # [Opcional] Posição da visão da camera
```


#### [Particles Data]
Nesta seção são informadas as propriedades das partículas como índice, raio e massa,
em forma de tabela, conforme o exemplo abaixo.

```text
[Particles Data]
#id    m[Kg]  r[m]
  1    1.0    1.0
  2    3.0    0.5
  3    1.5    2.0
```

#### [Initial Conditions]
Nesta seção são informadas as condições iniciais da simulação, em forma de tabela,
com informação como: posição (x, y, z), velocidade (vx, vy, vz) e aceleração (ax, ay, az),
conforme a tabela abaixo.

```text
#id    x[m]  y[m]   z[m]   vx[m/s]  vy[m/s]  vz[m/s]  ax[m/s2]  ay[m/s2]  az[m/s2]
  1    0.3   2.0    7.0    1.0      0.0      4.0      0.0       0.0       0.0
  2    5.0   4.0    0.0    0.5      1.0      0.0      0.0       0.0       0.0
  3    2.0  -3.0    6.0   -2.0      0.0      3.0      0.0       0.0       0.0
```

#### [Contacts Data]
Nesta seção são informados os dados do contato entre as partículas, em forma de
chave e valor, conforme o exemplo abaixo. Esta seção é **opcional**, caso não seja
inserida valores nulos serão atribuídos as variáveis.

```text
kn = 50.0      # [Opcional] Constante de rigidez [N/m]
ks = 20.0      # [Opcional] Constante de cisalhamento [N/m]
mu = 0.0       # [Opcional] Coeficiente de viscosidade [-]
db_max = 0.1   # [Opcional] Distância máxima para atração das partículas [m]
beta_n = 0.0   # [Opcional] Fator de amortecimento normal [-]
beta_s = 0.0   # [Opcional] Fator de amortecimento cisalhante [-]
```

A força normal entre as partículas pode ser atrativa ou repulsiva. Para cada
caso é possível fornecer uma constante de rigidez diferente. Para isso, basta
substituir a chave *kn* pelas chaves *kn_a* e *kn_r*.


#### [Boundary Conditions]
Esta seção é **opcional** e serve para definir as fronteiras do sistema. Atualmente,
apenas fronteiras planas são permetidas. Para inserir uma fronteira basta informar
um índice e a equação do plano, conforme o exemplo abaixo.

```text
[Boundary Conditions]
1:  x + 2y - 3*z = 4
2:  3*x -y + 5*z = 2
```

Para cada fronteira criada é possível modificar suas propriedades, criando uma seção
específica para cada uma delas. Por exemplo, para informar as propriedades
da fronteira 1 é necessário criar a seção [Boundary 1], conforme o exemplo abaixo.

```text
[Boundary Conditions]
1:  x + 2y - 3*z = 4

[Boundary 1]
type = 'Plane' # [Opcional] Tipo de fronteira
kn = 50.0      # [Opcional] Constante de rigidez [N/m]
ks = 20.0      # [Opcional] Constante de cisalhamento [N/m]
mu = 0.0       # [Opcional] Coeficiente de viscosidade [-]
db_max = 0.1   # [Opcional] Distância máxima para atração das partículas [m]
beta_n = 0.0   # [Opcional] Fator de amortecimento normal [-]
beta_s = 0.0   # [Opcional] Fator de amortecimento cisalhante [-]
```

Outros exemplos podem ser encontrados na pasta exemplos.


## 3. Execução
A execução do PyParticles resume-se ao script *PyParticles.py* e a um arquivo ".ini",
podendo ser realizada de duas formas: executando pelo terminal ou arrastando e
soltando.

### 3.1. Terminal
Para executar a partir de um terminal, basta dirigir-se para a pasta onde o script
*PyParticles.py* está localizado:

    $ cd PyParticles

Em seguida, executar o script *PyParticles.py* seguido do arquivo de entrada:

    $ python PyParticles.py /examples/example1.ini

### 3.2. Arrastando e Soltando
#### Windows
Para executar o simulador arrastando e soltando, basta arrastar o arquivo de entrada
para o script *PyParticles.py*.

#### Linux
Para usuários linux, é necessário criar um arquivo *PyParticles.desktop*, conforme
o exemplo abaixo.

```text
[Desktop Entry]
Type=Application
Terminal=true
Exec=python ~/Documentos/Git/PyParticles/PyParticles.py
Name=PyParticles
```

Em seguida, deve-se tornar o script *PyParticles.py* e o arquivo *PyParticles.desktop*
executáveis. Finalmente, basta arrastar o arquivo de entrada para o arquivo
*PyPartices.desktop*.


## 4. Arquivos de Saída
Durante a execução do simulador, são criados os arquivos ".out" e ".ctc" e, caso
o Paraview esteja instalado, um arquivo de video (".avi").

#### 4.1. Arquivo Principal (.out)
Este arquivo contém as informações básicas da simulação como posição, velocidade e aceleração,
para cada partícula, conforme o exemplo abaixo.

```text
==============  PyParticles 0.1  ==============

% Particles data
#Time
0.000000E+00
#id   x          y          z          vx         vy         vz         ax         ay         az
001   0.000E+00  0.000E+00  0.000E+00  1.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00
002   1.000E+00  1.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00
003   2.000E+00  0.000E+00  2.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00

#Time
5.000000E-03
#id   x          y          z          vx         vy         vz         ax         ay         az
001   5.000E-03  0.000E+00  0.000E+00  1.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00
002   1.000E+00  1.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00
003   2.000E+00  0.000E+00  2.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00

#Time
1.000000E-02
#id   x          y          z          vx         vy         vz         ax         ay         az
001   1.000E-02  0.000E+00  0.000E+00  1.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00
002   1.000E+00  1.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00
003   2.000E+00  0.000E+00  2.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00
```

#### 4.2. Arquivo de Forças no Contato (.ctc)

Este arquivo contém as informações sobre as forças existentes no contato como
os índices das partículas ou fronteiras envolvidas, o tipo de contato (P: contato
entre partículas e B: contato com fronteria), força normal (Fn),
força cisalhante (Fs), força de amortecimento normal (Fdn) e
força de amortecimento cisalhante (Fds), conforme o exemplo abaixo.

```text
#Time
0.000000E+00

#Time
5.000000E-03
# id0  id1  Type  Time       Fn[x]      Fn[y]      Fn[z]      Fs[x]      Fs[y]      Fs[z]      Fdn[x]     Fdn[y]     Fdn[z]     Fds[x]     Fds[y]     Fds[z]
  001  002  P     5.000E-03  0.000E+00  0.000E+00  1.956E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00 -0.000E+00 -0.000E+00 -0.000E+00
  001  001  B     5.000E-03  0.000E+00  0.000E+00  2.956E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00  0.000E+00 -0.000E+00 -0.000E+00 -0.000E+00
```



[1]:http://www.python.org/download/releases/2.7/
[2]:http://www.paraview.org/download/

