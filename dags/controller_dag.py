import os

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago

args = {
    'owner': 'Deep Search Labs',
    'start_date': days_ago(1)
}

dag = DAG(
    dag_id='crawler_executer',
    default_args=args,
    schedule_interval='@daily'
)

bash_task_1 = BashOperator(
    task_id='bash_task',
    bash_command='python app/main.py',
    dag=dag
)


args = {
    'owner': 'Deep Search Labs',
    'start_date': days_ago(6)
}

dag = DAG(
    dag_id='crawler_analysis',
    default_args=args,
    schedule_interval='@daily'
)

bash_task_2 = BashOperator(
    task_id='bash_task',
    bash_command='python app/analytics.py',
    dag=dag
)

print(os.listdir("app"), flush=True)
