from datetime import timedelta

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}
dag = DAG(
    'collect_dag',
    default_args=default_args,
    description='A simple tutorial DAG',
    schedule_interval=None,
    start_date=days_ago(2),
    tags=['vk_api'],
)

BashOperator(
    task_id='collect_task',
    bash_command='python3 /opt/DataMining/Task1/VkPostsCrawler.py 200 itis_kfu '
                 'dm-rg-database.cvjyc3nfgos9.us-east-1.rds.amazonaws.com postgres aws48916011 postgres 5432',
    dag=dag
)
