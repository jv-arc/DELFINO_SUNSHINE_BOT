# Projeto de Automação com n8n, PostgreSQL e Docker

Este projeto demonstra um fluxo de automação completo para processar dados de clientes, popular um banco de dados e gerar e-mails com base em análises de dados. A orquestração é feita pelo n8n, com o suporte de um banco de dados PostgreSQL e um servidor SMTP de teste (smtp4dev), tudo containerizado com Docker.

## Tecnologias Utilizadas

  * **n8n:** Ferramenta de automação de workflows, usada como o cérebro da aplicação.
  * **PostgreSQL:** Banco de dados relacional para armazenar os dados de clientes, contratos e leituras.
  * **smtp4dev:** Servidor de e-mail falso para testes, permitindo visualizar os e-mails enviados sem a necessidade de um provedor real.
  * **Docker & Docker Compose:** Para criar um ambiente de desenvolvimento consistente e isolado.
  * **Python:** Utilizado no script para geração de dados de exemplo.

## Configuração e Preparação

Antes de iniciar os containers, siga os passos abaixo.

### 1\. Chave de API da OpenAI

O workflow de geração de e-mails utiliza a API da OpenAI. Você precisa adicionar sua chave de API ao arquivo de credenciais do n8n.

  * Abra o arquivo: `containers/n8n/credentials.json`
  * Insira sua chave de API no campo `apiKey`:

<!-- end list -->

```json
{
  "data": {
    "apiKey": "SUA_CHAVE_DE_API_AQUI"
  }
}
```

### 2\. Geração de Dados

Os dados utilizados pela aplicação precisam ser preparados antes da execução.

  * Os dados de **clientes** estão definidos de forma fixa no arquivo `gerar dados/dados/clientes.csv`.
  * Os dados de **contratos** e **leituras** são gerados aleatoriamente.

Para gerar e preparar todos os dados para o n8n, execute o script `preparar_dados.sh` na raiz do projeto:

```bash
./preparar_dados.sh
```

Este script irá:

1.  Executar o `gerar.py` para criar os arquivos `contratos.csv` e `leituras.csv`.
2.  Compactar os três arquivos CSV (`clientes.csv`, `contratos.csv`, `leituras.csv`) em um arquivo `dados_iniciais.zip` dentro da pasta `containers/n8n`. Este arquivo será utilizado pelo n8n para popular o banco de dados.

> **Atenção:** Se desejar modificar os dados dos clientes, é crucial que as alterações sejam feitas em **dois lugares**:
>
> 1.  No arquivo `gerar dados/dados/clientes.csv`.
> 2.  Nos campos correspondentes (e-mails) dentro do arquivo de configuração do smtp4dev: `containers/smtp4dev/config.json`.
>
> Isso garante que o servidor de e-mail reconheça os destinatários para os testes.

## Execução

Com a chave de API e os dados preparados, você pode iniciar a aplicação.

1.  Navegue até o diretório `containers`:
    ```bash
    cd containers
    ```
2.  Inicie todos os serviços com o Docker Compose:
    ```bash
    docker-compose up -d
    ```

**Nota:** O container do n8n possui um delay de inicialização programado em seu `entrypoint.sh`. Ele pode demorar alguns segundos a mais para ficar online, garantindo que o PostgreSQL e o smtp4dev estejam totalmente prontos antes de sua inicialização, evitando problemas de conexão.

## Como Usar (Endpoints dos Workflows)

Após os containers estarem rodando, você pode disparar os workflows do n8n através de chamadas de webhook utilizando `curl` ou qualquer outra ferramenta de sua preferência.

### 1\. Limpar o Banco de Dados

Executa o workflow `limpa_db.json` para apagar todos os dados das tabelas, preparando o ambiente para uma nova carga.

```bash
curl -X GET http://localhost:5678/webhook/limpar_db
```

### 2\. Popular o Banco de Dados

Executa o workflow `popular_db.json`, que descompacta o `dados_iniciais.zip` e insere os dados de clientes, contratos e leituras no PostgreSQL.

```bash
curl -X GET http://localhost:5678/webhook/popular_db
```

### 3\. Analisar Leituras e Gerar E-mails

Executa o workflow principal `gera_emails.json`. Ele lê os dados do banco, encontra as leituras problemáticas e envia os e-mails correspondentes através do smtp4dev SOMENTE para os contratos ativos. É bom notar que dependendo do número de leituras com problemas esse passo pode demorar alguns minutos.

```bash
curl -X GET http://localhost:5678/webhook/gera_emails
```

## Acessando os Serviços

Você pode inspecionar o estado dos serviços e os resultados diretamente no seu navegador:

  * **Dashboard do n8n:** Para visualizar e editar os workflows.

      * URL: **http://localhost:5678**

  * **Caixa de Entrada do smtp4dev:** Para verificar os e-mails que foram gerados e enviados pelos workflows.

      * URL: **http://localhost:3300**