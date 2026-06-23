"""
NetworkX 网络分析模块 — 用图论分析涌现实验结果

将网格/粒子系统映射到图结构，计算复杂网络指标，
揭示实验中隐藏的结构特性（磁畴、群落、级联等）。

用法示例：
    from network_analysis import analyze_phase_domains, get_network_report
    report = get_network_report('phase_transitions', result)
"""

import numpy as np
import networkx as nx
from collections import Counter

# ============================================================
# 1. 相变（Ising）模型 — 磁畴分析
# ============================================================

def extract_ising_domains(grid: np.ndarray) -> list:
    """
    从 Ising 模型网格中提取磁性域（同向自旋的连通分量）。

    返回: 每个域的 (size, spin_value, [(i,j)...]) 列表，按大小降序。
    """
    size = len(grid)
    visited = np.zeros((size, size), dtype=bool)
    domains = []

    for i in range(size):
        for j in range(size):
            if visited[i, j]:
                continue
            spin = grid[i, j]
            stack = [(i, j)]
            visited[i, j] = True
            cells = []
            while stack:
                ci, cj = stack.pop()
                cells.append((ci, cj))
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ni, nj = ci + di, cj + dj
                    if 0 <= ni < size and 0 <= nj < size and not visited[ni, nj] and grid[ni, nj] == spin:
                        visited[ni, nj] = True
                        stack.append((ni, nj))
            if len(cells) > 1:  # 单格点噪声不记入域
                domains.append((len(cells), spin, cells))

    domains.sort(reverse=True, key=lambda x: x[0])
    return domains


def analyze_phase_domains(grid: np.ndarray) -> dict:
    """
    分析 Ising 模型的磁畴网络特性。

    返回包含域统计、连通性指标、幂律拟合信息的字典。
    """
    domains = extract_ising_domains(grid)
    sizes = [d[0] for d in domains]
    spins = [d[1] for d in domains]

    if not sizes:
        return {"error": "no domains found"}

    # 构建图：域为节点，相邻域之间连边
    G = nx.Graph()
    size = len(grid)
    domain_map = np.full((size, size), -1, dtype=int)

    for idx, (_, _, cells) in enumerate(domains):
        G.add_node(idx, size=sizes[idx], spin=spins[idx])
        for i, j in cells:
            domain_map[i, j] = idx

    # 相邻域之间的边
    for i in range(size - 1):
        for j in range(size):
            d1, d2 = domain_map[i, j], domain_map[i + 1, j]
            if d1 != -1 and d2 != -1 and d1 != d2:
                G.add_edge(d1, d2)
    for i in range(size):
        for j in range(size - 1):
            d1, d2 = domain_map[i, j], domain_map[i, j + 1]
            if d1 != -1 and d2 != -1 and d1 != d2:
                G.add_edge(d1, d2)

    # 网络指标
    n_domains = len(domains)
    avg_domain_size = np.mean(sizes)
    max_domain_size = max(sizes)

    # 度分布
    degrees = [d for _, d in G.degree()]
    avg_degree = np.mean(degrees) if degrees else 0

    # 聚类系数（三角形结构 = 三叉交界域）
    clustering = nx.average_clustering(G) if n_domains > 2 else 0.0

    # 社区检测（Louvain）
    try:
        communities = nx.community.louvain_communities(G, seed=42)
        n_communities = len(communities)
        modularity = nx.community.modularity(G, communities)
    except Exception:
        n_communities = 0
        modularity = 0.0

    # 判断是否接近临界（幂律分布）
    from scipy import stats
    power_law_fit = {}
    try:
        if len(sizes) > 5:
            log_sizes = np.log(sizes)
            (slope, intercept, r_value, p_value, std_err) = \
                stats.linregress(np.log(range(1, len(sizes) + 1)), log_sizes)
            power_law_fit = {
                "exponent": -slope,
                "r_squared": r_value ** 2,
                "near_critical": 1.0 < -slope < 2.5 if not np.isnan(slope) else False
            }
    except Exception:
        pass

    # 同手性连接（同向自旋的域是否倾向相邻）
    assortativity = nx.attribute_assortativity_coefficient(G, 'spin') if n_domains > 1 else 0

    # 用 +1 域占比判断有序度
    n_up = sizes.count(1) if isinstance(sizes[0], (int, np.integer)) else sum(1 for s in sizes if s > 0)

    return {
        "n_domains": n_domains,
        "avg_domain_size": round(float(avg_domain_size), 2),
        "max_domain_size": int(max_domain_size),
        "largest_domain_ratio": round(float(max_domain_size) / (size * size), 4),
        "avg_degree": round(float(avg_degree), 2),
        "clustering": round(float(clustering), 4),
        "n_communities": int(n_communities),
        "modularity": round(float(modularity), 4),
        "assortativity": round(float(assortativity), 4),
        "power_law": power_law_fit,
    }


