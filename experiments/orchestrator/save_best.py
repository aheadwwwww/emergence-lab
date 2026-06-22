"""保存进化找到的最佳参数可视化"""
from registry import REGISTRY, OUTPUT_DIR
import json

# 加载进化结果
with open(OUTPUT_DIR / 'evolution_results.json') as f:
    results = json.load(f)

print('Best parameter visualizations:\n')

for exp_name, data in results.items():
    exp = REGISTRY.get(exp_name)
    if not exp:
        continue
    
    params = {}
    for k, v in data['best_params'].items():
        try:
            if k in ('Du', 'Dv', 'F', 'k', 'density'):
                params[k] = float(v)
            elif k in ('size', 'steps', 'drops', 'width', 'height', 'rule'):
                params[k] = int(v)
            else:
                params[k] = v
        except:
            params[k] = v
    
    # 运行
    print(f'{exp_name}: params={params}')
    try:
        result = exp.run(params)
        img = exp.visualize(result)
        
        # 保存
        path = OUTPUT_DIR / f'best_{exp_name}.png'
        img.save(path)
        print(f'  Saved: {path}')
        print(f'  Score: {data["best_score"]}')
    except Exception as e:
        print(f'  Error: {e}')
    print()
