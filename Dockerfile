FROM duyetdev/airflow:1.10.10

COPY dags /usr/local/airflow/dags

COPY /requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt
COPY app app
