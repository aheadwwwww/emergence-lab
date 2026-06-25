import os
dirs = [
    'emergence_lab/core',
    'emergence_lab/models',
    'emergence_lab/experiments',
    'emergence_lab/examples',
]
for d in dirs:
    os.makedirs(d, exist_ok=True)
    # Create __init__.py
    init_path = os.path.join(d, '__init__.py')
    if not os.path.exists(init_path):
        with open(init_path, 'w') as f:
            f.write('')
print('Created directories:', dirs)
