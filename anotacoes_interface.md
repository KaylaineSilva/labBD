# Anotações da Interface Streamlit

---

## 1. Visão geral

A interface foi desenvolvida em **Python com Streamlit**.

Rodar: streamlit run app.py

Ela organiza o sistema em três tipos de usuário:

* **Admin**
* **Escuderia**
* **Piloto**

Cada tipo de usuário acessa telas diferentes de acordo com suas permissões.

O fluxo principal da aplicação é:

1. Usuário acessa a tela de login.
2. Após autenticação, o sistema salva os dados do usuário em `st.session_state`.
3. O menu lateral é exibido.
4. O usuário navega entre:

   * Dashboard
   * Relatórios
   * Ações
   * Teste de conexão, disponível apenas para Admin, se mantido no código.
5. Cada tela carrega informações específicas de acordo com o tipo de usuário logado.

---

## 2. Estrutura de arquivos

A estrutura atual da interface está organizada aproximadamente assim:

```text
labBD/
├── app.py
├── db.py
├── telas/
│   ├── __init__.py
│   ├── dashboard_admin.py
│   ├── dashboard_escuderia.py
│   ├── dashboard_piloto.py
│   ├── relatorios_admin.py
│   ├── relatorios_escuderia.py
│   ├── relatorios_piloto.py
│   └── acoes.py
└── anotacoes_interface.md
```

---

## 3. Arquivo `app.py`

O arquivo `app.py` é o arquivo principal da aplicação.

Ele é responsável por:

* configurar a página do Streamlit;
* inicializar variáveis de sessão;
* exibir a tela de login;
* montar o menu lateral;
* controlar o logout;
* decidir qual tela será exibida;
* direcionar o usuário para o dashboard, relatórios ou ações corretas conforme o tipo de usuário.

### Principais responsabilidades

#### `st.set_page_config(...)`

Define configurações gerais da página, como título, ícone e layout.

Exemplo:

```python
st.set_page_config(
    page_title="Sistema Fórmula 1",
    page_icon="🏎️",
    layout="wide"
)
```

#### `inicializar_sessao()`

Cria as variáveis necessárias no `st.session_state`.

As principais variáveis usadas são:

```python
st.session_state.logado
st.session_state.usuario
st.session_state.pagina
```

Significado:

* `logado`: indica se há usuário autenticado.
* `usuario`: armazena informações do usuário logado.
* `pagina`: indica qual tela está selecionada no menu lateral.

O dicionário do usuário segue este formato:

```python
{
    "userid": ...,
    "login": ...,
    "tipo": ...,
    "id_original": ...
}
```

O campo `tipo` pode ser:

```text
Admin
Escuderia
Piloto
```

O campo `id_original` representa:

* `None` para Admin;
* `constructors.id` para Escuderia;
* `drivers.id` para Piloto.

#### `tela_login()`

Mostra os campos de login e senha.

Atualmente, a interface usa uma autenticação baseada nos padrões do projeto:

* Admin:

  * login: `admin`
  * senha: `admin`

* Escuderia:

  * login: `<constructor_ref>_c`
  * senha: `<constructor_ref>`

* Piloto:

  * login: `<driver_ref>_d`
  * senha: `<driver_ref>`

Exemplos:

```text
admin / admin
mclaren_c / mclaren
hamilton_d / hamilton
```

A interface já busca o `id_original` no banco usando o `constructor_ref` ou `driver_ref`, para que os dashboards e relatórios mostrem dados do usuário correto.

Ponto a integrar futuramente:

* substituir a autenticação atual por consulta real à tabela `USERS`;
* validar senha protegida, não em texto puro;
* registrar login na tabela `USERS_LOG`.

#### `menu_lateral()`

Exibe o menu depois do login.

As opções principais são:

```text
Dashboard
Relatórios
Ações
```

Para Admin, pode aparecer também:

```text
Teste de conexão
```

O menu lateral também mostra:

* login do usuário;
* tipo do usuário;
* botão de sair.

Ponto a integrar futuramente:

* ao clicar em sair, registrar logout na tabela `USERS_LOG`.

#### `roteador()`

Decide qual função chamar com base na página selecionada e no tipo do usuário.

Exemplo lógico:

```python
if pagina == "Dashboard":
    if tipo == "Admin":
        mostrar_dashboard_admin(usuario)
    elif tipo == "Escuderia":
        mostrar_dashboard_escuderia(usuario)
    elif tipo == "Piloto":
        mostrar_dashboard_piloto(usuario)
```

