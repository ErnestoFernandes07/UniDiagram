# Arquitetura

## Separação implementada

O aplicativo é um único processo desktop. A separação é entre a fundação de software e pacotes de domínio declarativos; não há servidor nem serviços separados.

| Camada | Arquivos | Responsabilidade |
| --- | --- | --- |
| Composição | `app.py`, `configuracao.py` | Inicialização, coordenação de gestos, pacotes iniciais |
| Contrato | `nucleo/pacotes.py` | Descoberta, validação e registro de manifestos API 1 |
| Documento | `nucleo/documento.py` | Esquema versão 4, referências, carregamento e gravação atômica |
| Símbolos | `nucleo/simbolos.py`, `nucleo/geometria.py` | Primitivas vetoriais, transformação, nomes e terminais |
| Interface | `interface.py`, `paineis.py`, `propriedades.py` | Barras, categorias, inspeção, atalhos |
| Interação | `insercao.py`, `formas.py`, `texto.py`, `selecao.py` | Prévia, snap, formas, edição e seleção |
| Conexões | `ligacoes.py`, `tracado.py`, `rotulos.py` | Ligações entre portas/nós, curvas, derivações e etiquetas |
| Navegação/exportação | `navegacao.py`, `imagem.py` | Canvas, zoom, minimapa, waypoints e PNG |
| Domínio | `pacotes/*/pacote.json` | Símbolos, portas, categorias, cores e políticas de conexão |
| Compatibilidade | `pacotes/legado.py`, `pacotes/terminais_legados.json` | Importação elétrica v1/v2 e ajuste da geometria antiga |
| Validação | `nucleo/validacao.py` | Erros com caminho, tipos, limites, IDs e referências v4 |
| Integração por texto | `nucleo/ia.py`, `integracao_ia.py` | Contexto gerado dos manifestos, revisão de importação e recuperação |

`projeto.py` e `simbolos.py` mantêm imports antigos funcionando. Novos recursos devem usar os módulos de `nucleo`. Os módulos da interface ainda estão na raiz da aplicação e compõem a fundação; não são extensões elétricas.

## Fluxo de dependências

1. O registro descobre `pacotes/*/pacote.json` ao iniciar.
2. `configuracao.PACOTES_PADRAO` está vazio. O novo documento contém uma folha genérica e nenhuma biblioteca habilitada. `--pacote` pode habilitar bibliotecas explicitamente, sem criar folhas.
3. Cada componente e ligação registra ID e versão de seu pacote. A lista `bibliotecas` do documento controla apenas os catálogos habilitados na interface. O campo de pacote na folha existe apenas como fallback legado.
4. O menu consulta o pacote em hover; a inserção usa o pacote escolhido; o desenho e as conexões resolvem o pacote de cada objeto. Esses contextos são separados para impedir que um hover troque a geometria de objetos. `cores_bibliotecas` separa as cores compartilhadas por biblioteca e categoria em cada folha.
5. O renderer usa as mesmas primitivas no canvas e na exportação PNG.

A API 1 não importa Python nem executa scripts do pacote. Um pacote inválido gera erro de contrato; IDs e nomes de pacotes duplicados são recusados. A descoberta ocorre na inicialização, sem recarga ao vivo.

## Malha lógica e fundo

Uma unidade de encaixe equivale a 10 unidades do documento, independentemente do zoom. O fundo pode mostrar espaçamentos de 10, 20 ou 40; em zoom distante, o desenho do fundo reduz a densidade para evitar excesso de elementos. Isso nunca modifica a malha lógica nem o projeto.

A prévia usa o terminal `apoio` como origem da inserção. Rotação e espelhamento são aplicados antes de calcular a translação necessária para mantê-lo sob o cursor. Se Shift estiver pressionado, o apoio vai ao múltiplo de 10 mais próximo. Como todos os terminais locais têm coordenadas múltiplas de 10 e as rotações são de 90°, os demais terminais também ficam na malha. Sem Shift, a inserção é livre.

As guias verdes de alinhamento durante a edição de conexões têm outra finalidade e continuam independentes. A regra nova de Shift se aplica à inserção; não é um sistema geral de restrições paramétricas.

## Limites atuais

- Um pacote oferece componentes e políticas de conexão dentro das ferramentas existentes. Não pode adicionar ferramentas executáveis nem painéis arbitrários.
- Um documento depende dos pacotes instalados. O JSON registra ID/versão e não embute os manifestos.
- Uma folha aceita várias bibliotecas. Não há conversão automática entre pacotes. Uma conexão entre bibliotecas mantém a política do objeto de origem; isso não verifica compatibilidade elétrica.
- Categorias e conexões são limitadas pelo contrato para caberem na interface. Novos comportamentos de domínio podem exigir evolução da API e do núcleo.
- A ativação de bibliotecas é por documento. Desabilitar não descarrega dependências de objetos já existentes. O modelo genérico interno `nucleo.generico` não é uma biblioteca de componentes nem aparece nas caixas de seleção.
- A migração v3→v4 atribui a biblioteca da folha aos objetos existentes e preserva suas folhas e câmeras.

## Operações locais para integração por JSON

`validar_dados(dict)` devolve uma cópia validada e migrada sem modificar o argumento. `carregar_texto(str)` e `carregar(path)` usam a mesma validação. A leitura rejeita chaves duplicadas, valores não finitos e documentos acima de 10 MiB. Os limites publicados estão em `nucleo.validacao.LIMITES`.

`nucleo.ia` expõe `preparar_importacao`, `gerar_contexto`, `resumo_projeto`, `bibliotecas_relevantes` e `descrever_biblioteca`. Essas funções não dependem de Tk, não acessam rede e não aplicam alterações à sessão. A documentação estrutural das bibliotecas vem dos manifestos, enquanto o contrato geral é lido dos Markdown mantidos junto ao aplicativo.

`integracao_ia.py` adapta essas funções ao menu e à área de transferência. A revisão mantém o documento candidato separado do editor; editar o texto invalida a revisão. A aplicação valida novamente. A substituição salva uma cópia antes de alterar a sessão; a abertura em outra janela preserva o editor de origem. A janela importada é marcada como não salva.

Quando a janela principal é fechada com outros editores abertos, ela permanece oculta apenas para sustentar a sessão Tk até o último editor fechar. Cada editor verifica suas próprias alterações não salvas. Fechar uma janela não deve descartar silenciosamente outra.

Esta entrega não adiciona MCP, servidor, porta de rede ou camada genérica de comandos de edição. A troca completa de documentos atende ao fluxo atual sem duplicar operações gráficas. Exportação PNG continua na camada de renderização do editor.
