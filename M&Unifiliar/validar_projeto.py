"""Validador local do mesmo documento usado pela interface."""
import argparse
import json
from nucleo.documento import carregar
from nucleo.ia import resumo_projeto

parser = argparse.ArgumentParser(description="Validar um projeto JSON do M&Unifiliar")
parser.add_argument("arquivo")
args = parser.parse_args()
try:
    data = carregar(args.arquivo)
except (OSError,ValueError) as erro:
    parser.exit(1,str(erro)+"\n")
print(json.dumps(resumo_projeto(data),ensure_ascii=False,indent=2))
print("Estrutura válida. Isto não é uma aprovação elétrica.")
