# Exemplos reais de integração

Os arquivos em `exemplos/ia/` usam o mesmo JSON v4 aberto pelo editor. Os quatro exemplos válidos passam pelos testes automatizados; o quinto deve ser recusado.

| Arquivo | Conteúdo |
| --- | --- |
| [generico.json](../exemplos/ia/generico.json) | Retângulo, texto, dois nós e ligação genérica |
| [unifilar.json](../exemplos/ia/unifilar.json) | Disjuntor DIN 1P e luminária LED ligados pela categoria Circuito |
| [multifilar.json](../exemplos/ia/multifilar.json) | Disjuntor DIN 2P e LED com ligações L1 e L2 em portas individuais |
| [modificado.json](../exemplos/ia/modificado.json) | Documento genérico preservado, com texto, tamanho e cor alterados |
| [rejeitado-terminal.json](../exemplos/ia/rejeitado-terminal.json) | Referência incorreta ao terminal 9 de uma luminária com uma única porta |

Os exemplos elétricos demonstram representação gráfica e referências de portas, sem dimensionamento ou aprovação técnica da instalação.

## Pedidos possíveis

Para começar sem bibliotecas:

> Crie um retângulo, um título e uma conexão entre dois nós usando o documento vazio do contexto. Entregue somente o JSON v4 completo.

Para desenhar um circuito:

> Use a biblioteca elétrica fornecida no contexto. Represente os elementos legíveis da fotografia, mantendo as portas corretas. Aponte separadamente informações ilegíveis antes de gerar o documento; não invente dimensionamentos.

Para modificar um projeto:

> No projeto atual, altere apenas o texto da forma texto para Fluxo revisado, tamanho 24 e cor #008370. Preserve os demais objetos e IDs. Retorne o documento inteiro.

Importe `rejeitado-terminal.json` para ver a rejeição com a indicação `$.folhas.Folha 1.ligacoes.c1.b`. O projeto aberto deve permanecer intacto.

## Validação independente da interface

Execute na pasta do aplicativo:

```powershell
python validar_projeto.py exemplos/ia/generico.json
python validar_projeto.py exemplos/ia/unifilar.json
python validar_projeto.py exemplos/ia/multifilar.json
python validar_projeto.py exemplos/ia/modificado.json
```

O comando abaixo deve terminar com código de saída 1 e explicar a porta incorreta:

```powershell
python validar_projeto.py exemplos/ia/rejeitado-terminal.json
```

O importador aceita JSON puro ou uma resposta com um único bloco Markdown JSON. Ele não procura automaticamente arquivos citados na resposta, não instala bibliotecas e não executa conteúdo.
