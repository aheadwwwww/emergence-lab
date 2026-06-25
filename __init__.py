"""
EmergenceLab — 可编程涌现实验框架

提供统一的接口让研究者能观察、干预、引导涌现行为。
"""

from .models.lenia import Lenia
from .models.nca import NCA
from .models.pheromone import PheromoneCA
from .core.metrics import EmergenceMetrics

__version__ = '0.1.0'
__all__ = ['Lenia', 'NCA', 'PheromoneCA', 'EmergenceMetrics']