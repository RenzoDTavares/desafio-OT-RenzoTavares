<p>
    <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcQIAOtqQ5is5vwbcEn0ZahZfMxz1QIeAYtFfnLdkCXu1sqAGbnX" width="300">
 </p>
 
# API de Upload e Busca de Dados

## Visão Geral

Esta API permite o upload de arquivos, armazenamento de informações em um banco de dados e fornece funcionalidades de busca e histórico de uploads. É construída com Django e Django REST Framework.

## Estrutura do Projeto

As principais funcionalidades incluem:

- **Upload de Arquivos:** Carregue arquivos CSV, XLSX e XLS.
- **Histórico de Uploads:** Mantenha um histórico dos arquivos carregados.
- **Busca de Dados:** Realize consultas em dados carregados.
- **Autenticação:** Utilize tokens JWT para autenticação.

## URLs da API

Abaixo estão os endpoints disponíveis na API:

| Método | Endpoint          | Descrição                                                  |
|--------|-------------------|------------------------------------------------------------|
| GET    | `/api/v1/`       | Visualiza os endpoints da API.                             |
| POST   | `/api/v1/upload/` | Faz o upload de um arquivo e armazena as informações no banco de dados. |
| GET    | `/api/v1/history/`| Retorna o histórico de uploads com paginação.             |
| POST   | `/api/v1/token/`  | Obtém um token de autenticação com base em nome de usuário e senha. |
| GET    | `/api/v1/search/` | Realiza uma busca de registros com filtros específicos.    |

## Instalação

### Pré-requisitos

- Python 3.8.2
- Django
- Django REST Framework
- Pandas
- Django REST Framework Simple JWT

### Passos para Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/RenzoDTavares/desafio-OT-RenzoTavares.git
   ```

2. Navegue até o diretório do projeto:
   ```bash
   cd seu_repositorio
   ```

3. Crie um ambiente virtual e ative-o:
   ```bash
   python -m venv env
   `.\env\Scripts\activate`
   ```

4. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

5. Execute as migrações:
   ```bash
   python manage.py migrate
   ```

6. Inicie o servidor de desenvolvimento:
   ```bash
   python manage.py runserver
   ```

## Uso

### 1. Autenticação

Para autenticar um usuário e obter um token, faça uma solicitação `POST` para o endpoint `/api/v1/token/` com os seguintes dados:

```json
{
  "username": "seu_usuario",
  "password": "sua_senha"
}
```

**Exemplo com Postman:**
- **URL:** `http://localhost:8000/api/v1/token/`
- **Método:** `POST`
- **Body:** form-data ou raw com JSON

### 2. Upload de Arquivo

Para fazer o upload de um arquivo, envie uma solicitação `POST` para o endpoint `/api/v1/upload/` com os seguintes dados:

- `file`: O arquivo a ser carregado (CSV, XLSX ou XLS).
- `reference_date`: Data de referência no formato `YYYY-MM-DD`.

**Melhoria:** Há uma validação no processamento que, caso as colunas ['RptDt', 'TckrSymb', 'MktNm', 'SctyCtgyNm', 'ISIN'] estejam nulas, o processamento ignorará essa linha.

**Exemplo com Postman:**
- **URL:** `http://localhost:8000/api/v1/upload/`
- **Método:** `POST`
- **Body:** form-data
  - `file`: Selecione o arquivo
  - `reference_date`: `2024-10-29` 
- **Cabeçalho:**
    - Authorization: Bearer SEU_TOKEN

### 3. Consultar o Histórico de Uploads

Para consultar o histórico de uploads, envie uma solicitação `GET` para o endpoint `/api/v1/history/`.

**Exemplo com Postman:**
- **URL:** `http://localhost:8000/api/v1/history/`
- **Método:** `GET`
- **Cabeçalho:**
    - Authorization: Bearer SEU_TOKEN

### 4. Buscar Dados

Para buscar dados específicos, envie uma solicitação `GET` para o endpoint `/api/v1/search/` com os parâmetros desejados.

**Exemplo de Parâmetros:**
- `TckrSymb`: Símbolo do ticker.
- `RptDt`: Data do relatório no formato `YYYY-MM-DD`.
- `MktNm`: Nome do mercado.
- `SctyCtgyNm`: Categoria de segurança.
- `ISIN`: Código ISIN.
- `CrpnNm`: Nome da corporação.
- **Cabeçalho:**
    - Authorization: Bearer SEU_TOKEN

**Exemplo com Postman:**
- **URL:** `http://localhost:8000/api/v1/search/?TckrSymb=AAPL`
- **Método:** `GET`
- **Cabeçalho:**
    - Authorization: Bearer SEU_TOKEN

## Testes 

Os testes para a API estão organizados na classe HistoryTests, SearchTests, UploadTests e TokenAuthTests, que utiliza o framework de testes do Django. Os testes abrangem as seguintes funcionalidades:
- CT001: Upload de um arquivo sem erros
- CT002: Upload de um arquivo com erros em 6 linhas
- CT003: Upload de um arquivo já existente na base de dados
- CT004: Upload de um arquivo sem os campos obrigatórios (file e reference_date)
- CT005: Upload de um arquivo invalido
- CT006: Upload de um arquivo sem as credenciais de acesso    
- CT007: Filtro por nome do arquivo no histórico
- CT008: Busca de histórico com diretório vazio
- CT009: Busca de um item com parametros
- CT010: Busca de um item com parametro de data errado
- CT011: Validação de paginação na busca de vários itens
- CT012: Login com as credenciais corretas    
- CT013: Login com as credenciais erradas

Você pode rodar os testes utilizando o comando:
```bash
python manage.py test uploader/tests
````

## Contribuidor

Este projeto foi desenvolvido por [Renzo Tavares](https://www.linkedin.com/in/renzotavares/) para o desafio referente a uma vaga de desenvolvedor na Oliveira Trust.
