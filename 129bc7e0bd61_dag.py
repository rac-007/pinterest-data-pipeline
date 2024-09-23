# Install the required package
# %pip install apache-airflow
# %pip install apache-airflow-providers-databricks
from airflow import DAG
from airflow.providers.databricks.operators.databricks import DatabricksSubmitRunOperator, DatabricksRunNowOperator
from datetime import datetime, timedelta 

#Define params for Submit Run Operator
notebook_task = {
    'notebook_path': '/Workspace/Users/racjob.2018@gmail.com/clean_s3_data',
}

# COMMAND ----------

default_args = {
    'owner': '129bc7e0bd61',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=2)
}

# COMMAND ----------

with DAG('129bc7e0bd61_dag',
    # should be a datetime format
    start_date=datetime(2024, 8, 23),
    # check out possible intervals, should be a string
    schedule_interval='@daily',
    catchup=False,
    default_args=default_args
    ) as dag:
    opr_submit_run = DatabricksSubmitRunOperator(
        task_id='submit_run',
        databricks_conn_id='databricks_default',
        existing_cluster_id='1108-162752-8okw8dgg',
        notebook_task=notebook_task
    )
    opr_submit_run