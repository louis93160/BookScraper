from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

#Définition des arguments par défaut du DAG
default_args = {
    "owner" : "user",
    "depends_on_past" : False,
    "start_date" : datetime(2024, 1, 1),
    "email_on_failure" : False,
    "email_on_retry" : False,
    "retries" : 1,
    "retry_delay" : timedelta(minutes=5)
}

#Définition du DAG
dag = DAG(
    "monthly_script_execution",
    default_args = default_args,
    description = "Exécute les scriptis Python une fois par mois à 7h",
    schedule_interval = "0 7 1 **",
    catchup = False
)

#Définition des tâches
task_1 = BashOperator(
    task_id = "run_books_extract.py",
    bash_command = "Python3 /home/louis/BookScraper/etl/books_extract.py",
    dag = dag
)

task_2 = BashOperator(
    task_id = "run_books_transformation.py",
    bash_command = "Python3 /home/louis/BookScraper/etl/books_transformation.py",
    dag = dag
)

task_3 = BashOperator(
    task_id = "run_books_load.py",
    bash_command = "Python3 /home/louis/BookScraper/etl/books_load.py",
    dag = dag
)

#Définition de l'odre d'éxécution des tâches
task_1 >> task_2 >> task_3