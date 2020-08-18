FROM python:3.8

WORKDIR /home
ENV TELEGRAM_TOKEN=""
ENV KEY_EGR=""
ENV KEY_BANK_INFO=""

COPY *.txt ./
RUN pip install -U pip && pip install -r requirements.txt && apt update && apt install sqlite3
RUN apt install -y --no-install-recommends locales; rm -rf /var/lib/apt/lists/*; sed -i '/^#.* ru_RU.UTF-8 /s/^#//' /etc/locale.gen; locale-gen
RUN locale -a
COPY *.py ./
COPY createdb.sql ./
COPY *.docx ./
COPY ./handlers/ ./handlers/

ENTRYPOINT ["python", "bot.py"]
