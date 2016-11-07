# -*- coding: utf-8 -*-
# Autor: Bismarck Gomes Souza Junior <bismarckgomes@gmail.com>
# Data: 28/10/2016

import re, ast
import numpy as np
from StringIO import StringIO


def read_keys_in_section(filename, section, default={}, error_msg=True):
    "Lê os dados de uma seção."

    m = re.search(".*\[%s\].*\n(([^[]|(?<==| )\[)+)" % section, open(filename).read())

    if m:
        data = default

        new_data = []
        for a,b in re.findall("(\w+)\s*=\s*(.+)\s*(?:#.*)?\s*", m.group()):
            try:
                if ('[' in b):
                    val = eval(b)
                else:
                    val = ast.literal_eval(b)
            except:
                val = b

            new_data.append((a.lower(), val))

        # Atualiza novos dados
        data.update(new_data)

        return data

    else:
        if (error_msg):
            print 'Erro na seção', section, '!!'
            raw_input()

        return default


def read_table_in_section(filename, section, error_msg=True):
    "Lê uma tabela em uma seção."

    # Padrão de leitura
    pattern = ".*\[%s\].*\n(?:#.*\n)+((?:[^\n]{2,}\n)+)"

    m = re.search(pattern % section, open(filename).read())

    if m:
        try:
            matrix = np.loadtxt(StringIO(m.group(1)))

            if (len(matrix.shape) == 1):
                return np.array([matrix])
            else:
                return matrix

        except Exception,e:
            print str(e)
            print 'Erro ao ler a tabela na seção', section
            raw_input()
    else:
        if (error_msg):
            print 'Erro na seção ', section, '!'
            raw_input()

    return np.array([])


def read_lines_in_section(filename, section, error_msg=True):
    "Lê as linhas no interior de uma seção."

    m = re.search(".*\[%s\].*\n([^[]+)" % section, open(filename).read())

    if m:
        try:
            return m.group(1).strip().split('\n')

        except Exception,e:
            print str(e)
            print 'Erro ao ler as linhas na seção', section
            raw_input()
    else:
        if (error_msg):
            print 'Erro na seção ', section, '!!!'
            raw_input()

    return []

