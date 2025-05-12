import pandas as pd
from faker import Faker
import random
import os
# Inicializa gerador de dados
fake = Faker('pt_BR')
Faker.seed(42)
random.seed(42)

# Geração dos dados
n = 1000  # número de transações
transacoes = []

for i in range(1, n + 1):
    transacoes.append({
        "id_transacao": i,
        "id_cliente": random.randint(1, 300),
        "data": fake.date_between(start_date='-1y', end_date='today'),
        "valor": round(random.uniform(10.0, 1000.0), 2),
        "categoria": random.choice(["mercado", "eletronico", "vestuario", "farmacia", "restaurante"]),
        "cidade": fake.city()
    })

# Criação do DataFrame
df = pd.DataFrame(transacoes)

# Criar pasta Data/ se não existir
os.makedirs("Data", exist_ok=True)

# Salvando no mesmo diretório do código

clientes_csv_path ="Data/transacoes.csv"
df.to_csv(clientes_csv_path, index=False)



print("✅ Arquivo 'transacoes.csv' criado com sucesso!")
