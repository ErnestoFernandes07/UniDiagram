# Forks, IA e manutenção

Leia primeiro o AGENTS.md na raiz do repositório. Ele orienta tanto agentes de IA quanto colaboradores humanos.

## Escolher o nível da alteração

Para um novo catálogo, crie um pacote. Para uma interação útil a todos os domínios, altere a fundação. Para um comportamento que não cabe no contrato atual, proponha uma evolução explícita da API antes de adicionar exceções de domínio em `app.py`.

Em um fork, as bibliotecas inicialmente habilitadas ficam em `configuracao.py`. A distribuição padrão mantém essa lista vazia para abrir genérica. Habilitar uma biblioteca nunca deve criar uma folha ou converter os objetos existentes. O nome da distribuição e os textos de marca ainda ficam na interface; alterá-los não exige mudar o contrato dos pacotes. Os pacotes elétricos podem continuar incluídos ou ser substituídos pela composição do fork. Migrações de documentos antigos dependem das bibliotecas correspondentes.

## Rotina de uma alteração

1. Identifique os documentos afetados e os comportamentos existentes que precisam ser preservados.
2. Implemente a mudança na camada adequada. Não faça renumeração silenciosa de terminais.
3. Faça testes proporcionais ao risco, incluindo round-trip JSON e PNG quando afetados.
4. Execute a suíte com ambiente gráfico e confira visualmente mudanças de interface/símbolos.
5. Atualize documentação e CHANGELOG na mesma entrega. Se a API mudar, inclua versão, migração e exemplos atualizados.

## Matriz de atualização da documentação

| Mudança | Documentos a revisar |
| --- | --- |
| Gesto, atalho, painel | USO, README, janela Atalhos |
| Manifesto ou descoberta de pacotes | CRIAR_PACOTE, ARQUITETURA, exemplo e validador |
| Documento ou migração | FORMATO_JSON, testes de migração, README |
| Fronteira de módulos | ARQUITETURA, AGENTS.md |
| Componente ou porta | README do pacote, testes de terminais, migração se necessária |
| Qualquer funcionalidade entregue | CHANGELOG |

Essas instruções não são uma atualização automática da documentação. Elas estabelecem a obrigação de atualizar os arquivos junto com o código a cada entrega.

## Pedido sugerido para manutenção por IA

> Leia AGENTS.md e a documentação do aplicativo. Implemente [mudança] preservando os pacotes e os projetos existentes. Identifique se a alteração pertence à fundação ou ao pacote. Mantenha a malha lógica independente do fundo, valide referências e preserve undo/redo. Execute os testes pertinentes em ambiente gráfico, confira JSON e PNG se afetados e atualize os Markdown relacionados e o CHANGELOG na mesma entrega. Relate verificações reais e limitações.

## Antes de publicar um fork

Defina sua licença e autoria; esta refatoração não atribui licença ao projeto. Verifique permissões para bibliotecas e conteúdos distribuídos. Inclua instruções de instalação, requisitos, exemplos, changelog e os pacotes necessários aos documentos de demonstração. Não publique credenciais, arquivos pessoais ou capturas do ambiente de desenvolvimento.
