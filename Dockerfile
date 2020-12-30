FROM python:3.9.1

EXPOSE 80
WORKDIR /app

RUN pip install --upgrade pip
#pip freeze > requirements.txt
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

