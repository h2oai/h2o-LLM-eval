FROM python:3.10-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

ENV H2O_WAVE_NO_LOG=true

EXPOSE 10101
ENTRYPOINT ["wave", "run", "--no-reload", "llm_eval/app.py"]
