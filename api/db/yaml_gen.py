import yaml
from secrets import app_yaml_dict

with open('app.yaml', 'w') as outfile:
    yaml.dump(app_yaml_dict, outfile, default_flow_style=False)