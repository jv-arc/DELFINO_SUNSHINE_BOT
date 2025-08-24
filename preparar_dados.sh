#!/bin/bash

# Script para gerar dados e criar zip com inicializacao do db

set -e  # Para o script se algum comando falhar

echo "Executando gerar.py..."
cd "gerar dados"
python3 gerar.py

echo "Criando zip dos dados..."
zip -r dados_iniciais.zip dados/
cd ..

echo "Movendo zip para containers/n8n..."
mv "gerar dados/dados_iniciais.zip" "containers/n8n/dados_iniciais.zip"

echo "Concluido! Pode rodar o docker compose"
