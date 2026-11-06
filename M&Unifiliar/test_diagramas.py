from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from formas import CORES
from apoio_testes import eletrico_v3
from projeto import CARGAS, GRUPOS, MOTOR_FF, carregar, novo, salvar, terminais


class DiagramasTest(unittest.TestCase):
    def test_terminais_de_toda_a_biblioteca(self):
        multi = {"Terra":1,"Quadro de distribuição":10,"Interruptor":2,"DPS":2,"DR 2P":4,"DR 4P":8,
                 "Tomada 2P+T":3,"Luminária LED":2,"Luminária LED com PE":3,"Carga resistiva":2,
                 "Carga resistiva com PE":3,"Motor monofásico":3,MOTOR_FF:3,"Motor trifásico":4}
        for grupo in GRUPOS.values():
            for tipo in grupo:
                with self.subTest(tipo=tipo):
                    self.assertEqual(len(terminais(tipo,"Unifilar")),1 if tipo in CARGAS or tipo=="Terra" else 2)
                    contagem = int(tipo[-2])*2 if tipo.startswith("Disjuntor") else multi[tipo]
                    self.assertEqual(len(set(terminais(tipo,"Multifilar"))),contagem)

    def test_migracao_preserva_fios_e_alcas_em_ambas_as_folhas(self):
        projeto = eletrico_v3()
        projeto["versao"] = 1
        for nome,folha in projeto["folhas"].items():
            folha["componentes"]["c"] = dict(x=120,y=100,tipo="Luminária LED",nome="Luz")
            folha["nos"] = {"n":[230,80]}
            folha["ligacoes"]["f"] = dict(a=["n",0],b=["c",1],condutor="L1",cor=CORES[2])
            folha["formas"] = {"s":dict(tipo="Linha",cor=CORES[1],pontos=[[120,124],[80,70]],ancoras={"0":["c",1]})}
        with TemporaryDirectory() as pasta:
            p = Path(pasta)/"antigo.json"
            salvar(p,projeto)
            novo_projeto = carregar(p)
            uni,multi = novo_projeto["folhas"].values()
            self.assertEqual(uni["ligacoes"]["f"]["b"],["c",0])
            self.assertEqual(uni["formas"]["s"]["pontos"][0],[120,70])
            self.assertEqual(multi["ligacoes"]["f"]["b"],["c",1])
            self.assertEqual(multi["cores_bibliotecas"]["eletrica.multifilar"]["L1"],CORES[2])
            salvar(p,novo_projeto)
            self.assertEqual(carregar(p),novo_projeto)
