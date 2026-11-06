# Documento de trabalho — versão 4

O projeto é JSON UTF-8. Sua versão é independente da API 1 dos manifestos de bibliotecas.

```json
{
  "versao": 4,
  "ativa": "Folha 1",
  "bibliotecas": [],
  "folhas": {
    "Folha 1": {"componentes": {}, "ligacoes": {}}
  },
  "grade": {"tipo": "pontos", "passo": 20}
}
```

## Bibliotecas e identidade dos objetos

`bibliotecas` é a lista de catálogos habilitados para novas inserções. Cada entrada é `{"id":"eletrica.unifilar","versao":1}`, por exemplo. O estado das caixas é salvo no documento, não em uma preferência global. Novo projeto começa com a lista vazia.

Cada componente e ligação criado pelo editor tem seu próprio campo `pacote`, com ID e versão. A identidade do componente é pacote + `tipo`; componentes de mesmo nome em bibliotecas diferentes não se confundem. É possível misturá-los na mesma folha. A conexão conserva a biblioteca do objeto em que o desenho da ligação começou. Se for uma ligação genérica, usa `nucleo.generico`, definição interna sem componentes.

Desabilitar uma biblioteca remove apenas sua entrada em `bibliotecas`. Os objetos mantêm seus pacotes e continuam sendo desenhados e exportados. Portanto, bibliotecas não marcadas ainda podem ser dependências necessárias do arquivo.

## Folhas, componentes e ligações

`ativa` identifica uma folha existente. A folha contém `componentes`, `ligacoes` e, opcionalmente, `formas`, `nos` e `cores_bibliotecas`. Novos projetos têm uma folha sem abas visíveis. As múltiplas folhas de documentos antigos são preservadas e continuam acessíveis por abas.

Componentes são indexados por IDs de instância. Campos usados são `pacote`, `tipo`, `nome`, `x`, `y`; também podem conter `rotacao` (0, 90, 180, 270), `espelho` e `mostrar_nome`. Posições podem ser fracionárias em inserção livre. Portas são resolvidas no pacote de cada objeto, independentemente da biblioteca aberta no menu.

Ligações contêm `pacote`, `a`, `b` e `condutor`. O nome histórico `condutor` representa a categoria da conexão, mesmo em pacotes não elétricos. Cada ponta é `[id_da_instancia, indice_da_porta]` ou `[id_do_no, 0]`. `pontos` contém as dobras intermediárias dos traçados manuais; as extremidades são calculadas pelas referências. Estilos opcionais incluem `cor`, `espessura`, `opacidade`, `tracejado` e `mostrar_nome`. `etiqueta` armazena a fração ao longo do caminho (0–1) e o afastamento perpendicular (-32–32).

`nos` mapeia IDs para `[x,y]`. Formas têm tipo, pontos, cor e estilo; texto também guarda conteúdo, fonte, tamanho e ângulo. `ancoras` associa alças a portas ou nós. As referências acompanham a movimentação.

`cores_bibliotecas` tem a estrutura `{id_da_biblioteca: {categoria: cor}}`. Uma alteração de L1 no Multifilar não altera uma ligação L1 do Unifilar na mesma folha. As opções editáveis de cor estão em `formas.CORES`; as cores iniciais vêm do manifesto.

## Navegação e fundo

- `grade.tipo`: `linhas`, `pontos` ou `nenhuma`.
- `grade.passo`: 10, 20 ou 40, somente para exibição; o encaixe permanece em 10.
- `vistas`: câmera por folha com `x`, `y`, `zoom`.
- `waypoints`: chaves `1`, `2`, `3`, com folha e câmera.
- `minimapa`: posição normalizada `[x,y]` dentro da área do editor.

## Migração

Versões 1 e 2 recebem a migração elétrica anterior, corrigindo referências de cargas unifilares quando necessário e ajustando rotas manuais e formas ancoradas aos terminais alinhados à malha. Os centros dos componentes não são deslocados automaticamente.

