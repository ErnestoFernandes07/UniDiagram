# Histórico

## 2026-11-06 — Escala e identificação de componentes

- Nome reposicionável após selecionar o componente, com tamanho no painel e padrão para as próximas inserções da sessão.
- Escalas inteiras 1×–4×, com preservação do apoio, atualização de conexões e âncoras.
- Shift alinha trechos/vértices de fios e elimina dobras colineares; não remove junções reais.
- Campos opcionais documentados e validados no JSON v4, usados também em PNG e contexto para IA.


## 2026-11-06 — Snap das formas e bibliotecas laterais

- Shift aplica encaixe na malha de 10 ao criar, mover e redimensionar formas e linhas.
- Barra de bibliotecas vertical, arrastável pelo título, com catálogos posicionados conforme o espaço disponível. Posição mantida na sessão.


## 2026-11-05 — 0.5.0, integração universal por JSON/Markdown

- Copiar contexto para IA pelo menu Arquivo, incluindo projeto atual ou somente instruções e bibliotecas para um projeto novo.
- Contexto estrutural gerado dos manifestos relevantes; metadados opcionais `ia` para bibliotecas de terceiros, tratados como dados não confiáveis.
- Importação de texto, arquivo ou único bloco Markdown JSON, com validação, resumo e aplicação explícita.
- Nova janela com estado não salvo, ou substituição com backup `.recuperacao` e undo. Falha no backup interrompe a substituição.
- Validador compartilhado por abertura/importação, com caminhos de erro, limites, referências e rejeição de chaves/IDs duplicados.
- Exemplos reais genérico, unifilar, multifilar, modificação e rejeição; validador de projetos por linha de comando.
- Documentação de IA, contrato e instruções de manutenção atualizados. Sem MCP, rede, modelo integrado ou API paga; JSON permanece v4 e manifestos API 1.

## 2026-11-05 — Abertura genérica e bibliotecas opcionais, documento v4

- Novo projeto com uma folha genérica, sem abas elétricas e sem bibliotecas habilitadas.
- Caixas de seleção em Bibliotecas + para habilitar catálogos por documento, com undo/redo e persistência JSON.
- Barra flutuante por biblioteca, com catálogo por hover e categorias internas.
- Componentes de várias bibliotecas na mesma folha, identificados por pacote e tipo.
- Conexões guardam a biblioteca de origem; cores compartilhadas são isoladas por biblioteca e categoria.
- Desmarcar preserva componentes, fios, geometria e exportação.
- Migração v3→v4 preservando folhas antigas e atribuindo pacotes aos objetos. A API dos manifestos continua na versão 1.
- Documentação e testes atualizados para a inicialização genérica, hover, persistência e bibliotecas mistas.

## 2026-11-05 — Fundação e pacotes, documento v3 / API de pacotes v1

- Separação do modelo, contrato de pacotes, geometria e renderer genérico em `nucleo/`.
- Pacotes elétricos Unifilar e Multifilar em JSON, distribuídos com o aplicativo.
- Descoberta de pacotes locais, seleção em Arquivo → Novo com pacote e opção `--pacote`.
- Categorias, terminais, símbolos e política de cores resolvidos pelo pacote ativo.
- Exemplo de fluxograma e validador de manifestos para autores e IAs.
- Prévia de inserção apoiada em um terminal, com rotação, espelhamento e Shift para encaixe.
- Malha lógica fixa de 10, independente do espaçamento visual. Terminais dos pacotes elétricos atualizados para essa regra.
- Importação de documentos v1/v2, com atualização de referências, rotas manuais e formas vinculadas aos novos terminais.
- Documentação de arquitetura, uso, JSON, pacotes e forks, além de instruções AGENTS.md para manter os arquivos atualizados.

Limites: não há conversão entre pacotes, instalação online, scripts de extensão nem realinhamento automático de todos os componentes antigos. O documento referencia pacotes instalados por ID e versão.

## Estado anterior à separação

Editor elétrico em Python/Tkinter com formas, texto na folha, conexões editáveis, derivações, cores compartilhadas no multifilar, etiquetas arrastáveis, seleção múltipla, grade configurável, minimapa, waypoints, JSON v2 e PNG. A nova fundação preserva essas funções.

## 2026-11-06 — Ferramentas genéricas e bibliotecas de domínio

- Diagrama elétrico habilita Unifilar/Multifilar em conjunto; Fio/Ligar e Derivar ficam na lateral, disponíveis apenas com bibliotecas habilitadas.
- Barra principal genérica com Seta curva, prévia, dobras e alças. Ctrl+clique em linhas inicia ramificação visual independente; Esc cancela.
- Metadado opcional biblioteca na API 1 e tipo Seta curva no documento v4. Projetos sem esse tipo seguem compatíveis; leitores antigos não reconhecem a nova forma.

### Fios e vínculo de terminais (2026-11-06)

Os botões laterais de ligar e derivar usam ícones, sem seta de dropdown; o nome e atalho aparecem ao passar o mouse. Os novos fios elétricos usam L1 inicialmente e mostram o nome por padrão. Arrastar uma ponta livre até 10 pixels de um terminal conecta de fato ao componente: todas as ligações e formas ancoradas naquele nó passam a referenciar a porta. Mover o componente passa a levar os fios junto. Desfazer restaura a ponta livre.

Unifilar e Multifilar compartilham cores por categoria dentro de cada biblioteca e folha. Alterar L1 atualiza todos os L1 daquele catálogo, incluindo novas ligações. Bibliotecas diferentes permanecem independentes. Cores locais antigas não prevalecem sobre essa política compartilhada. “Circuito” fica oculto para novas escolhas, mas continua reconhecido em arquivos antigos para evitar renomear silenciosamente o conteúdo.

## Fluidez do canvas — 2026-11-06

O canvas e o minimapa reutilizam as primitivas já desenhadas. Arrastar um componente atualiza o componente e seus fios, sem reconstruir os objetos que não mudaram. Eventos de movimento pendentes são agrupados e apenas a posição mais recente é processada; soltar o botão aplica o último movimento antes de encerrar o gesto. Isso evita reproduzir um trajeto atrasado do cursor. Zoom, seleção e exportação continuam disponíveis.

A otimização não desativa vínculos: fios conectados continuam acompanhando componentes, inclusive sem Shift. Shift mantém seu papel de encaixe e alinhamento assistido. Não foi necessário mudar a biblioteca gráfica. Projetos com muita transparência ainda exigem composição raster e podem custar mais.

Para medir com o quadro de exemplo, execute `python -B medir_desempenho.py`. O script abre uma janela temporária e mede redesenho, pan e arraste circular; não salva alterações no projeto. As medições dependem do computador e do desenho.
