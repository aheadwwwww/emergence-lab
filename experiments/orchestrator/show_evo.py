import json
d = json.load(open(r'D:\emergence_experiments\evolution_results.json'))
for k, v in d.items():
    print('{}: score={}, params={}'.format(k, v['best_score'], v['best_params']))
