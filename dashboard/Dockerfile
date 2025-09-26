FROM python:3.11-slim

WORKDIR dashboard/

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    apt-transport-https \
    unixodbc \
    unixodbc-dev && \
    curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.gpg && \
    curl https://packages.microsoft.com/config/debian/11/prod.list | tee /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
        msodbcsql18 \
        mssql-tools18 

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY db_utils.py data_cache.py charts.py app.py ./

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501"]