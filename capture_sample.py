import os
import requests
import json

SPTRANS_API_TOKEN = os.environ.get('SPTRANS_API_TOKEN', '5c9d3d50308a3a1c3804a775eb78d2a4fb86beacd9060b02dd824727d29cbc17')
API_URL = 'http://api.olhovivo.sptrans.com.br/v2.1'
OUTPUT_FILE = 'sample_data.json'

def main():
    """Autentica, busca os dados uma vez e salva em um arquivo."""
    session = requests.Session()
    print("Tentando autenticar na API da SPTrans...")

    if SPTRANS_API_TOKEN == 'SEU_TOKEN_AQUI':
        print("ERRO: Por favor, defina seu token na variável de ambiente SPTRANS_API_TOKEN.")
        return

    auth_url = f"{API_URL}/Login/Autenticar?token={SPTRANS_API_TOKEN}"
    auth_response = session.post(auth_url)

    if auth_response.status_code != 200 or not auth_response.text.lower() == 'true':
        print(f"Falha na autenticação: {auth_response.status_code} - {auth_response.text}")
        return
    print("Autenticação bem-sucedida.")

    print("Buscando posições dos veículos...")
    posicao_url = f"{API_URL}/Posicao"
    posicao_response = session.get(posicao_url)
    if posicao_response.status_code != 200:
        print(f"Falha ao buscar posições: {posicao_response.status_code}")
        return

    dados = posicao_response.json()
    if not dados.get('l'):
         print("API não retornou dados de veículos. Tente novamente.")
         return

    print("Dados de posição capturados com sucesso.")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)
    print(f"Amostra de dados salva com sucesso no arquivo '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    main()