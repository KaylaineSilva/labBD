# Projeto Final — Laboratório de Bases de Dados (SCC-241)

Este projeto foi desenvolvido para a disciplina de Laboratório de Bases de Dados, utilizando a base de dados da Fórmula 1. A aplicação permite a exploração dos dados por meio de uma interface web com autenticação, dashboards, relatórios e ações específicas para diferentes tipos de usuários.

## Tecnologias utilizadas

* Python
* Streamlit
* PostgreSQL
* psycopg2
* Pandas
* bcrypt

## Estrutura geral do projeto

```text
labBD/
├── app.py
├── db.py
├── auth.py
├── requirements.txt
├── README.md
├── admin/
│   ├── admin_dashboard.py
│   ├── admin_relatorios.py
│   ├── admin_cadastrar.py
│   └── admin_func.py
├── escuderia/
│   ├── dashboard_escuderia.py
│   ├── relatorios_escuderia.py
│   └── acoes_escuderia.py
├── piloto/
│   ├── dashboard_piloto.py
│   └── relatorios_piloto.py
├── bd_conf/
│   └── table_users.sql
└── sql/
    ├── triggers.sql
    ├── func_admin.sql
    └── indice_admin.sql
```

## Funcionalidades implementadas

### Autenticação de usuários

A aplicação possui um sistema de login baseado na tabela `USERS`. Cada usuário possui um tipo de acesso, podendo ser:

* `Admin`
* `Escuderia`
* `Piloto`

As senhas são armazenadas utilizando hash, evitando o armazenamento em texto puro. A tabela `USERS_LOG` registra operações relevantes, como login, logout e cadastros realizados no sistema.

### Usuário administrador

O usuário administrador possui acesso a dashboards, relatórios e ações administrativas.

Funcionalidades principais:

* Visualização da quantidade total de pilotos, escuderias e temporadas cadastradas.
* Listagem das corridas da temporada mais recente.
* Listagem das escuderias que correram na temporada mais recente, com total de pontos obtidos.
* Listagem dos pilotos que correram na temporada mais recente, com total de pontos obtidos.
* Cadastro de novos pilotos.
* Cadastro de novas escuderias.
* Relatórios administrativos específicos.

Ao cadastrar um novo piloto ou escuderia, triggers no banco de dados criam automaticamente o usuário correspondente na tabela `USERS`.

### Usuário escuderia

O usuário do tipo escuderia acessa funcionalidades relacionadas à sua própria equipe. A aplicação utiliza o campo `id_original` da tabela `USERS` para identificar qual escuderia está logada e, a partir disso, restringir as consultas aos dados correspondentes.

Funcionalidades principais:

* Dashboard com informações da escuderia logada.
* Relatórios específicos da escuderia.
* Ações permitidas para o perfil de escuderia.

### Usuário piloto

O usuário do tipo piloto acessa informações relacionadas ao seu próprio histórico na base. Assim como no perfil de escuderia, o campo `id_original` é utilizado para relacionar o usuário autenticado ao registro correspondente na tabela `DRIVERS`.

Funcionalidades principais:

* Dashboard com informações do piloto logado.
* Relatórios específicos do piloto.
* Visualização de dados relacionados às participações do piloto.

## Técnicas de banco de dados utilizadas

O projeto utiliza diferentes recursos de banco de dados, incluindo:

* Criação de tabelas auxiliares, como `USERS` e `USERS_LOG`.
* Consultas SQL com `JOIN`, `LEFT JOIN`, `GROUP BY`, `ORDER BY`, funções de agregação e subconsultas.
* Funções armazenadas no PostgreSQL para modularizar consultas mais complexas.
* Triggers para criação automática de usuários após cadastro de pilotos e escuderias.
* Índices para auxiliar consultas específicas, especialmente nos relatórios que envolvem busca por cidade, aeroportos e tipos de aeroporto.
* Controle de transações com `COMMIT` e `ROLLBACK` em operações críticas.

## Scripts SQL

Os principais scripts SQL utilizados pela aplicação são:

* `bd_conf/table_users.sql`: cria as tabelas `USERS` e `USERS_LOG`, caso ainda não existam.
* `sql/triggers.sql`: cria os triggers responsáveis por gerar usuários automaticamente após o cadastro de pilotos e escuderias.
* `sql/func_admin.sql`: cria funções armazenadas utilizadas nos relatórios do usuário administrador.
* `sql/indice_admin.sql`: cria índices para auxiliar consultas administrativas.

## Como rodar o projeto

### 1. Clonar o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd labBD
```

### 2. Criar e ativar o ambiente virtual

No Linux ou WSL:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

No Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 5. Rodar a aplicação

Com o ambiente virtual ativado, execute:

```bash
streamlit run app.py
```

Depois, acesse no navegador:

```text
http://localhost:8501
```

## Usuários de acesso

Os usuários são criados automaticamente a partir dos dados existentes na base.

### Administrador

```text
Login: admin
Senha: admin
```

### Escuderias

Para escuderias, o login segue o formato:

```text
<constructor_ref>_c
```

A senha inicial corresponde ao valor de `constructor_ref`.

Exemplo:

```text
Login: mclaren_c
Senha: mclaren
```

### Pilotos

Para pilotos, o login segue o formato:

```text
<driver_ref>_d
```

A senha inicial corresponde ao valor de `driver_ref`.

Exemplo:

```text
Login: hamilton_d
Senha: hamilton
```

## Observações

* Os scripts SQL são executados automaticamente na inicialização da aplicação para garantir que tabelas auxiliares, triggers, funções e índices existam no banco.
* As funções e triggers utilizam `CREATE OR REPLACE` ou comandos equivalentes para evitar erros em execuções repetidas.
* A aplicação utiliza `st.session_state` para controlar o usuário autenticado e a navegação entre páginas.
* O sistema foi organizado em módulos para separar autenticação, conexão com o banco, telas de administrador, escuderia e piloto.

## Autoria
Giovanna Lopes de Andrade - 14574772 

Julia de Almeida Carvalho - 13713184 

Kaylaine Bessa da Silva - 14747506 

Roberto Spíndola Abrenhosa Filho - 14748960