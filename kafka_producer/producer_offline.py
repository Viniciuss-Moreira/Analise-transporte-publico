import time
from kafka import KafkaProducer
import json
import random
import pathlib

# --- Configurações ---
KAFKA_SERVER = 'localhost:9092'
KAFKA_TOPIC = 'posicoes_onibus'

# Constrói o caminho absoluto para o arquivo de dados
PROJECT_ROOT = pathlib.Path(__file__).parent.parent
SAMPLE_DATA_FILE = PROJECT_ROOT / 'sample_data.json'

def main():
    """Lê dados de um arquivo JSON e os simula como um stream para o Kafka."""

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_SERVER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    print("Producer Offline inicializado. Lendo do arquivo de amostra...")

    try:
        with open(SAMPLE_DATA_FILE, 'r', encoding='utf-8') as f:
            posicoes = json.load(f)
    except FileNotFoundError:
        print(f"Erro: Arquivo de amostra '{SAMPLE_DATA_FILE}' não encontrado.")
        print("Por favor, execute o script 'capture_sample.py' primeiro.")
        return

    if not posicoes or 'l' not in posicoes:
        print("Arquivo de amostra está vazio ou em formato incorreto.")
        return

    todos_veiculos = []
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
                todos_veiculos.append(mensagem)

    if not todos_veiculos:
        print("Nenhum veículo encontrado no arquivo de amostra.")
        return

    print(f"{len(todos_veiculos)} veículos de amostra carregados. Iniciando simulação...")

    while True:
        veiculo_aleatorio = random.choice(todos_veiculos)
        producer.send(KAFKA_TOPIC, veiculo_aleatorio)
        print(f"Enviado veículo simulado: {veiculo_aleatorio['prefixo_veiculo']}")
        time.sleep(random.uniform(0.2, 1.5))

if __name__ == "__main__":
    main()