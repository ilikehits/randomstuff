FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install discord.py-self
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
