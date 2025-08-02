# Questionnaire Manager

## Descrição

O Questionnaire Manager é uma aplicação web desenvolvida em Python utilizando o framework Flask. Ele foi projetado para facilitar o preenchimento de questionários e o gerenciamento de respostas, oferecendo uma experiência intuitiva e eficiente para usuários e administradores. A aplicação inclui funcionalidades avançadas como autenticação de usuários, gerenciamento de perguntas, importação de questionários em lote, visualização de resultados e um painel administrativo completo. Além disso, a interface foi construída com Bootstrap para garantir um design moderno e responsivo.

## Estrutura do Projeto

A estrutura do projeto é organizada da seguinte forma:

```
questionnaire-manager/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes.py
│   ├── main/
│   │   ├── __init__.py
│   │   ├── routes.py
│   ├── static/
│   │   ├── style.css
│   ├── templates/
│       ├── admin.html
│       ├── index.html
│       ├── login.html
│       ├── register.html
│       ├── submitted.html
├── config.py
├── requirements.txt
├── run.py
```

- **app/**: Contém o código principal da aplicação.
  - **auth/**: Gerencia autenticação e rotas relacionadas.
  - **main/**: Contém as rotas principais da aplicação.
  - **static/**: Arquivos estáticos como CSS.
  - **templates/**: Templates HTML para renderização.
- **config.py**: Configurações da aplicação.
- **requirements.txt**: Dependências do projeto.
- **run.py**: Arquivo principal para executar a aplicação.

## Funcionalidades

- Autenticação de usuários.
- Preenchimento e envio de questionários.
- Interface amigável com Bootstrap.
- Painel administrativo para gerenciar perguntas e visualizar resultados.
- Importação de perguntas em lote.
- Alteração de senha para administradores.

## Requisitos

Certifique-se de ter o Python instalado. As dependências podem ser instaladas usando o seguinte comando:

```bash
pip install -r requirements.txt
```

## Executando o Projeto

1. Clone o repositório:

```bash
git clone <URL_DO_REPOSITORIO>
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Execute a aplicação:

```bash
python run.py
```

4. Acesse a aplicação no navegador em `http://127.0.0.1:5000`.

## Exemplos de Uso

### Cadastro de Administrador

Acesse a rota `/auth/register` para cadastrar o primeiro administrador.

### Responder Questionário

Acesse a página inicial e preencha o questionário com as perguntas cadastradas.

### Gerenciar Perguntas

No painel administrativo, você pode adicionar, editar ou excluir perguntas e opções.

### Visualizar Resultados

Os resultados dos questionários respondidos podem ser visualizados no painel administrativo.

### Importar Questionários em Lote

Para importar perguntas em lote, acesse o painel administrativo e utilize a funcionalidade de importação. O formato esperado para o arquivo de texto é:

```
pergunta: "Você gosta de maçã?"
opcoes e peso: "sim:1","não:0","talvez:0.5"
pergunta: "Você gosta de uva?"
opcoes e peso: "sim:1","não:0","talvez:0.5"
```

#### Exemplo Completo

Copie e cole o seguinte conteúdo no campo de importação ou utilize o arquivo de exemplo disponível em `exemplo-perguntas-em-lote.txt`.

```
pergunta: "Qual sua fruta favorita?"
opcoes e peso: "maçã:1","banana:0.5","laranja:0.8"
pergunta: "Você gosta de esportes?"
opcoes e peso: "sim:1","não:0","às vezes:0.5"
pergunta: "Qual sua cor favorita?"
opcoes e peso: "azul:1","vermelho:0.8","verde:0.6"
```

Após preencher o campo ou carregar o arquivo, clique em "Importar Perguntas" para adicionar as perguntas ao sistema.

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
