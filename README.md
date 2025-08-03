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
│   │   ├── api.py
│   ├── static/
│   │   ├── admin.js
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
├── build_exe.py
├── LICENSE
```

### Principais Arquivos e Funcionalidades

- **`app/__init__.py`**: Inicializa a aplicação Flask e configura os blueprints.
- **`app/models.py`**: Define os modelos do banco de dados, como `User`, `Question`, `Option` e `Resultado`.
- **`app/auth/routes.py`**: Gerencia autenticação e rotas relacionadas ao login e cadastro.
- **`app/main/routes.py`**: Contém as rotas principais, como submissão de questionários e administração.
- **`app/main/api.py`**: Fornece uma API para buscar perguntas em formato JSON.
- **`app/static/admin.js`**: Scripts JavaScript para melhorar a experiência do usuário no painel administrativo.
- **`app/static/style.css`**: Estilos CSS para garantir um design moderno e responsivo.
- **`app/templates/`**: Contém os templates HTML para renderização das páginas.
- **`config.py`**: Configurações da aplicação, incluindo a conexão com o banco de dados SQLite.
- **`run.py`**: Arquivo principal para executar a aplicação.
- **`build_exe.py`**: Script para empacotar a aplicação em um executável usando PyInstaller.
- **`LICENSE`**: Licença MIT para uso do projeto.

### Como Executar

1. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

2. Execute a aplicação:

   ```bash
   python run.py
   ```

3. Acesse a aplicação no navegador em `http://127.0.0.1:5000`.

### Empacotamento

Para gerar um executável da aplicação, utilize o script `build_exe.py`:

```bash
python build_exe.py
```

### Exemplos de Uso

#### Importação de Perguntas em Lote

O arquivo `exemplo-perguntas-em-lote.txt` contém exemplos de perguntas que podem ser importadas em lote para o sistema. Cada linha segue o formato:

```
pergunta: "Você gosta de café?"
opcoes e peso: "sim:1","nao:0","depende:0.5"
```

Para importar, utilize o formulário disponível no painel administrativo.

#### Exportação de Resultados

Os resultados dos questionários podem ser exportados em formato CSV diretamente pelo painel administrativo. Basta clicar no botão "Exportar Resultados" e o arquivo será gerado automaticamente.

#### Gerenciamento de Perguntas

No painel administrativo, é possível adicionar, editar e excluir perguntas. Além disso, há suporte para gerenciar opções de resposta.

### Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