# ============================================================
# 2. 生命游戏 — 结构分析
# ============================================================

def analyze_gol_patterns(grid: np.ndarray) -> dict:
    """
    分析生命游戏的存活细胞图结构：
    - 连通分量（群落）
    - 每个群落的直径、密度
    - 聚类系数（局部秩序的度量）
    """
    size = len(grid)
    cells = np.argwhere(grid > 0)
    if len(cells) < 2:
        return {"population": int(grid.sum()), "n_components": 0}

    # 建立图：8-邻域连接
    G = nx.Graph()
    cell_set = set((int(r), int(c)) for r, c in cells)
    for r, c in cells:
        ri, ci = int(r), int(c)
        G.add_node((ri, ci))
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                if di == 0 and dj == 0:
                    continue
                ni, nj = ri + di, ci + dj
                if (ni, nj) in cell_set:
                    G.add_edge((ri, ci), (ni, nj))

    # 连通分量
    components = list(nx.connected_components(G))
    comp_sizes = sorted([len(c) for c in components], reverse=True)
    n_components = len(components)

    # 分量的直径（最大内部距离）
    diameters = []
    for comp in components[:10]:  # 前10大，避免太慢
        sub = G.subgraph(comp)
        if len(sub) > 1:
            try:
                diam = nx.diameter(sub)
                diameters.append(diam)
            except nx.NetworkXError:
                pass

    avg_clustering = nx.average_clustering(G)
    density = nx.density(G)
    population = int(grid.sum())

    return {
        "population": population,
        "density": round(float(population) / (size * size), 4),
        "n_components": n_components,
        "largest_component": comp_sizes[0] if comp_sizes else 0,
        "comp_sizes_top5": comp_sizes[:5],
        "avg_component_diameter": round(float(np.mean(diameters)), 2) if diameters else 0,
        "graph_density": round(float(density), 6),
        "clustering_coefficient": round(float(avg_clustering), 4),
    }


# ============================================================
# 3. 沙堆模型 — 雪崩级联分析
# ============================================================

def analyze_sandpile_avalanches(grid: np.ndarray) -> dict:
    """
    分析沙堆的崩塌结构：高度分布、级联规模的图透视。
    """
    heights = grid.flatten()
    threshold_mask = grid >= 4

    # 构建邻接图（≥4 的格点之间有连通域）
    size = len(grid)
    critical = np.argwhere(threshold_mask)
    if len(critical) < 2:
        return {"above_threshold": int(threshold_mask.sum())}

    G = nx.Graph()
    critical_set = set((int(r), int(c)) for r, c in critical)
    for r, c in critical:
        ri, ci = int(r), int(c)
        G.add_node((ri, ci))
        for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ni, nj = ri + di, ci + dj
            if (ni, nj) in critical_set:
                G.add_edge((ri, ci), (ni, nj))

    components = list(nx.connected_components(G))
    comp_sizes = sorted([len(c) for c in components], reverse=True)

    # 高度分布熵（无序度的度量）
    from scipy.stats import entropy
    height_counts = Counter(heights.tolist())
    probs = np.array(list(height_counts.values())) / len(heights)
    height_entropy = float(entropy(probs))

    return {
        "above_threshold": int(threshold_mask.sum()),
        "n_avalanche_zones": len(components),
        "largest_avalanche_zone": comp_sizes[0] if comp_sizes else 0,
        "zone_sizes_top5": comp_sizes[:5],
        "height_entropy": round(height_entropy, 4),
        "max_height": int(grid.max()),
        "mean_height": round(float(grid.mean()), 2),
    }


