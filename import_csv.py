import psycopg2
import csv
import os

# Configuração da conexão com o PostgreSQL
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME", "cbo_db"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", "postgres"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", 5432))
)

cur = conn.cursor()

# Caminho do arquivo CSV dentro do contêiner
csv_file = "/app/cbo.csv" 

# Lendo e inserindo dados no banco
with open(csv_file, mode="r", encoding="ISO-8859-1") as file:
    reader = csv.reader(file, delimiter=";")
    next(reader)  # Pula o cabeçalho

    for row in reader:
        codigo, titulo = row
        cur.execute(
            "INSERT INTO cbo (code, title, description) VALUES (%s, %s, %s) ON CONFLICT (code) DO NOTHING",
            (codigo, titulo, "")
        )

# Commit e fechamento da conexão
conn.commit()
cur.close()
conn.close()

print("Dados importados com sucesso!")
