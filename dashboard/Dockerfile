FROM python:latest

WORKDIR dashboard/

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY  db_utils.py data_cache.py charts.py ./utils/

COPY app.py .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]