Na etapa v3→v4, a biblioteca de cada folha é atribuída aos seus componentes e ligações. As cores antes em `cores_condutores` são transferidas para o espaço da biblioteca em `cores_bibliotecas`. Folhas, nomes, câmeras e waypoints são preservados. As bibliotecas usadas ficam habilitadas na importação, para continuar o trabalho.

O campo `pacote` na folha permanece como fallback de compatibilidade nos projetos importados. Objetos sem referência própria nesses documentos usam esse fallback; objetos novos sempre recebem referência própria. Folhas novas não possuem pacote fixo.

A importação não sobrescreve o arquivo. Salvar grava a versão 4 de forma atômica. Versões antigas do aplicativo não abrem v4. Pacotes ausentes ou com versão incompatível geram erro específico; o arquivo não embute símbolos nem instala pacotes automaticamente. Alterar manualmente o pacote de um objeto não é uma conversão segura entre bibliotecas.

## Validação para arquivos externos

Abrir arquivo e importar texto usam a mesma validação estrutural. Mensagens incluem o caminho do objeto ou campo incorreto. Chaves duplicadas no JSON, IDs repetidos entre tipos na mesma folha, índices de porta inválidos, bibliotecas incompatíveis e campos não suportados são recusados.

Limites atuais: 10 MiB por JSON, 64 folhas, 20.000 objetos totais, 2.000 pontos por caminho, coordenadas finitas entre -10.000.000 e 10.000.000 e até 10.000 caracteres por texto. IDs têm até 128 caracteres, usando letras, números, `_`, `.` ou `-`. Nomes de componentes têm até 256 caracteres. Espessura vai de 0,5 a 32; opacidade é um inteiro de 0 a 100; tamanho do texto é inteiro de 1 a 512; ângulo de texto é inteiro de 0 a 359. Fontes e cores editáveis são as listas de `formas.py`, também incluídas no contexto para IA.

Esses limites protegem o carregamento e não mudam a versão 4. Um documento estruturalmente válido ainda pode ser grande e renderizar lentamente. Não há validação de engenharia nem execução de código contido no documento.

## Escala e identificação dos componentes

Campos opcionais compatíveis com v4: `escala` inteiro de 1 a 4 (padrão 1); `tamanho_nome` inteiro de 8 a 96 (padrão 12); `posicao_nome` como [dx,dy] em unidades de mundo relativas ao centro. O deslocamento da etiqueta não é rotacionado ou escalado. A transformação das portas aplica escala, espelhamento, rotação e translação. A interface altera a escala preservando o terminal de apoio. Escalas inteiras preservam a malha dos terminais já alinhados; componentes colocados livremente não são realinhados à força.

## Seta curva

Forma genérica `tipo: "Seta curva"`, com `pontos` contendo de 2 a 2000 pares de coordenadas, `cor` e os estilos opcionais comuns das formas. Os pontos descrevem a polilinha; o renderer arredonda os joelhos e desenha a ponta de seta. Não possui referências elétricas. Ramificações por Ctrl+clique são formas separadas. Documento permanece v4; versões anteriores do aplicativo que desconhecem esse tipo não conseguem abrir projetos que o utilizam. A ativação conjunta Diagrama elétrico salva os dois pacotes na lista `bibliotecas` já existente, sem campos novos no documento.

### Categorias de conexões legadas

A API 1 aceita `conexoes.categorias_ocultas`, uma lista opcional de categorias existentes que não são oferecidas para novas escolhas. O padrão não pode estar oculto. Leitores continuam aceitando objetos antigos dessas categorias. Nos dois pacotes elétricos, Circuito é legado; para novas conexões use L1/L2/L3/N/PE/Retorno conforme o desenho. Novos fios mostram o nome; a opção individual `mostrar_nome:false` continua válida. As duas bibliotecas agora compartilham cores por categoria, cada uma em seu escopo na folha. No unifilar, um traço pode representar um conjunto de condutores: um rótulo L1 não descreve sozinho sua composição completa. O editor não verifica a adequação elétrica das ligações.
