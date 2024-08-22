# pip install ansible-runner
import ansible_runner


def my_status_handler(data, runner_config):
    print(data)


r = ansible_runner.run(private_data_dir='/etc/ansible', playbook='playbook1.yml', status_handler=my_status_handler)