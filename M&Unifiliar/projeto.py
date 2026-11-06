"""Compatibilidade de imports. Novas extensões devem usar nucleo.pacotes."""
from nucleo.documento import *
from configuracao import PACOTES_PADRAO
from nucleo.pacotes import obter
from pacotes.legado import CARGAS, MOTOR_FF
FOLHAS = ("Unifilar","Multifilar")
GRUPOS = obter("eletrica.unifilar").categorias
CONDUTORES = obter("eletrica.unifilar").conexoes["categorias"]
