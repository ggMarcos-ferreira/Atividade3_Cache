# Usando a imagem oficial do Python
FROM python:3.9

# Definindo o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copiando os arquivos do projeto para dentro do contêiner
COPY . .

# Instalando as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expondo a porta 5000 (onde a API Flask rodará)
EXPOSE 5000

# Definindo o comando para rodar a aplicação
CMD ["python", "app.py"]
