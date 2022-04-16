FROM python:3.9-slim

WORKDIR /spotitubot

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "spotitubot/main.py" ]
