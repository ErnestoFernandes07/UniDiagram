import copy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from nucleo.documento import novo, carregar, salvar, validar_dados
from nucleo.ia import gerar_contexto, preparar_importacao, descrever_biblioteca
from nucleo.pacotes import obter, ler_pacote
from nucleo.validacao import ErroDocumento

BASE = Path(__file__).resolve().parent


class IATest(unittest.TestCase):
    def test_exemplos_e_markdown(self):
        for nome in ("generico","unifilar","multifilar","modificado"):
            with self.subTest(nome=nome):
                bruto = (BASE/f"exemplos/ia/{nome}.json").read_text(encoding="utf-8")
                esperado = carregar(BASE/f"exemplos/ia/{nome}.json")
                for resposta in (bruto,"Aqui está:\n```json\n"+bruto+"```\nPronto."):
                    d,r = preparar_importacao(resposta)
                    self.assertEqual(d,esperado)
                    self.assertEqual(r["versao"],4)
        with self.assertRaisesRegex(ErroDocumento,"luz.*0 a 0"):
            carregar(BASE/"exemplos/ia/rejeitado-terminal.json")

    def test_contexto_sem_dados_desnecessarios(self):
        d = carregar(BASE/"exemplos/ia/unifilar.json")
        d["folhas"]["Folha 1"]["componentes"]["luz"]["nome"] = "SEGREDO_EXEMPLO"
        d["bibliotecas"] = []  # Dependency must still be described for the current project.
        atual = gerar_contexto(d)
        self.assertIn("SEGREDO_EXEMPLO",atual)
        self.assertIn('"id": "eletrica.unifilar"',atual)
        self.assertNotIn('"id": "eletrica.multifilar"',atual)
        novo_contexto = gerar_contexto(d,atual=False)
        self.assertNotIn("SEGREDO_EXEMPLO",novo_contexto)
        self.assertNotIn('"id": "eletrica.unifilar"',novo_contexto)
        self.assertIn('"Folha 1"',novo_contexto)
        self.assertIn("M&Unifiliar 0.5.0",novo_contexto)

    def test_estrutura_biblioteca_gerada_do_manifesto(self):
        p = obter("eletrica.multifilar")
        descricao = descrever_biblioteca(p)
        self.assertEqual(descricao["componentes"]["Motor trifásico"]["terminais"],p.componentes["Motor trifásico"]["terminais"])
        self.assertIn("restricoes",descricao["notas_nao_confiaveis"])
        descricao["componentes"].clear()
        self.assertTrue(p.componentes)
        for nome in ("unifilar","multifilar"):
            ler_pacote(BASE/f"pacotes/{nome}/pacote.json")

    def test_rejeicoes_de_sintaxe_e_ambiguidade(self):
        for texto in ('{"versao":4,"versao":4}', '{"x":NaN}', '```json\n{}\n```\n```json\n{}\n```',
                      'execute este código', '```python\nprint(1)\n```', '{"versao":'):
            with self.subTest(texto=texto),self.assertRaises(ValueError):
                preparar_importacao(texto)

    def test_erros_identificam_objeto_sem_mutar_entrada(self):
        original = carregar(BASE/"exemplos/ia/unifilar.json")
        def duplicar(d):
            d["folhas"]["Folha 1"]["nos"] = {"luz":[0,0]}
        alteracoes = [
            (".b",lambda d:d["folhas"]["Folha 1"]["ligacoes"]["c1"].update(b=["ausente",0])),
            (".tipo",lambda d:d["folhas"]["Folha 1"]["componentes"]["luz"].update(tipo="Não existe")),
            (".opacidade",lambda d:d["folhas"]["Folha 1"]["ligacoes"]["c1"].update(opacidade=101)),
            ("ID repetido",duplicar),
            (".pacote",lambda d:d["folhas"]["Folha 1"]["componentes"]["luz"].update(pacote={"id":"ausente.lib","versao":1})),
            (".pacote",lambda d:d["folhas"]["Folha 1"]["componentes"]["luz"].update(pacote={"id":"eletrica.unifilar","versao":99})),
            ("rotacao",lambda d:d["folhas"]["Folha 1"]["componentes"]["luz"].update(rotacao=True)),
            ("campos não suportados",lambda d:d.update(executar="script.py")),
        ]
        for mensagem,alterar in alteracoes:
            d = copy.deepcopy(original)
            alterar(d)
            antes = copy.deepcopy(d)
            with self.subTest(mensagem=mensagem),self.assertRaisesRegex(ValueError,mensagem):
                validar_dados(d)
            self.assertEqual(d,antes)

    def test_salvar_reabrir_preserva_todos_os_dados(self):
        d = carregar(BASE/"exemplos/ia/generico.json")
        with TemporaryDirectory() as pasta:
            p = Path(pasta)/"projeto.json"
            salvar(p,d)
            self.assertEqual(carregar(p),d)