Esse roteamento é o que garante que cada usuário veja apenas as telas correspondentes ao seu perfil.

---

## 4. Arquivo `db.py`

O arquivo `db.py` concentra a conexão com o banco de dados PostgreSQL.

Ele deve conter uma função chamada:

```python
conectar()
```

Essa função é usada pelos arquivos da interface para abrir conexão com o banco.

Exemplo de uso:

```python
conn = conectar()
cur = conn.cursor()
```

A interface depende desse arquivo para executar as consultas SQL.

Pontos importantes:

* a função `conectar()` precisa usar o schema correto;
* se o projeto usa `search_path`, ele deve estar configurado corretamente;
* qualquer alteração no nome do schema pode afetar todas as consultas da interface.

---

## 5. Pasta `telas/`

A pasta `telas/` contém as telas separadas da aplicação.

O arquivo `__init__.py` pode ficar vazio. Ele serve para o Python reconhecer a pasta como um pacote importável.

---

## 6. Arquivo `dashboard_admin.py`

Esse arquivo implementa o Dashboard do Administrador.

Função principal:

```python
mostrar_dashboard_admin(usuario)
```

### O que essa tela mostra

O dashboard do Admin apresenta:

1. total de pilotos cadastrados;
2. total de escuderias cadastradas;
3. total de temporadas cadastradas;
4. lista das corridas da temporada mais recente;
5. lista das escuderias da temporada mais recente com total de pontos;
6. lista dos pilotos da temporada mais recente com total de pontos.

### Consultas usadas

A tela consulta tabelas como:

```text
drivers
constructors
races
results
circuits
seasons
```

A temporada mais recente é identificada a partir da data mais recente em `races.race_date`, e não pelo maior `season_id`, porque o `season_id` não necessariamente representa ordem cronológica.

### Observações para integração

Se alguém alterar nomes de colunas, conferir principalmente:

```text
drivers.id
constructors.id
races.id
races.race_name
races.race_date
races.race_time
races.circuit_id
results.race_id
results.driver_id
results.constructor_id
results.points
results.laps
circuits.id
circuits.name
```

---

## 7. Arquivo `dashboard_escuderia.py`

Esse arquivo implementa o Dashboard da Escuderia.

Função principal:

```python
mostrar_dashboard_escuderia(usuario)
```

### O que essa tela mostra

A tela recebe o `constructor_id` por:

```python
constructor_id = usuario["id_original"]
```

E mostra:

1. nome da escuderia;
2. quantidade de vitórias;
3. quantidade de pilotos diferentes que já correram pela escuderia;
4. primeiro ano em que há dados da escuderia;
5. último ano em que há dados da escuderia.

### Tabelas usadas

```text
constructors
results
races
```

### Observações para integração

Essa tela depende do login preencher corretamente:

```python
usuario["id_original"]
```

Para escuderias, esse valor deve ser o `id` da tabela `constructors`.

---

## 8. Arquivo `dashboard_piloto.py`

Esse arquivo implementa o Dashboard do Piloto.

Função principal:

```python
mostrar_dashboard_piloto(usuario)
```

### O que essa tela mostra

A tela recebe o `driver_id` por:

```python
driver_id = usuario["id_original"]
```

E mostra:

1. nome completo do piloto;
2. escuderia mais recente associada ao piloto;
3. primeiro ano em que há dados do piloto;
4. último ano em que há dados do piloto;
5. desempenho por ano e circuito:

   * pontos obtidos;
   * vitórias;
   * total de corridas.

### Tabelas usadas

```text
drivers
results
races
constructors
circuits
```

### Observações para integração

Para pilotos, `usuario["id_original"]` precisa ser o `id` da tabela `drivers`.

---

## 9. Arquivo `relatorios_admin.py`

Esse arquivo implementa os relatórios disponíveis para o Admin.

Função principal:

```python
mostrar_relatorios_admin(usuario)
```

A tela usa um `selectbox` para escolher qual relatório será exibido.

### Relatório 1: Quantidade de resultados por status

Função:

```python
relatorio_resultados_por_status()
```

Mostra:

* nome do status;
* quantidade de resultados associados a cada status.

Tabelas usadas:

```text
results
status
```

Colunas esperadas:

```text
results.status_id
status.id
status.status
```

---

### Relatório 2: Aeroportos próximos a uma cidade brasileira

Função:

