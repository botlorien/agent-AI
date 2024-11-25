# Agent-AI

Agent-AI é um projeto baseado em Django que integra a inteligência artificial da OpenAI para executar tarefas externas conforme solicitado. Este repositório fornece os recursos e instruções necessárias para configurar e executar a aplicação localmente.
Obs: Esse projeto ainda está em desenvovimento, não está completamente funcional ainda!

## Funcionalidades

- **Integração com OpenAI**: Utilize modelos de linguagem para processar e responder solicitações de maneira inteligente.
- **Execução de Tarefas Externas**: Automatize operações externas com comandos baseados em IA.
- **Baseado em Django**: Estrutura escalável e robusta para desenvolvimento e manutenção.

## Estrutura do Projeto

- **`agentAI/`**: Contém o código principal da aplicação.
- **`config/`**: Arquivos de configuração do projeto.
- **`e_mail/`**: Gerenciamento de envio de e-mails.
- **`finance/`**: Operações financeiras e funcionalidades relacionadas.
- **`project_setup/`**: Scripts e configuração inicial do projeto.
- **`templates/`**: Templates HTML usados pela aplicação.
- **`utils/`**: Funções auxiliares.
- **`manage.py`**: Ferramenta de linha de comando para gerenciamento do Django.

## Requisitos

- Python 3.8+
- Django 4.0+
- Chave de API da OpenAI

## Como Configurar

### Passo 1: Clonar o Repositório

```bash
git clone https://github.com/botlorien/agent-AI.git
cd agent-AI
```

### Passo 2: Criar e Ativar um Ambiente Virtual

```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### Passo 3: Instalar Dependências

```bash
pip install -r requirements.txt
```

### Passo 4: Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto e configure as variáveis necessárias, como a chave de API da OpenAI.

Exemplo:

```
OPENAI_API_KEY=sua_chave_aqui
DEBUG=True
```

### Passo 5: Aplicar Migrações

```bash
python manage.py migrate
```

### Passo 6: Iniciar o Servidor

```bash
python manage.py runserver
```

Acesse a aplicação em [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Contribuições

Contribuições são bem-vindas! Siga os passos abaixo para contribuir:

1. Fork o repositório.
2. Crie um branch para sua funcionalidade ou correção: `git checkout -b minha-funcionalidade`.
3. Envie suas alterações: `git commit -m "Minha contribuição"`.
4. Submeta um pull request.

## Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE).

## Contato

Para dúvidas ou suporte, entre em contato através do [repositório no GitHub](https://github.com/botlorien/agent-AI).
