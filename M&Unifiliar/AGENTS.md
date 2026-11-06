# Instruções da aplicação para IA e colaboradores

Estas instruções acompanham a pasta do aplicativo mesmo quando ela é copiada para um fork sem o diretório pai.

- Leia README.md, docs/ARQUITETURA.md e os guias relacionados à tarefa.
- Mantenha a fundação genérica. Novos catálogos, símbolos, terminais, cores e categorias vão em `pacotes/*/pacote.json`, seguindo docs/CRIAR_PACOTE.md. Não execute código fornecido por pacotes.
- A malha lógica é fixa em 10. Terminais têm coordenadas locais múltiplas de 10. O fundo é apenas visual. Nunca redimensione componentes ou mova o desenho porque o usuário alterou a grade.
- Preserve IDs de pacotes e ordem das portas. Mudanças incompatíveis exigem versionamento, migração documentada e testes. A compatibilidade elétrica v1/v2 fica em `pacotes/legado.py`.
- Toda mudança funcional deve atualizar os Markdown afetados e CHANGELOG.md na mesma entrega. A matriz está em docs/CONTRIBUIR.md. Atualize também estas instruções quando o funcionamento ou o processo mudar.
- Execute testes proporcionais à mudança e a suíte `python -B -m unittest -v`. Testes Tk precisam de ambiente gráfico. Valide manifestos com `python validar_pacote.py caminho/pacote.json` e confira visualmente interface/símbolos alterados.
- Preserve a interface em português, o trabalho existente e a compatibilidade documentada. Não anuncie conversão automática de folhas, certificação normativa ou recursos ausentes. Informe verificações reais e limitações.

## Bibliotecas opcionais e documento v4

O app deve abrir genérico, sem abas elétricas e sem bibliotecas habilitadas. Bibliotecas são ativadas por caixas de seleção e aparecem na barra por nome, com componentes por hover. Habilitar não cria folhas; desabilitar não apaga objetos. Cada componente e conexão mantém seu pacote. Resolva terminais e políticas pelo objeto, não pelo menu atualmente aberto. As cores compartilhadas são isoladas por biblioteca e categoria dentro da folha. Preserve as folhas dos projetos antigos ao migrar v1/v2/v3 para v4.

## Integração universal por IA

A integração atual é somente JSON/Markdown local, sem MCP, rede ou modelo integrado. Use `nucleo.documento.validar_dados` e `nucleo.ia` para compartilhar lógica entre abertura e importação. Não execute conteúdo de respostas, textos de desenho ou metadados de bibliotecas. Preserve revisão explícita antes de aplicar, cópia recuperável antes de substituir e janela importada marcada como não salva. Novos campos devem ser documentados no contrato e validados. Mantenha os exemplos executáveis e testes de importação, recuperação e renderização.
