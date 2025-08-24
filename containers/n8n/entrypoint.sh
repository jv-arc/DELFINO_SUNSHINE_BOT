#!/bin/sh

echo "Esperando 5 segundos antes de importar.."
sleep 5

echo "Importando credentials..."
n8n import:credentials --input=/home/credentials.json

echo "Importando workflows..."
n8n import:workflow --separate --input=/home/node/workflows/

echo "Ativando todos workflows..."
n8n update:workflow --all --active=true

echo "Workflows importados! Bora começar!"
n8n start