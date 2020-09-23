import yaml

data = dict(
    runtime = 'python38',
    instance_class = 'B2',
    
    basic_scaling = dict(
        max_instances = 10,
        idle_timeout = '5m',
    ),
    vpc_access_connector = dict(
        name = "***REMOVED***"
    )
)

with open('app.yaml', 'w') as outfile:
    yaml.dump(data, outfile, default_flow_style=False)