# ============================================================
# 4. Boids — 领导力涌现网络
# ============================================================

def analyze_boids_network(positions: np.ndarray, velocities: np.ndarray,
                          vision_radius: float = 80.0) -> dict:
    """
    分析 Boids 群体中的信息流网络：
    - 度中心性（谁被最多同伴看到？）
    - 介数中心性（谁在控制信息流？→ 可能领导者）
    """
    n = len(positions)
    if n < 3:
        return {"error": "too few agents"}

    G = nx.Graph()
    for i in range(n):
        G.add_node(i)

    # 连接处于视觉距离内的个体
    for i in range(n):
        for j in range(i + 1, n):
            dist = np.linalg.norm(positions[i] - positions[j])
            if dist < vision_radius:
                G.add_edge(i, j, weight=1.0 / (dist + 1e-6))

    if G.number_of_edges() == 0:
        return {"n_agents": n, "n_edges": 0, "graph_density": 0}

    density = nx.density(G)
    avg_deg = sum(d for _, d in G.degree()) / n

    # 中心性分析
    degree_centrality = nx.degree_centrality(G)

    # 介数中心性（只算前几来加速）
    if n < 1000:
        betweenness = nx.betweenness_centrality(G, k=min(n, 100), seed=42)
    else:
        betweenness = {i: 0 for i in range(n)}

    top_leaders_by_betweenness = sorted(
        betweenness.items(), key=lambda x: x[1], reverse=True
    )[:5]

    # 领导者：介数中心性 > 2σ 的个体
    b_vals = list(betweenness.values())
    leader_threshold = np.mean(b_vals) + 2 * np.std(b_vals) if len(b_vals) > 2 else 0.5
    leader_count = sum(1 for v in b_vals if v > leader_threshold)

    # 小世界性
    try:
        from scipy.stats import pearsonr
        # 快速随机网络对比
        n_rand_edges = G.number_of_edges()
        rand_graph = nx.gnm_random_graph(n, n_rand_edges, seed=42)
        C_orig = nx.average_clustering(G)
        C_rand = nx.average_clustering(rand_graph)
        L_orig = nx.average_shortest_path_length(G) if n < 500 else float('nan')
        L_rand = nx.average_shortest_path_length(rand_graph) if n < 500 else float('nan')
        small_world_index = (C_orig / C_rand) / (L_orig / L_rand) if C_rand > 0 and L_rand > 0 else float('nan')
    except Exception:
        small_world_index = float('nan')

    return {
        "n_agents": n,
        "n_edges": G.number_of_edges(),
        "graph_density": round(float(density), 6),
        "avg_degree": round(float(avg_deg), 2),
        "avg_clustering": round(float(nx.average_clustering(G)), 4),
        "leader_count": int(leader_count),
        "top_leaders": [
            {"agent": int(idx), "betweenness": round(float(b), 4)}
            for idx, b in top_leaders_by_betweenness
        ],
        "small_world_index": round(float(small_world_index), 4) if not np.isnan(small_world_index) else None,
        "connected": int(nx.is_connected(G)) if n < 1000 else None,
    }


# ============================================================
# 5. Gray-Scott 反应扩散 — 斑图拓扑网络
# ============================================================

