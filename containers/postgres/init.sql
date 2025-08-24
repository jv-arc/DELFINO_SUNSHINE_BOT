--======================================================================================
--ESTRUTURA DE DB PARA SISTEMA DE MONITORAMENTO DE LEITURAS DE ENERGIA SOLAR
--======================================================================================

--..............................................................................
--CRIACAO DA TABELA DE CLIENTES
--..............................................................................
--Decidi manter os campos essenciais para funcionamento mas com adicao de dados 
--de identificacao, como cpf ou cnpj
--..............................................................................

CREATE TABLE clientes(
    --Campos essenciais definidos no case
    id              SERIAL PRIMARY KEY,
    nome            VARCHAR(100) NOT NULL,

    --endeerco de email para contato
    email           VARCHAR(200) NOT NULL,

    --Melhor identificacao do cliente, podendo ser cpf ou cnpj dependendo do tipo
    --pode ser bem chato usar o db sem isso
    cpf             VARCHAR(14), --para "000.000.000-00"
    cnpj            VARCHAR(18), --para "00.000.000/0000-00"
    tipo            CHAR(1) CHECK (tipo IN ('F', 'J')), --'F' para pessoa fisica e 'J' para pessoa juridica
    
    --Verificacao para garantir que extamente um seja preenchido, cnpj para pessoas juridicas e cpf para fisicas
    CHECK (
        (tipo = 'F' AND cpf IS NOT NULL AND cnpj IS NULL) OR
        (tipo = 'J' AND cnpj IS NOT NULL AND cpf IS NULL) 
    )
);

--..............................................................................
--CRIACAO DA TABELA DE CONTRATOS
--..............................................................................
--Os campos sao aqueles definidos no case.
--..............................................................................
CREATE TABLE contratos(
    id              SERIAL PRIMARY KEY,

    --'fk_' como padrao para chave estrangeira
    fk_cliente      INT NOT NULL, 

    --basta a data para o inicio do contrato
    data_inicio     DATE NOT NULL,

    --talvez seja util outros estados como 'suspenso', mas estes bastam para o case
    status          VARCHAR(7) DEFAULT 'inativo' CHECK (status IN ('ativo', 'inativo')),


    FOREIGN KEY (fk_cliente) REFERENCES clientes(id)
);

--..............................................................................
--CRIACAO DA TABELA DE LEITURAS
--..............................................................................
--Os campos sao aqueles definidos no case.
--..............................................................................
CREATE TABLE leituras(
    --se leituras forem frequentes como em alguns sistemas de monitoramento de
    --energia, SERIAL nao e o suficiente, por isso optei por BIGSERIAL.
    id              BIGSERIAL PRIMARY KEY,

    --'fk_' como padrao para chave estrangeira
    fk_contratos    INT NOT NULL, 

    --diferente da data de inicio a leitura deve ter o timestamp para multiplas 
    --leituras ao longo do dia, mas talvez dependa das regras da empresa
    data_leitura    TIMESTAMP NOT NULL,

    --escolhi 10 digitos com 3 decimais para dar uma boa margem para os valores
    --dependendo da escala de energia produzida pelos clientes esse numero pode
    --ser bem diferente.... 
    --
    --decidi permitir leituras NULL para diferenciar falhas na leitura de 
    --leituras que valem zero.
    valor           DECIMAL(10,3), 

    --idealmente leituras negativas deveriam estar separadas para identificar
    --energia injetada na rede, mas isso foge um pouco do escopo do case

    FOREIGN KEY (fk_contratos) REFERENCES contratos(id)
);
