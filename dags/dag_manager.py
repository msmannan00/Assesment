import os
from datetime import timedelta

from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
import airflow.utils.dates
from scripts.airflow_manager import *

os.chdir("/usr/local/airflow/dags")

dag_crawler = DAG(
    dag_id='web-crawler-001',
    catchup=False,
    default_args={
        'owner': 'Deep Search Labs',
        'start_date': airflow.utils.dates.days_ago(0)
    },
    schedule_interval='@hourly'
)

dag_analytics = DAG(
    dag_id='web-analytics-001',
    default_args={
        'owner': 'Deep Search Labs',
        'start_date': airflow.utils.dates.days_ago(5)
    },
    schedule_interval=timedelta(days=5)
)


def task_001_invoker():
    onInitializeWebsites()


def task_002_invoker():
    onCrawlWebsites()


def task_003_invoker():
    onAnalyticsHourly()


def task_104_invoker():
    onAnalyticsWeekly()


task_dag_001 = PythonOperator(
    task_id='Fresh.URL.Initializer',
    python_callable=task_001_invoker,
    dag=dag_crawler,
)
task_dag_002 = PythonOperator(
    task_id='URL.Crawler',
    python_callable=task_002_invoker,
    dag=dag_crawler,
)
task_dag_003 = PythonOperator(
    task_id='Analytics.Generator.Hourly',
    python_callable=task_003_invoker,
    dag=dag_crawler,
)

task_dag_001 >> task_dag_002 >> task_dag_003

with dag_analytics:
    task_104_invoker = PythonOperator(
        task_id='Analytics.Generator.Weekly',
        python_callable=task_104_invoker,
        dag=dag_analytics,
    )
