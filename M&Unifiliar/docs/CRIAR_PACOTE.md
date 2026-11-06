# Criar um pacote — API 1

Use `exemplos/fluxograma/pacote.json` como modelo executável. Não é necessário editar Python para adicionar componentes. Os dois pacotes elétricos incluídos seguem o mesmo contrato.

## Instalar e experimentar

1. Copie a pasta `exemplos/fluxograma` para `pacotes/meu_pacote`.
2. Edite `pacote.json`. Escolha `id` e `nome` únicos entre os pacotes instalados.
3. Execute `python validar_pacote.py pacotes/meu_pacote/pacote.json`.
4. Reinicie o aplicativo e marque a nova biblioteca em **Bibliotecas +**.
5. Teste inserção livre, Shift, R, E, ligações em todas as portas, JSON e PNG.

Para abrir diretamente, use `python app.py --pacote exemplo.fluxograma`. A opção pode ser repetida para habilitar várias bibliotecas na mesma folha genérica. Isso exige instalar a pasta antes. O catálogo de exemplo permanece fora da descoberta automática enquanto estiver em `exemplos/`.

## Campos do manifesto

| Campo | Significado |
| --- | --- |
| `api` | Inteiro `1`, versão do contrato |
| `id` | Identificador estável, como `empresa.hidraulica`; letras minúsculas, números, `_`, `-`, `.` |
| `versao` | Inteiro positivo da versão do pacote |
| `nome` | Nome único exibido na interface, até 48 caracteres |
| `unidade` | Obrigatoriamente `10` na API 1 |
| `categorias` | Objeto com 1 a 8 categorias e listas de chaves dos componentes |
| `componentes` | Objeto com até 500 definições de componentes |
| `conexoes` | Categorias, cores, padrão e política de ligações |

Cada componente tem `terminais`, `apoio` (índice, padrão 0), `simbolo` (lista de primitivas) e, opcionalmente, `margem_nome` (padrão 13). A chave do componente aparece na biblioteca e é salva em `tipo`; portanto renomeá-la quebra referências existentes. Um componente pode ficar fora das categorias para continuar abrindo arquivos sem oferecê-lo em novas inserções, como o barramento legado.

## Regra obrigatória dos terminais

**Todas as coordenadas locais dos terminais devem ser múltiplas de 10.** Use, por exemplo, `[[0,-30],[0,30]]` ou `[[-10,-30],[10,-30],[40,0]]`. Terminais em `[0,-24]` ou `[7,0]` são recusados. Há de 1 a 64 portas, sem posições repetidas. O apoio precisa apontar para uma delas.

Planeje o corpo em torno dessas portas. Curvas e detalhes gráficos internos podem ter coordenadas intermediárias; a restrição da malha vale para os terminais. Mantenha a ordem das portas estável, pois os fios salvam o índice da porta. Não reordene portas para fins cosméticos.

O espaçamento escolhido no botão Fundo é visual. Não use esse valor para dimensionar componentes, recalcular portas ou mover objetos. O encaixe é sempre na malha lógica de 10, e a prévia exibe os pontos intermediários quando Shift está pressionado. Rotações de componentes são múltiplos de 90° e preservam a malha.

## Símbolos vetoriais

Cada primitiva tem `tipo` e `pontos`, uma lista plana de coordenadas locais. Tipos aceitos:

- `line`: dois ou mais pontos.
- `polygon`: contorno fechado.
- `rectangle` e `oval`: duas extremidades da caixa delimitadora.
- `text`: uma posição e o campo `text`.

Campos visuais: `fill`, `outline`, `width`, conforme a primitiva. Cores usam `#RRGGBB`; também se aceita `white` e `""` para ausência de preenchimento. A tinta `#203b46` é substituída pelo destaque ao selecionar. Texto pode ter `font`, por exemplo `["Segoe UI",-12,"bold"]`; tamanho negativo corresponde a pixels do desenho. Não coloque `width` ou `outline` em texto, nem `outline` em linhas. Use somente os campos pertinentes ao tipo.

O núcleo desenha automaticamente o nome e os círculos dos terminais, com tags para seleção e conexões. Não duplique essas partes no símbolo. O pacote não pode fornecer código, callbacks, caminhos de scripts ou recursos remotos.

## Conexões

```json
{
  "categorias": {"Fluxo": "#34445a", "Sim": "#15805b", "Não": "#a03b52"},
  "padrao": "Fluxo",
  "cores_compartilhadas": false,
  "nomes_ocultos": ["Fluxo"],
  "rotulo": "Conexão"
}
```

Há de 1 a 12 categorias. `padrao` deve existir. Se `cores_compartilhadas` for verdadeiro, alterar a cor de uma conexão altera todas as da mesma categoria e biblioteca nessa folha. `nomes_ocultos` controla apenas a visibilidade inicial das etiquetas; o usuário pode mudá-la em cada conexão.

A chave de um componente pode existir em outro pacote: a identidade é o par ID do pacote + chave do componente. Não dependa de uma biblioteca global ativa para resolver portas ou estilos. O catálogo aparece ao passar o mouse sobre o nome da biblioteca, e suas categorias ficam dentro do menu.

## Compatibilidade e publicação

O documento exige a versão exata do pacote referenciado. O aplicativo informa dependência ausente ou incompatível ao abrir. Distribua os manifestos junto com exemplos de projetos. Mudanças que alterem portas ou chaves precisam de plano de migração e testes antes de aumentar a versão. Não existe migração universal de pacotes na API 1.

Inclua um README no pacote com finalidade, significado das portas, exemplos de conexão, versão, autor/licença escolhidos por você e limitações. Registre mudanças no histórico. Não afirme certificação normativa sem fundamentação.

## Pedido sugerido para uma IA

> Leia AGENTS.md, docs/ARQUITETURA.md, docs/CRIAR_PACOTE.md e exemplos/fluxograma/pacote.json. Crie um pacote API 1 para [finalidade], com [componentes]. Use ID [id]. Todos os terminais devem ser múltiplos de 10 e o terminal de apoio deve favorecer a inserção. Preserve a ordem das portas de componentes existentes. Não introduza código executável no pacote nem regras de domínio no editor. Valide o manifesto, teste inserção, rotação, conexões, JSON e PNG e atualize README e histórico. Explique limitações reais.

## Informações padronizadas para assistentes externos

Copiar contexto para IA gera automaticamente ID, versão, categorias, definições dos símbolos, índices e coordenadas de terminais e políticas de conexões a partir do manifesto. Não mantenha uma segunda lista manual dessas estruturas.

O manifesto API 1 pode incluir o campo opcional `ia`, compatível com os pacotes existentes:

```json
{
  "ia": {
    "descricao": "Finalidade desta biblioteca.",
    "restricoes": ["Limites de uso que o autor deseja explicar."],
    "exemplos": ["Descrição de um uso típico; exemplos completos podem acompanhar a distribuição."]
  }
}
```

`descricao` tem até 4.000 caracteres. `restricoes` e `exemplos` são listas de até 20 textos, cada um com até 2.000 caracteres. O validador verifica esses campos. São notas de domínio, não permissões para executar código, ler arquivos ou alterar o computador.

O contexto identifica as notas como dados não confiáveis. Não há leitura automática de scripts, arquivos privados, URLs ou outros arquivos referenciados pelo manifesto. Para o projeto atual, entram bibliotecas habilitadas e dependências dos objetos existentes; para um projeto novo, apenas as habilitadas, além das definições genéricas internas.
