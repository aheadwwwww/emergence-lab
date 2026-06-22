from registry import REGISTRY, TurmitesExperiment
import time

# 测试 Turmites
exp = TurmitesExperiment()
params = exp.generate_params()
print('Params:', params)

start = time.time()
result = exp.run(params)
elapsed = time.time() - start

print('Done:', exp.describe(params, result))
print('Elapsed:', elapsed, 's')
print('Grid shape:', result['grid'].shape)

# 保存图片
img = exp.visualize(result)
path = exp.save_image(img)
print('Image saved:', path)

# 显示注册表
print('\nAll experiments:', list(REGISTRY.keys()))