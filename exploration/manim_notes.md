# Manim 学习笔记

## 项目简介

**Manim** (Mathematical Animation Engine) 是一个用于创建解释性数学视频的动画引擎。最初由 Grant Sanderson (3Blue1Brown) 开发，现在有社区维护版本 (ManimCE)。

核心定位：
- 程序化创建精确的数学动画
- 支持 LaTeX 数学公式渲染
- 生成高质量视频输出
- 适合制作教育视频和可视化

## 核心架构

### 模块结构

```
manim/
├── animation/      # 动画系统
│   ├── animation.py
│   ├── creation.py
│   ├── fading.py
│   ├── movement.py
│   ├── rotation.py
│   ├── transform.py
│   └── updaters/
├── camera/         # 摄像机
│   ├── camera.py
│   ├── moving_camera.py
│   └── three_d_camera.py
├── mobject/        # 数学对象
│   ├── geometry/   # 几何图形
│   ├── graphing/   # 图表函数
│   ├── three_d/    # 3D对象
│   ├── text/       # 文本和公式
│   ├── svg/        # SVG支持
│   └── types/      # 类型系统
├── scene/          # 场景系统
│   └── scene.py
├── renderer/       # 渲染引擎
│   └── cairo_renderer.py
└── utils/          # 工具函数
    ├── color.py
    ├── rate_functions.py
    └── bezier.py
```

## 核心概念

### 1. Mobject (Mathematical Object)

所有可见对象的基类：

```python
from manim import *

# 基本图形
circle = Circle()
square = Square()
line = Line()

# 文本和公式
text = Text("Hello")
formula = MathTex(r"E = mc^2")

# 图表
axes = Axes()
graph = axes.plot(lambda x: x**2)

# 3D对象
sphere = Sphere()
cube = Cube()
```

### 2. Scene (场景)

动画的容器：

```python
class MyAnimation(Scene):
    def construct(self):
        # 添加对象到场景
        circle = Circle()
        self.add(circle)
        
        # 播放动画
        self.play(Create(circle))
        self.play(circle.animate.scale(2))
        self.play(FadeOut(circle))
        
        # 等待
        self.wait(1)
```

### 3. Animation (动画)

变换效果：

```python
# 创建动画
self.play(Create(circle))

# 变换动画
self.play(Transform(square, circle))

# 移动动画
self.play(circle.animate.shift(RIGHT * 2))

# 旋转动画
self.play(circle.animate.rotate(PI / 4))

# 淡入淡出
self.play(FadeIn(circle))
self.play(FadeOut(circle))
```

## 常用功能

### 几何图形

```python
# 基本形状
circle = Circle(radius=1.0, color=BLUE)
square = Square(side_length=2.0)
triangle = Triangle()
rectangle = Rectangle(width=3, height=2)

# 多边形
polygon = Polygon([0, 0, 0], [1, 0, 0], [1, 1, 0])

# 曲线
arc = Arc(radius=1, start_angle=0, angle=PI)
curve = ParametricFunction(lambda t: np.array([t, t**2, 0]))
```

### 文本和公式

```python
# 纯文本
text = Text("Hello, Manim!", font_size=48)

# LaTeX 公式
formula = MathTex(r"\int_0^1 x^2 dx = \frac{1}{3}")

# 代码高亮
code = Code("print('hello')", language="python")
```

### 图表

```python
# 坐标系
axes = Axes(
    x_range=[-3, 3],
    y_range=[-2, 2],
    axis_config={"include_numbers": True}
)

# 函数图像
graph = axes.plot(lambda x: np.sin(x), color=BLUE)

# 标签
label = axes.get_graph_label(graph, "sin(x)")
```

### 3D场景

```python
class ThreeDScene(ThreeDScene):
    def construct(self):
        # 3D对象
        sphere = Sphere(radius=2)
        cube = Cube()
        
        # 设置摄像机
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
        
        # 旋转摄像机
        self.begin_ambient_camera_rotation(rate=0.1)
```

## 动画原理

### 时间函数 (Rate Functions)

控制动画的加速度：

```python
# 线性
self.play(circle.animate.shift(RIGHT * 2), rate_func=linear)

# 缓入缓出
self.play(circle.animate.shift(RIGHT * 2), rate_func=smooth)

# 弹性
self.play(circle.animate.shift(RIGHT * 2), rate_func=there_and_back)

# 自定义
def custom_rate(t):
    return t**2

self.play(circle.animate.shift(RIGHT * 2), rate_func=custom_rate)
```

### Updaters (更新器)

实时更新对象：

```python
# 定义更新器
def update_circle(circle, dt):
    circle.rotate(PI * dt)

# 添加更新器
circle.add_updater(update_circle)

# 移除更新器
circle.remove_updater(update_circle)

# 基于时间的更新
self.play(circle.animate.shift(RIGHT * 2), run_time=2)
```

## 渲染输出

### 命令行参数

```bash
# 预览（低质量）
manim -pql my_scene.py MyAnimation

# 高质量
manim -pqh my_scene.py MyAnimation

# 4K质量
manim -pqk my_scene.py MyAnimation

# 指定输出格式
manim -pql my_scene.py MyAnimation --format gif
manim -pql my_scene.py MyAnimation --format webm
```

### 质量选项

- `-ql`: 480p, 快速
- `-qm`: 720p, 中等
- `-qh`: 1080p, 高质量
- `-qk`: 4K, 最高质量

## 与涌现实验的结合

### 1. 可视化细胞自动机