```python
relatorio_aeroportos_por_cidade()
```

Entrada do usuário:

```text
Nome da cidade
```

Mostra aeroportos brasileiros a até 100 km da cidade pesquisada, considerando apenas tipos:

```text
medium_airport
large_airport
```

Tabelas usadas:

```text
cities
countries
airports
airport_types
```

Colunas esperadas:

```text
cities.id
cities.name
cities.latitude
cities.longitude
cities.country_id

countries.id
countries.code
countries.name

airports.id
airports.name
airports.iata_code
airports.latitude_deg
airports.longitude_deg
airports.city_id
airports.airport_type_id

airport_types.id
airport_types.type
```

Detalhes importantes:

* A busca foi ajustada para aceitar cidade com ou sem acento.
* Exemplo: `sao paulo` encontra `São Paulo`.
* A busca foi ajustada para ser exata após normalização, evitando que `sao paulo` traga também `São Paulo do Potengi`.
* A distância é calculada pela fórmula baseada em latitude e longitude.
* A consulta filtra apenas cidades brasileiras usando `countries.code = 'BR'` ou nomes equivalentes.

Ponto a integrar futuramente:

* criar índice para auxiliar a consulta, especialmente em cidades, países e aeroportos.

---

### Relatório 3: Relatório hierárquico de escuderias e corridas

Função:

```python
relatorio_hierarquico()
```

Esse relatório apresenta:

1. lista de escuderias cadastradas e quantidade de pilotos;
2. quantidade total de corridas cadastradas;
3. quantidade de corridas por circuito;
4. mínimo, média e máximo de voltas por circuito;
5. para um circuito selecionado, lista as corridas, voltas registradas e quantidade de pilotos participantes.

Tabelas usadas:

```text
constructors
results
drivers
races
circuits
```

Observação:

* O relatório usa um `selectbox` para o usuário escolher um circuito e visualizar o detalhamento daquele circuito.

---

## 10. Arquivo `relatorios_escuderia.py`

Esse arquivo implementa os relatórios disponíveis para Escuderia.

Função principal:

```python
mostrar_relatorios_escuderia(usuario)
```

A tela identifica a escuderia logada por:

```python
constructor_id = usuario["id_original"]
```

### Relatório 4: Vitórias por piloto da escuderia

Função:

```python
relatorio_vitorias_por_piloto(constructor_id)
```

Mostra:

* nome completo do piloto;
* quantidade de vitórias pela escuderia.

Tabelas usadas:

```text
results
drivers
```

Critério de vitória:

```text
results.position_order = 1
```

Restrição de escopo:

```text
results.constructor_id = constructor_id
```

---

### Relatório 5: Quantidade de resultados por status

Função:

```python
relatorio_status_escuderia(constructor_id)
```

Mostra:

* status;
* quantidade de resultados.

Tabelas usadas:

```text
results
status
```

Restrição de escopo:

```text
results.constructor_id = constructor_id
```

Esse filtro garante que a escuderia veja apenas informações relacionadas a ela.

---

## 11. Arquivo `relatorios_piloto.py`

Esse arquivo implementa os relatórios disponíveis para Piloto.

Função principal:

```python
mostrar_relatorios_piloto(usuario)
```

A tela identifica o piloto logado por:

```python
driver_id = usuario["id_original"]
```

### Relatório 6: Pontos por ano e corridas pontuadas

Função:

```python
relatorio_pontos_por_ano(driver_id)
```

Mostra:

1. resumo por ano:

   * ano;
   * total de pontos;
   * corridas disputadas;
   * corridas com pontos;

2. para cada ano, exibe as corridas em que o piloto obteve pontos.

A interface usa `st.expander()` para organizar as corridas por ano.

Tabelas usadas:

```text
results
races
circuits
```

Restrição de escopo:

```text
results.driver_id = driver_id
```

Filtro das corridas pontuadas:

```text
results.points > 0
```

Esse relatório deve mostrar apenas informações do piloto logado.

---

### Relatório 7: Quantidade de resultados por status

Função:

```python
relatorio_status_piloto(driver_id)
```

Mostra:

* status;
* quantidade de resultados.

Tabelas usadas:

```text
results
status
```

Restrição de escopo:

```text
results.driver_id = driver_id
```

Esse filtro garante que o piloto veja apenas os status das corridas em que participou.

---

## 12. Arquivo `acoes.py`

Esse arquivo implementa a tela de ações do sistema.

Função principal:

