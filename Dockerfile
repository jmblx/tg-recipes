FROM python:3.11

RUN apt-get -y update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    openssl libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV DB_LITE=sqlite+aiosqlite:///my_base.db \
    TOKEN=6542468672:AAHSLZwJob_o9Rj8pFgdPXG3F190XUXbp8A \
    ADMIN_LIST=1039610272,806605960

RUN mkdir /bot_app

WORKDIR /bot_app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY / .

CMD ["python3", "./app.py"]