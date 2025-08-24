#=============================================
# SCRIPT PARA GERAR DADOS DA APLICACAO
#=============================================

import csv
import random
from datetime import datetime, timedelta
import numpy as np








#.........CONFIGURACAO GERAL..............

#Arquivos de Entrada/Saida
CLIENTES_FILE = './dados/clientes.csv'
CONTRATOS_FILE = './dados/contratos.csv'
LEITURAS_FILE = './dados/leituras.csv'

# Periodo para a data de inicio dos contratos
START_YEAR_CONTRATO = 2022
END_YEAR_CONTRATO = 2025

# Regras para pessoa fisica (F)
MIN_CONTRATOS_F = 1
MAX_CONTRATOS_F = 2
ACTIVE_CONTRATOS_F = 1  # Numero exato de contratos ativos

# Regras para pessoa juridica (J)
MIN_CONTRATOS_J = 1
MAX_CONTRATOS_J = 6
MIN_ACTIVE_CONTRATOS_J = 1  # Minimo de contratos ativos
MAX_ACTIVE_CONTRATOS_J = 3  # Maximo de contratos ativos

# Total de leituras a serem geradas por tipo de cliente
NF_LEITURAS = 3000      # Total para pessoa fisica
NJ_LEITURAS = 6000      # Total para pessoa juridica

# Numero de leituras com falha
NF_FALHA = 10           # Falhas para pessoa fisica
NJ_FALHA = 20           # Falhas para pessoa juridica

# Numero de outliers
NF_OUTLIERS = 20        # Outliers para Pessoa fisica
NJ_OUTLIERS = 40        # Outliers para pessoa juridica

# Parametros da distribuicao gaussiana
MEAN_F = 50 # media pessoas fisicas
STD_F = 10  # desvio pessoas fisicas
MEAN_J = 70 # media pessoas juridicas
STD_J = 15  # media pessoas juridicas









#.........FUNCOES PARA GERACAO DE CONTRATOS............

def generate_random_date(start_year, end_year):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    
    random_date = start_date + timedelta(days=random_days)
    return random_date.strftime('%Y-%m-%d')

def generate_contracts_for_client(client_id, client_type, contract_id_counter):
    contracts = []
    
    if client_type == 'F':
        num_contracts = random.randint(MIN_CONTRATOS_F, MAX_CONTRATOS_F)
        active_count = ACTIVE_CONTRATOS_F
    else:  # client_type == 'J'
        num_contracts = random.randint(MIN_CONTRATOS_J, MAX_CONTRATOS_J)
        max_active = min(MAX_ACTIVE_CONTRATOS_J, num_contracts)
        min_active = min(MIN_ACTIVE_CONTRATOS_J, max_active)
        active_count = random.randint(min_active, max_active)
    
    status_list = ['ativo'] * active_count + ['inativo'] * (num_contracts - active_count)
    random.shuffle(status_list)
    
    for status in status_list:
        contract = {
            'id': contract_id_counter[0],
            'fk_cliente': client_id,
            'data_inicio': generate_random_date(START_YEAR_CONTRATO, END_YEAR_CONTRATO),
            'status': status
        }
        contracts.append(contract)
        contract_id_counter[0] += 1
    
    return contracts

