"""Execute: python validar_pacote.py caminho/para/pacote.json"""
import argparse
from nucleo.pacotes import ler_pacote, ErroPacote

parser = argparse.ArgumentParser(description="Validar um pacote declarativo da API 1")
parser.add_argument("manifesto")
args = parser.parse_args()
try:
    pacote = ler_pacote(args.manifesto)
except ErroPacote as erro:
    parser.exit(1,str(erro)+"\n")
print(f"OK: {pacote.id} v{pacote.versao}, {len(pacote.componentes)} componentes, malha de 10 unidades.")
