from jinja2 import Environment, FileSystemLoader

# Create the Jinja2 environment
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('dms_endpoints.j2')

# List of servers
servers = [
    {'server_name': 'FirstInstance', 'ip_address': '192.168.1.1'},
    {'server_name': 'SecondInstance', 'ip_address': '192.168.1.2'},
    {'server_name': 'ThirdInstance', 'ip_address': '192.168.1.3'},
]

# Render the template with the servers variable
rendered_template = template.render(servers=servers)

# Save or print the rendered CloudFormation YAML
print(rendered_template)
