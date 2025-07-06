import os
import time
import requests
from kafka import KafkaProducer
import json

SPTRANS_API_TOKEN = os.environ.get('SPTRANS_API_TOKEN', 'SEU_TOKEN_AQUI')
KAFKA_SERVER = 'localhost:9092'
KAFKA_TOPIC = 'posicoes_onibus'

try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_SERVER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        api_version=(0, 10, 1)
    )
    print("Producer Kafka inicializado com sucesso.")
except Exception as e:
    print(f"Erro ao inicializar o Producer Kafka: {e}")
    exit()

API_URL = 'http://api.olhovivo.sptrans.com.br/v2.1'

def autenticar_api(session, token):
    """Autentica na API usando a sessão fornecida."""
    url = f"{API_URL}/Login/Autenticar?token={token}"
    response = session.post(url)
    if response.status_code == 200 and response.cookies.get('apiCredentials'):
        print("Autenticação na API bem-sucedida.")
        return True
    else:
        print(f"Falha na autenticação: {response.status_code} - {response.text}")
        return False

def buscar_posicoes(session):
    url = f"{API_URL}/Posicao"
    try:
        response = session.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar posições: {e}")
        return None

def main():
    session = requests.Session()

    if not autenticar_api(session, SPTRANS_API_TOKEN):
        return

    print(f"Iniciando a captura de dados para o tópico: {KAFKA_TOPIC}")

    while True:
        posicoes = buscar_posicoes(session)

        if posicoes and 'l' in posicoes:
            total_veiculos = 0
            for linha in posicoes['l']:
                if 'vs' in linha:
                    for veiculo in linha['vs']:
                        mensagem = {
                            'timestamp_captura': posicoes.get('hr'),
                            'id_linha': linha.get('cl'),
                            'letreiro_ida': linha.get('sl'),
                            'letreiro_volta': linha.get('lt0'),
                            'destino_principal': linha.get('lt1'),
                            'prefixo_veiculo': veiculo.get('p'),
                            'latitude': veiculo.get('py'),
                            'longitude': veiculo.get('px'),
                            'timestamp_veiculo': veiculo.get('ta'),
                            'acessivel': veiculo.get('a', False)
                        }
                        producer.send(KAFKA_TOPIC, mensagem)
                        total_veiculos += 1

            producer.flush()
            print(f"Enviados dados de {total_veiculos} veículos para o Kafka.")
        else:
            print("Nenhum dado de veículo recebido da API. Verificando autenticação novamente...")
            autenticar_api(session, SPTRANS_API_TOKEN)

        time.sleep(60)

if __name__ == "__main__":
    main()