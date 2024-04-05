FROM python:3.11

WORKDIR /code

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

EXPOSE 8000 8080

CMD ["unicorn", "src.main:app", '--reload', "0.0.0.0", "--port", "8000"]