def analyze_gray_scott_pattern(U: np.ndarray, V: np.ndarray) -> dict:
    """
    分析 Gray-Scott 反应扩散生成的浓度斑图。

    策略: 以 V 浓度场为基底，通过阈值分割提取结构，
    计算斑图的拓扑网络特性（连通域、骨架、图案复杂度）。
    """
    size = len(V)

    # V 的直方图分析 — 分布形态反映图案类型
    v_flat = V.flatten()
    v_mean = float(np.mean(v_flat))
    v_std = float(np.std(v_flat))

    # 直方图熵（用概率质量，而非密度）
    hist_counts, _ = np.histogram(v_flat, bins=32)
    hist_counts = hist_counts[hist_counts > 0]
    probs = hist_counts / len(v_flat)
    v_entropy = float(-np.sum(probs * np.log(probs + 1e-30))) if len(probs) > 1 else 0.0

    # 双峰检验 — 判断是否是斑点图案（双峰分布）还是渐变条纹（单峰分布）
    # 用平滑直方图
    hist_broad, _ = np.histogram(v_flat, bins=32, density=True)
    # 寻找局部极大值数量（去噪后）
    peaks = 0
    offset = (hist_broad.max() - hist_broad.min()) * 0.1  # 去噪阈值
    for i in range(1, len(hist_broad) - 1):
        if (hist_broad[i] > hist_broad[i-1] + offset and
            hist_broad[i] > hist_broad[i+1] + offset):
            peaks += 1
    is_bimodal = peaks >= 2

    # 阈值分割：自适应多策略
    # 策略1: 均值 + 0.5σ
    # 策略2: 95分位数（对稀疏图案有效）
    # 策略3: 中位数
    v_95 = float(np.percentile(v_flat, 95))
    v_median = float(np.median(v_flat))

    # 选择最佳阈值使得覆盖率为 10%-40%
    candidates = [
        ('mean_0.5std', v_mean + v_std * 0.5),
        ('percentile_95', v_95),
        ('median', v_median),
    ]
    best_threshold = v_median
    best_ratio = 0.0
    for name, th in candidates:
        ratio = float(np.mean(V >= th))
        if 0.05 <= ratio <= 0.50:
            best_threshold = th
            best_ratio = ratio
            break
        if abs(ratio - 0.25) < abs(best_ratio - 0.25) or best_ratio == 0:
            if 0.02 <= ratio <= 0.80:
                best_threshold = th
                best_ratio = ratio

    pattern_mask = V >= best_threshold
    pattern_ratio = float(np.mean(pattern_mask))

    # 连通分量（斑图碎片）
    labeled, n_labels = _connected_components(pattern_mask)
    component_sizes = [np.sum(labeled == i) for i in range(1, n_labels + 1)]
    component_sizes.sort(reverse=True)

    # 图结构：每个斑块作为节点，相邻斑块之间连边
    if n_labels >= 2:
        G = nx.Graph()
        for idx in range(1, n_labels + 1):
            G.add_node(idx, size=component_sizes[idx - 1])

        # 相邻斑块检测
        for i in range(size - 1):
            for j in range(size):
                l1, l2 = labeled[i, j], labeled[i + 1, j]
                if l1 != 0 and l2 != 0 and l1 != l2:
                    G.add_edge(int(l1), int(l2))
        for i in range(size):
            for j in range(size - 1):
                l1, l2 = labeled[i, j], labeled[i, j + 1]
                if l1 != 0 and l2 != 0 and l1 != l2:
                    G.add_edge(int(l1), int(l2))

        n_components = nx.number_connected_components(G)
        clustering = nx.average_clustering(G) if n_labels > 2 else 0.0
        density = nx.density(G)

        # 介数中心性（哪些斑块是拓扑枢纽）
        if n_labels < 500:
            betweenness = nx.betweenness_centrality(G, k=min(n_labels, 50), seed=42)
            top_hubs = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:3]
        else:
            top_hubs = []
    else:
        n_components = 0
        clustering = 0.0
        density = 0.0
        top_hubs = []

    # 图案特征：均匀性 vs 条纹性
    # 用自相关函数判断
    autocorr = _autocorrelation(V)

    return {
        "pattern_type": "bimodal_spot" if is_bimodal else "continuous_pattern",
        "v_mean": round(v_mean, 4),
        "v_std": round(v_std, 4),
        "v_entropy": round(v_entropy, 4),
        "n_patches": int(n_labels),
        "patch_sizes_top5": component_sizes[:5],
        "largest_patch_ratio": round(component_sizes[0] / (size * size), 4) if component_sizes else 0,
        "pattern_coverage": round(pattern_ratio, 4),
        "n_patch_clusters": int(n_components),
        "patch_graph_clustering": round(float(clustering), 4),
        "patch_graph_density": round(float(density), 6),
        "autocorrelation_scale": round(float(autocorr), 4),
        "topological_hubs": [
            {"patch": int(idx), "betweenness": round(float(b), 4)}
            for idx, b in top_hubs
        ],
    }