def generate_contratos_csv():
    print("-" * 50)
    print("Iniciando a geracao de contratos...")
    
    all_contracts = []
    contract_id_counter = [1]
    
    try:
        with open(CLIENTES_FILE, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            clients = list(reader)
        
        print(f"Encontrados {len(clients)} clientes em {CLIENTES_FILE}")
        
        for client in clients:
            client_id = int(client['id'])
            client_type = client['tipo']
            contracts = generate_contracts_for_client(client_id, client_type, contract_id_counter)
            all_contracts.extend(contracts)
        
        with open(CONTRATOS_FILE, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['id', 'fk_cliente', 'data_inicio', 'status']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_contracts)
        
        print(f"Gerados {len(all_contracts)} contratos em {CONTRATOS_FILE}")
        
    except FileNotFoundError:
        print(f"Erro: Arquivo de entrada '{CLIENTES_FILE}' nao encontrado!")
        raise
    except Exception as e:
        print(f"Erro inesperado ao gerar contratos: {e}")
        raise







#..............FUNCOES PARA GERACAO DE LEITURAS.....................

def load_data_for_readings():
    clientes = {}
    with open(CLIENTES_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            clientes[int(row['id'])] = row['tipo']
    
    contratos = []
    with open(CONTRATOS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            contratos.append({
                'id': int(row['id']),
                'fk_cliente': int(row['fk_cliente']),
                'data_inicio': datetime.strptime(row['data_inicio'], '%Y-%m-%d'),
                'status': row['status']
            })
    
    return clientes, contratos

def generate_gaussian_with_outliers_and_nulls(n_total, n_outliers, n_falha, mean, std):
    n_normal = n_total - n_outliers - n_falha
    if n_normal < 0:
        raise ValueError("O numero total de leituras e menor que a soma de outliers e falhas.")
        
    normal_data = np.random.normal(loc=mean, scale=std, size=n_normal)
    normal_data = np.clip(normal_data, 0, None)
    
    outliers = []
    while len(outliers) < n_outliers:
        val = np.random.normal(loc=mean, scale=std * 4)
        z_score = abs((val - mean) / std)
        if z_score >= 3 and val >= 0:
            outliers.append(val)
    
    all_values = list(normal_data) + outliers + [None] * n_falha
    random.shuffle(all_values)
    
    formatted_values = []
    for val in all_values:
        if val is None:
            formatted_values.append(None)
        else:
            formatted_val = f"{val:.3f}"
            if len(formatted_val.replace('.', '')) > 10:
                formatted_val = f"{val:.0f}"[:7] + ".000"
            formatted_values.append(formatted_val)
    
    return formatted_values

def random_datetime_after(start_date):
    delta_days = random.randint(1, 365 * 3)
    delta_seconds = random.randint(0, 86399)
    return start_date + timedelta(days=delta_days, seconds=delta_seconds)

def generate_leituras_csv():
    print("-" * 50)
    print("Iniciando a geracao de leituras...")
    
    try:
        clientes, contratos = load_data_for_readings()
        
        F_contracts = [c for c in contratos if clientes.get(c['fk_cliente']) == 'F']
        J_contracts = [c for c in contratos if clientes.get(c['fk_cliente']) == 'J']
        
        print(f"Encontrados {len(F_contracts)} contratos para pessoa fisica")
        print(f"Encontrados {len(J_contracts)} contratos para pessoa Juridica")
        
        vals_F = generate_gaussian_with_outliers_and_nulls(
            NF_LEITURAS, NF_OUTLIERS, NF_FALHA, MEAN_F, STD_F
        )
        vals_J = generate_gaussian_with_outliers_and_nulls(
            NJ_LEITURAS, NJ_OUTLIERS, NJ_FALHA, MEAN_J, STD_J
        )
        
        leituras = []
        id_counter = 1
        
        # Processa leituras tipo F
        if not F_contracts and vals_F:
            print("Aviso: Nao ha contratos do tipo 'F' para associar as leituras. Leituras 'F' serao puladas.")
        else:
            for val in vals_F:
                contrato = random.choice(F_contracts)
                data_leitura = random_datetime_after(contrato['data_inicio'])
                leituras.append({
                    'id': id_counter,
                    'fk_contratos': contrato['id'],
                    'data_leitura': data_leitura.strftime('%Y-%m-%d %H:%M:%S'),
                    'valor': val
                })
                id_counter += 1

        # Processa leituras tipo J
        if not J_contracts and vals_J:
            print("Aviso: Nao ha contratos do tipo 'J' para associar as leituras. Leituras 'J' serao puladas.")
        else:
            for val in vals_J:
                contrato = random.choice(J_contracts)
                data_leitura = random_datetime_after(contrato['data_inicio'])
                leituras.append({
                    'id': id_counter,
                    'fk_contratos': contrato['id'],
                    'data_leitura': data_leitura.strftime('%Y-%m-%d %H:%M:%S'),
                    'valor': val
                })
                id_counter += 1

        with open(LEITURAS_FILE, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['id', 'fk_contratos', 'data_leitura', 'valor']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(leituras)
        
        print(f"Geradas {len(leituras)} leituras totais em {LEITURAS_FILE}")

    except FileNotFoundError as e:
        print(f"Erro: Arquivo necessario nao encontrado - {e}. Certifique-se de que {CONTRATOS_FILE} foi gerado.")
        raise
    except Exception as e:
        print(f"Erro inesperado ao gerar leituras: {e}")
        raise





#...................EXECUCAO PRINCIPAL..........................

if __name__ == "__main__":
    try:
        # Etapa 1: Gerar o arquivo de contratos
        generate_contratos_csv()
        
        # Etapa 2: Gerar o arquivo de leituras usando o arquivo de contratos
        generate_leituras_csv()
        
        print("-" * 50)
        print("Processo concluído com sucesso!")
        
    except Exception as e:
        print("-" * 50)
        print(f"Ocorreu um erro e o processo foi interrompido.")
