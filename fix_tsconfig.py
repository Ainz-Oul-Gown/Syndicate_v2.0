import json

with open('tsconfig.json', 'r') as f:
    config = json.load(f)

config['exclude'] = ['supabase/functions', 'node_modules', 'dist']

with open('tsconfig.json', 'w') as f:
    json.dump(config, f, indent=2)
