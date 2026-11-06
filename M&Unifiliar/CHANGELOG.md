# Histórico

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
