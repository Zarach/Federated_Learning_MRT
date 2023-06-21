from clearml import Task

client_number = 0

task = Task.init(project_name='FL_MRT', task_name=f'Client {client_number}')
task.execute_remotely(queue_name='default', clone=False, exit_process=True)


import client

client.start_client("127.0.0.1")