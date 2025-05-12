import pandas as pd
from faker import Faker
import random
import os

# Inicializar gerador de dados
fake = Faker('pt_BR')
random.seed(42)
Faker.seed(42)

# Criar dados de clientes
num_clientes = 300
clientes = []

for i in range(1, num_clientes + 1):
    clientes.append({
        "id_cliente": i,
        "nome": fake.name(),
        "idade": random.randint(18, 70),
        "email": fake.email(),
        "estado": fake.estado_sigla()
    })

df_clientes = pd.DataFrame(clientes)

# Criar pasta Data/ se não existir
os.makedirs("Data", exist_ok=True)

# Salvar CSV na pasta
clientes_csv_path = "Data/clientes.csv"
df_clientes.to_csv(clientes_csv_path, index=False)

print(f"✅ Arquivo salvo com sucesso em: {clientes_csv_path}")
