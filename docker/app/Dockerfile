FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install poetry && poetry install
CMD ["poetry", "run", "python", "scripts/hello.py"]