```python
mostrar_acoes(usuario)
```

Essa função verifica o tipo do usuário e chama:

```python
acoes_admin()
acoes_escuderia(usuario)
```

Para Piloto, a tela apenas mostra uma mensagem informando que pilotos não podem alterar dados.

---

### Ações do Admin

Função:

```python
acoes_admin()
```

O Admin possui duas abas:

```text
Cadastrar escuderia
Cadastrar piloto
```

#### Cadastrar escuderia

Campos da interface:

```text
constructor_ref
name
country_id
wikipedia_url
```

Ponto a integrar:

* chamar uma função real de inserção na tabela `constructors`;
* após a inserção, a trigger do banco deve criar automaticamente o usuário correspondente na tabela `USERS`;
* se já existir usuário com o login gerado, a trigger deve cancelar a inserção.

#### Cadastrar piloto

Campos da interface:

```text
driver_ref
given_name
family_name
date_of_birth
country_id
```

Ponto a integrar:

* chamar uma função real de inserção na tabela `drivers`;
* após a inserção, a trigger do banco deve criar automaticamente o usuário correspondente na tabela `USERS`;
* validar se o piloto já existe, se essa regra ficar na aplicação ou no banco.

---

### Ações da Escuderia

Função:

```python
acoes_escuderia(usuario)
```

A Escuderia possui duas abas:

```text
Consultar piloto por sobrenome
Inserir pilotos por arquivo
```

#### Consultar piloto por sobrenome

Entrada:

```text
Sobrenome do piloto
```

Ponto a integrar:

* consultar se existe piloto com esse sobrenome que já tenha corrido pela escuderia logada;
* usar `usuario["id_original"]` como `constructor_id`;
* consultar a tabela `results` para verificar associação entre piloto e escuderia;
* retornar nome completo, data de nascimento e país ou nacionalidade associada ao piloto.

#### Inserir pilotos por arquivo

A interface permite upload de arquivo CSV ou TXT.

Formato esperado do arquivo:

```text
driver_ref,given_name,family_name,date_of_birth,country_id
```

Ponto a integrar:

* ler cada linha do arquivo;
* validar se já existe piloto com mesmo nome e sobrenome;
* inserir piloto na tabela `drivers`;
* criar automaticamente o usuário correspondente via trigger;
* decidir se será registrada associação explícita entre o novo piloto e a escuderia logada.

---

## 13. Tela de Teste de Conexão

A tela de teste de conexão fica dentro do `app.py`.

Ela foi criada apenas para ajudar no desenvolvimento.

Funções da tela:

* mostrar o schema atual;
* listar tabelas disponíveis;
* permitir selecionar uma tabela;
* mostrar colunas e tipos de dados;
* mostrar os primeiros registros da tabela escolhida.

Essa tela foi útil para conferir nomes reais de tabelas e colunas.

Recomendação:

* manter essa tela apenas para Admin durante o desenvolvimento;
* antes da entrega, decidir se ela será removida ou mantida como ferramenta administrativa;
* se mantida, tomar cuidado para não expor informações desnecessárias.

---

## 14. Variável `usuario`

Todas as telas recebem um dicionário chamado `usuario`.

Formato esperado:

```python
usuario = {
    "userid": int,
    "login": str,
    "tipo": str,
    "id_original": int | None
}
```

Exemplos:

Admin:

```python
{
    "userid": 1,
    "login": "admin",
    "tipo": "Admin",
    "id_original": None
}
```

Escuderia:

```python
{
    "userid": 2,
    "login": "mclaren_c",
    "tipo": "Escuderia",
    "id_original": 1
}
```

Piloto:

```python
{
    "userid": 3,
    "login": "hamilton_d",
    "tipo": "Piloto",
    "id_original": 1
}
```

Importante:

* Para Escuderia, `id_original` deve ser o `constructors.id`.
* Para Piloto, `id_original` deve ser o `drivers.id`.
* Para Admin, `id_original` pode ser `None`.

---

## 15. Pontos pendentes para integração com banco

A interface está pronta estruturalmente, mas alguns pontos dependem das implementações de banco de dados.

### Autenticação real

Atualmente, o login segue o padrão do projeto, mas deve ser integrado à tabela:

```text
USERS
```

Campos esperados:

```text
userid
login
password
tipo
id_original
```

Pontos pendentes:

* buscar usuário por login;
* validar senha protegida;
* não armazenar senha em texto puro;
* preencher `st.session_state.usuario` com os dados vindos da tabela `USERS`.