```python
class LangtonsAnt(Scene):
    def construct(self):
        # 创建网格
        grid = IntegerMatrix([[0] * 50 for _ in range(50)])
        
        # 动画展示朗顿蚂蚁
        ant = Dot().move_to(grid.get_center())
        
        for _ in range(1000):
            # 更新规则
            self.play(ant.animate.move_to(new_position), run_time=0.01)
```

### 2. 可视化分形

```python
class MandelbrotSet(Scene):
    def construct(self):
        # 创建 Mandelbrot 集
        plane = ComplexPlane()
        mandelbrot = ImageMobject(mandelbrot_image())
        
        self.play(FadeIn(plane))
        self.play(FadeIn(mandelbrot))
        
        # 缩放动画
        self.play(mandelbrot.animate.scale(0.5), run_time=2)
```

### 3. 可视化相变

```python
class IsingModel(Scene):
    def construct(self):
        # Ising 模型网格
        grid = VGroup(*[
            Square() for _ in range(100)
        ]).arrange_in_grid(10, 10)
        
        # 温度动画
        for T in np.linspace(0.1, 4.0, 100):
            # 更新网格颜色
            self.play(UpdateFromFunc(grid, update_grid), run_time=0.1)
```

## 高级功能

### 组合动画

```python
# 并行动画
self.play(
    circle.animate.shift(LEFT),
    square.animate.shift(RIGHT),
    run_time=2
)

# 序列动画
self.play(Succession(
    Create(circle),
    circle.animate.scale(2),
    FadeOut(circle)
))

# 延迟动画
self.play(LaggedStart(
    *[FadeIn(dot) for dot in dots],
    lag_ratio=0.1
))
```

### Group 和 VGroup

```python
# 组织多个对象
group = VGroup(circle, square, triangle)
group.arrange(RIGHT)

# 批量操作
group.set_color(RED)
group.shift(UP)

# 添加到场景
self.play(Create(group))
```

## 性能优化

### 1. 降低帧率

```python
# 减少帧数
config.frame_rate = 30  # 默认 60
```

### 2. 使用缓存

```python
# 缓存 Tex 对象
config.tex_template = TexTemplate()
```

### 3. 预计算

```python
# 预生成帧
frames = [compute_frame(i) for i in range(1000)]
self.play(FadeIn(ImageMobject(frames[0])))
```

## 实际应用示例

### 演示几何定理

```python
class PythagoreanTheorem(Scene):
    def construct(self):
        # 创建直角三角形
        triangle = Polygon(
            ORIGIN, RIGHT * 3, UP * 4,
            color=WHITE
        )
        
        # 标注边
        a_label = MathTex("a").next_to(triangle, DOWN)
        b_label = MathTex("b").next_to(triangle, LEFT)
        c_label = MathTex("c").next_to(triangle, UP + RIGHT)
        
        # 创建正方形
        square_a = Square(side_length=3).next_to(triangle, DOWN)
        square_b = Square(side_length=4).next_to(triangle, LEFT)
        
        # 公式
        formula = MathTex("a^2 + b^2 = c^2")
        
        self.play(Create(triangle))
        self.play(Write(formula))
```

### 演示物理过程

```python
class PendulumSimulation(Scene):
    def construct(self):
        # 创建单摆
        pivot = Dot(UP * 2)
        bob = Dot(RIGHT * 2 + DOWN * 2, radius=0.2, color=RED)
        rod = Line(pivot.get_center(), bob.get_center())
        
        # 添加更新器
        def update_pendulum(mob, dt):
            # 物理模拟
            angle = 0.5 * np.sin(2 * dt)
            bob.move_to(pivot.get_center() + 
                        np.array([np.sin(angle), -np.cos(angle), 0]) * 3)
        
        bob.add_updater(update_pendulum)
        self.add(pivot, rod, bob)
        self.wait(10)
```

## 安装和配置

### 安装

```bash
# 使用 pip
pip install manim

# 使用 conda
conda install -c conda-forge manim

# 安装依赖（LaTeX）
# Windows: https://miktex.org/
# macOS: brew install --cask mactex
# Linux: sudo apt install texlive-full
```

### 配置文件

```python
# manim.cfg
[CLI]
output_file = my_animation
media_dir = ./media
frame_rate = 60
pixel_height = 1080
pixel_width = 1920
```

## 与其他工具对比

| 特性 | Manim | Matplotlib | Blender | D3.js |
|------|-------|------------|---------|-------|
| 动画 | ✅ | ⚠️ | ✅ | ✅ |
| 数学公式 | ✅ | ✅ | ❌ | ❌ |
| 编程接口 | Python | Python | Python | JS |
| 渲染质量 | 高 | 中 | 极高 | 高 |
| 学习曲线 | 中 | 低 | 高 | 高 |
| 视频输出 | ✅ | ❌ | ✅ | ❌ |

## 参考资源

- 官方文档：https://docs.manim.community/
- GitHub：https://github.com/ManimCommunity/manim
- 3Blue1Brown：https://www.3blue1brown.com/
- 示例库：https://docs.manim.community/en/stable/examples.html
- Reddit：https://www.reddit.com/r/manim/
- Discord：https://manim.community/discord/

## 下一步探索

1. **为涌现实验创建动画**
   - 朗顿蚂蚁的路径可视化
   - 生命游戏的演化过程
   - Boids 群集行为的动态展示

2. **教学视频制作**
   - 制作"什么是涌现"解释视频
   - 可视化复杂系统概念

3. **与 JAX 集成**
   - 用 Manim 可视化 JAX 计算过程
   - 创建神经网络训练动画

4. **高级技术**
   - 自定义 Mobject
   - OpenGL 着色器
   - 交互式场景