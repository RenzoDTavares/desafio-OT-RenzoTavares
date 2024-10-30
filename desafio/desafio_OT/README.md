Documentação da API
Visão Geral
Esta API permite o upload de arquivos, armazenamento de informações em um banco de dados e fornece funcionalidades de busca e histórico de uploads. 

Estrutura do Projeto
O projeto é construído com Django e Django REST Framework. As principais funcionalidades incluem:

Upload de Arquivos: Carregue arquivos CSV, XLSX e XLS.
Histórico de Uploads: Mantenha um histórico dos arquivos carregados.
Busca de Dados: Realize consultas em dados carregados.
Autenticação: Utilize tokens JWT para autenticação.
URLs da API
Abaixo estão os endpoints disponíveis na API:

Método	Endpoint	Descrição
GET	/api/v1/	Visualiza os endpoints da API.
POST	/api/v1/upload/	Faz o upload de um arquivo e armazena as informações no banco de dados.
GET	/api/v1/history/	Retorna o histórico de uploads com paginação.
POST	/api/v1/token/	Obtém um token de autenticação com base em nome de usuário e senha.
GET	/api/v1/search/	Realiza uma busca de registros com filtros específicos.

Instalação
Pré-requisitos
Python 3.8.2
Django
Django REST Framework
Pandas
Django REST Framework Simple JWT
Passos para Instalação
Clone o repositório:

bash
Copiar código
git clone https://github.com/seu_usuario/seu_repositorio.git
Navegue até o diretório do projeto:

bash
Copiar código
cd seu_repositorio
Crie um ambiente virtual e ative-o:

bash
Copiar código
python -m venv env
source env/bin/activate  # No Windows use `env\Scripts\activate`
Instale as dependências:

bash
Copiar código
pip install -r requirements.txt
Execute as migrações:

bash
Copiar código
python manage.py migrate
Inicie o servidor de desenvolvimento:

bash
Copiar código
python manage.py runserver
Uso
1. Autenticação
Para autenticar um usuário e obter um token, faça uma solicitação POST para o endpoint /api/v1/token/ com os seguintes dados:

json
Copiar código
{
  "username": "seu_usuario",
  "password": "sua_senha"
}
Exemplo com Postman
URL: http://localhost:8000/api/v1/token/
Método: POST
Body: form-data ou raw com JSON
2. Upload de Arquivo
Para fazer o upload de um arquivo, envie uma solicitação POST para o endpoint /api/v1/upload/ com os seguintes dados:

file: O arquivo a ser carregado (CSV, XLSX ou XLS).
reference_date: Data de referência no formato YYYY-MM-DD.
Exemplo com Postman
URL: http://localhost:8000/api/v1/upload/
Método: POST
Body: form-data
file: Selecione o arquivo
reference_date: 2024-10-29
3. Consultar o Histórico de Uploads
Para consultar o histórico de uploads, envie uma solicitação GET para o endpoint /api/v1/history/.

Exemplo com Postman
URL: http://localhost:8000/api/v1/history/
Método: GET
4. Buscar Dados
Para buscar dados específicos, envie uma solicitação GET para o endpoint /api/v1/search/ com os parâmetros desejados:

Exemplo de Parâmetros
TckrSymb: Símbolo do ticker.
RptDt: Data do relatório no formato YYYY-MM-DD.
MktNm: Nome do mercado.
SctyCtgyNm: Categoria de segurança.
ISIN: Código ISIN.
CrpnNm: Nome da corporação.
Exemplo com Postman
URL: http://localhost:8000/api/v1/search/?TckrSymb=AAPL
Método: GET
Testes
Você pode testar a API usando o Postman. Certifique-se de que o servidor esteja em execução e siga os exemplos fornecidos acima.

Exemplos de Testes
Teste de Autenticação:

Verifique se o token é retornado corretamente ao enviar um POST para /api/v1/token/.

Teste de Upload:

Verifique se o upload de um arquivo válido é bem-sucedido e se os dados são salvos no banco de dados.

Teste de Consulta de Histórico:

Verifique se o histórico de uploads pode ser recuperado corretamente.

Teste de Busca:

Teste se a busca retorna resultados válidos de acordo com os parâmetros fornecidos.