---

### Auditoria de login/logout

Deve ser integrada a tabela:

```text
USERS_LOG
```

Pontos pendentes:

* registrar `LOGIN` quando o usuário entra;
* registrar `LOGOUT` quando o usuário sai;
* armazenar `userid`, ação e data/hora.

---

### Inserções reais

As ações do Admin e da Escuderia já possuem formulários, mas ainda precisam chamar funções reais de inserção no banco.

Pontos pendentes:

* inserir escuderia em `constructors`;
* inserir piloto em `drivers`;
* tratar erros de duplicidade;
* exibir mensagens amigáveis em caso de sucesso ou erro;
* garantir que triggers criem ou atualizem os registros correspondentes em `USERS`.

---

### Upload de arquivo

A interface já permite upload de arquivo para inserção de pilotos.

Pontos pendentes:

* validar formato do arquivo;
* validar colunas obrigatórias;
* validar duplicidade de piloto;
* inserir pilotos válidos;
* informar quais linhas foram inseridas e quais foram rejeitadas.

---

### Índices

Alguns relatórios exigem índices para otimização.

Sugestões de índices para discutir com quem está implementando SQL:

```sql
CREATE INDEX IF NOT EXISTS idx_results_driver_race
ON results(driver_id, race_id);

CREATE INDEX IF NOT EXISTS idx_results_constructor_driver
ON results(constructor_id, driver_id);

CREATE INDEX IF NOT EXISTS idx_results_constructor_status
ON results(constructor_id, status_id);

CREATE INDEX IF NOT EXISTS idx_results_driver_status
ON results(driver_id, status_id);

CREATE INDEX IF NOT EXISTS idx_races_circuit_date
ON races(circuit_id, race_date);

CREATE INDEX IF NOT EXISTS idx_airports_city_type
ON airports(city_id, airport_type_id);

CREATE INDEX IF NOT EXISTS idx_cities_name_country
ON cities(name, country_id);
```

Esses índices são sugestões iniciais. Eles devem ser revisados conforme as queries finais e o plano de execução.

---

## 16. Como executar a interface

No terminal, dentro da pasta do projeto:

```bash
cd ~/code/labBD
```

Ativar ambiente virtual:

```bash
source .venv/bin/activate
```

Rodar a aplicação:

```bash
python -m streamlit run app.py
```

Ou, se o comando `streamlit` estiver disponível:

```bash
streamlit run app.py
```

---

## 17. Logins para teste

Admin:

```text
admin / admin
```

Escuderia:

```text
mclaren_c / mclaren
```

Piloto:

```text
hamilton_d / hamilton
```

Também é possível testar com outras escuderias e pilotos existentes na base, seguindo os padrões:

```text
<constructor_ref>_c / <constructor_ref>
<driver_ref>_d / <driver_ref>
```

---

## 18. Checklist da interface

Antes da entrega, testar:

### Admin

* Login com `admin / admin`.
* Dashboard Admin aparece.
* Relatório 1 funciona.
* Relatório 2 funciona para uma cidade brasileira, como `sao paulo`.
* Relatório 3 funciona.
* Ações Admin aparecem.
* Formulário de cadastrar escuderia aparece.
* Formulário de cadastrar piloto aparece.
* Logout funciona.

### Escuderia

* Login com uma escuderia existente.
* Dashboard da escuderia aparece.
* Relatório de vitórias por piloto aparece.
* Relatório de status da escuderia aparece.
* Ações da escuderia aparecem.
* Consulta por sobrenome aparece.
* Upload de arquivo aparece.
* Logout funciona.

### Piloto

* Login com um piloto existente.
* Dashboard do piloto aparece.
* Relatório de pontos por ano aparece.
* Relatório de status do piloto aparece.
* Tela de ações bloqueia alteração de dados.
* Logout funciona.

---

## 19. Observações finais

A interface já está estruturada para o fluxo completo do sistema.

O principal ponto de atenção para as próximas implementações é substituir os trechos provisórios das ações por chamadas reais ao banco e integrar a autenticação com a tabela `USERS`.

As consultas dos dashboards e relatórios já estão sendo executadas diretamente no código, com SQL explícito, para facilitar análise e avaliação.

Sempre que alguma tabela ou coluna for alterada, revisar os arquivos da pasta `telas/`, principalmente os relatórios e dashboards que dependem diretamente dos nomes das colunas.