def _connected_components(mask: np.ndarray) -> tuple:
    """快速连通分量标记（4-邻域），返回 (labeled, n_labels)"""
    labeled = np.zeros_like(mask, dtype=int)
    label = 1
    for i in range(len(mask)):
        for j in range(len(mask[i])):
            if mask[i, j] and labeled[i, j] == 0:
                stack = [(i, j)]
                labeled[i, j] = label
                while stack:
                    ci, cj = stack.pop()
                    for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ni, nj = ci + di, cj + dj
                        if 0 <= ni < len(mask) and 0 <= nj < len(mask) and mask[ni, nj] and labeled[ni, nj] == 0:
                            labeled[ni, nj] = label
                            stack.append((ni, nj))
                label += 1
    return labeled, label - 1


def _autocorrelation(arr: np.ndarray) -> float:
    """空间自相关函数，衡量图案的规则性。
    高值 → 周期性条纹；低值 → 随机斑点。
    """
    size = min(arr.shape[0], 100)  # 采样中心区域
    center = arr[arr.shape[0]//2 - size//2:arr.shape[0]//2 + size//2,
                 arr.shape[1]//2 - size//2:arr.shape[1]//2 + size//2]
    shift = 3  # 小偏移量
    shifted = np.roll(center, shift, axis=0)
    shifted2 = np.roll(center, shift, axis=1)
    corr = float(np.corrcoef(center.flatten(), shifted.flatten())[0, 1])
    corr2 = float(np.corrcoef(center.flatten(), shifted2.flatten())[0, 1])
    return (abs(corr) + abs(corr2)) / 2


# ============================================================
# 6. 统一入口
# ============================================================

def get_network_report(experiment_name: str, result: dict, params: dict = None) -> dict:
    """
    对实验结果进行网络分析，返回结构化的指标报告。

    根据实验类型自动选择适当的分析函数。
    """
    analysis_map = {
        'phase_transitions': lambda: analyze_phase_domains(result.get('grid', np.array([]))),
        'game_of_life': lambda: analyze_gol_patterns(result.get('grid', np.array([]))),
        'sandpile': lambda: analyze_sandpile_avalanches(result.get('grid', np.array([]))),
        'boids': lambda: analyze_boids_network(
            result.get('positions', np.array([])),
            result.get('velocities', np.array([]))
        ),
        'gray_scott': lambda: analyze_gray_scott_pattern(
            result.get('U', np.array([])),
            result.get('V', np.array([]))
        ),
        'turing_patterns': lambda: analyze_gray_scott_pattern(
            result.get('U', np.array([])),
            result.get('V', np.array([]))
        ),
    }

    analyzer = analysis_map.get(experiment_name)
    if analyzer:
        try:
            return analyzer()
        except Exception as e:
            return {"error": str(e)}
    else:
        return {"note": f"Network analysis not yet implemented for '{experiment_name}'"}


# ============================================================
# CLI / 快速测试
# ============================================================

if __name__ == '__main__':
    print("=== NetworkX Analysis Module ===")
    print("Analyzing emergence experiments through graph theory.")
    print()

    # 测试 Ising 域分析
    print("--- Ising Domain Test ---")
    test_grid = np.random.choice([-1, 1], size=(50, 50))
    report = analyze_phase_domains(test_grid)
    for k, v in report.items():
        print(f"  {k}: {v}")
    print()

    # 测试 Boids 网络
    print("--- Boids Network Test ---")
    import time
    np.random.seed(int(time.time() * 1000) % 2 ** 32)
    pos = np.random.rand(30, 2) * 500
    vel = (np.random.rand(30, 2) - 0.5) * 4
    report = analyze_boids_network(pos, vel)
    for k, v in report.items():
        print(f"  {k}: {v}")
