#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
适应性共识算法的可靠性计算器
专门针对新共识算法设计的可靠性评估
"""

import statistics
from typing import List, Dict, Any, Tuple
from collections import Counter


class AdaptiveReliabilityCalculator:
    """
    适应性共识算法的可靠性计算器

    专门处理新共识算法的可靠性评估：
    1. 动态评估器数量
    2. 多轮共识过程
    3. 合并评分与原始评分的差异
    """

    def __init__(self):
        # 可靠性计算参数
        self.consensus_quality_weight = 0.4    # 共识质量权重
        self.evaluator_diversity_weight = 0.3  # 评估器多样性权重
        self.processing_efficiency_weight = 0.2  # 处理效率权重
        self.final_agreement_weight = 0.1     # 最终一致性权重

    def calculate_adaptive_reliability(self, consensus_result: Dict[str, Any],
                                      original_scores: List[int],
                                      processing_history: List[Dict] = None) -> Dict[str, Any]:
        """
        计算适应性共识算法的可靠性

        Args:
            consensus_result: 共识算法的结果
            original_scores: 原始评分列表
            processing_history: 处理过程历史记录

        Returns:
            可靠性评估结果
        """
        final_scores = consensus_result['final_scores']
        consensus_method = consensus_result['consensus_method']
        processing_rounds = consensus_result['processing_rounds']

        # 1. 共识质量评估
        consensus_quality = self._assess_consensus_quality(
            original_scores, final_scores, consensus_method
        )

        # 2. 评估器多样性评估
        diversity_score = self._assess_evaluator_diversity(
            original_scores, final_scores, processing_rounds
        )

        # 3. 处理效率评估
        efficiency_score = self._assess_processing_efficiency(
            processing_rounds, consensus_method
        )

        # 4. 最终一致性评估
        agreement_score = self._assess_final_agreement(final_scores)

        # 5. 综合可靠性计算
        overall_reliability = (
            self.consensus_quality_weight * consensus_quality +
            self.evaluator_diversity_weight * diversity_score +
            self.processing_efficiency_weight * efficiency_score +
            self.final_agreement_weight * agreement_score
        )

        return {
            'overall_reliability': round(overall_reliability, 3),
            'consensus_quality': round(consensus_quality, 3),
            'evaluator_diversity': round(diversity_score, 3),
            'processing_efficiency': round(efficiency_score, 3),
            'final_agreement': round(agreement_score, 3),
            'detailed_analysis': {
                'original_scores': original_scores,
                'final_scores': final_scores,
                'processing_rounds': processing_rounds,
                'consensus_method': consensus_method,
                'score_transformation': self._analyze_score_transformation(
                    original_scores, final_scores
                )
            }
        }

    def _assess_consensus_quality(self, original_scores: List[int],
                                final_scores: List[int],
                                consensus_method: str) -> float:
        """评估共识质量"""

        # 基于共识方法的基础分数
        method_scores = {
            'perfect_consensus': 1.0,      # 完全共识，最高质量
            'minor_consensus': 0.8,        # 轻微分歧，高质量
            'median_consensus': 0.7,       # 中位数共识，较高质量
            'average_consensus': 0.6,      # 平均数共识，中等质量
            'extended_consensus': 0.5,     # 扩展共识，中等质量
            'max_divergence_consensus': 0.4 # 最大分歧共识，需要改进
        }

        base_score = method_scores.get(consensus_method, 0.3)

        # 评分改善程度调整
        original_range = max(original_scores) - min(original_scores)
        final_range = max(final_scores) - min(final_scores)

        if original_range > 0:
            improvement = (original_range - final_range) / original_range
            quality_adjustment = min(improvement * 0.2, 0.2)  # 最多提升0.2
        else:
            quality_adjustment = 0.0

        return min(base_score + quality_adjustment, 1.0)

    def _assess_evaluator_diversity(self, original_scores: List[int],
                                   final_scores: List[int],
                                   processing_rounds: int) -> float:
        """评估评估器多样性"""

        # 1. 原始评估器的多样性
        original_diversity = len(set(original_scores)) / len(original_scores)

        # 2. 最终评分的多样性
        final_diversity = len(set(final_scores)) / len(final_scores)

        # 3. 处理轮数的合理性（轮数越多，说明分歧越大，但最终解决了）
        round_efficiency = max(0.0, 1.0 - (processing_rounds - 1) * 0.2)

        # 综合多样性分数
        diversity_score = (
            0.4 * original_diversity +
            0.4 * final_diversity +
            0.2 * round_efficiency
        )

        return diversity_score

    def _assess_processing_efficiency(self, processing_rounds: int,
                                    consensus_method: str) -> float:
        """评估处理效率"""

        # 基础效率分数（轮数越少效率越高）
        if processing_rounds == 1:
            round_efficiency = 1.0
        elif processing_rounds == 2:
            round_efficiency = 0.8
        else:
            round_efficiency = max(0.4, 1.0 - (processing_rounds - 2) * 0.2)

        # 根据共识方法调整
        method_efficiency = {
            'perfect_consensus': 1.0,      # 一次性达成，最高效
            'minor_consensus': 0.9,        # 轻微处理，高效
            'median_consensus': 0.8,       # 中位数处理，较高效
            'average_consensus': 0.7,      # 平均数处理，中等效率
            'extended_consensus': 0.6,     # 需要扩展，效率较低
            'max_divergence_consensus': 0.5 # 最大分歧处理，效率最低
        }

        method_factor = method_efficiency.get(consensus_method, 0.5)

        return (round_efficiency + method_factor) / 2

    def _assess_final_agreement(self, final_scores: List[int]) -> float:
        """评估最终一致性"""

        if len(final_scores) < 2:
            return 1.0

        # 1. 标准差一致性
        std_dev = statistics.stdev(final_scores)
        max_possible_std = 2.0  # 1-5评分制的最大标准差
        consistency_score = max(0.0, 1.0 - (std_dev / max_possible_std))

        # 2. 众数比例
        score_counts = Counter(final_scores)
        max_count = max(score_counts.values())
        mode_ratio = max_count / len(final_scores)

        # 3. 评分范围
        score_range = max(final_scores) - min(final_scores)
        range_score = max(0.0, 1.0 - (score_range / 4.0))  # 最大范围是4

        # 综合一致性
        agreement = 0.4 * consistency_score + 0.4 * mode_ratio + 0.2 * range_score

        return agreement

    def _analyze_score_transformation(self, original_scores: List[int],
                                    final_scores: List[int]) -> Dict[str, Any]:
        """分析评分转换过程"""

        original_mean = statistics.mean(original_scores)
        final_mean = statistics.mean(final_scores)

        original_median = statistics.median(original_scores)
        final_median = statistics.median(final_scores)

        return {
            'original_mean': round(original_mean, 2),
            'final_mean': round(final_mean, 2),
            'mean_change': round(final_mean - original_mean, 2),
            'original_median': original_median,
            'final_median': final_median,
            'median_change': final_median - original_median,
            'score_count_change': len(final_scores) - len(original_scores)
        }


def demonstrate_adaptive_reliability():
    """演示适应性可靠性计算"""
    print("🔧 适应性共识算法可靠性计算演示")
    print("=" * 60)

    calculator = AdaptiveReliabilityCalculator()

    # 模拟共识结果
    test_cases = [
        {
            'name': '完全共识场景',
            'consensus_result': {
                'consensus_score': 3.0,
                'final_scores': [3, 3, 3],
                'consensus_method': 'perfect_consensus',
                'processing_rounds': 1
            },
            'original_scores': [3, 3, 3]
        },
        {
            'name': '轻微分歧场景',
            'consensus_result': {
                'consensus_score': 3.67,
                'final_scores': [3, 3, 5],
                'consensus_method': 'minor_consensus',
                'processing_rounds': 1
            },
            'original_scores': [3, 3, 5]
        },
        {
            'name': '严重分歧处理后',
            'consensus_result': {
                'consensus_score': 2.33,
                'final_scores': [1, 3, 3],
                'consensus_method': 'extended_consensus',
                'processing_rounds': 2
            },
            'original_scores': [1, 1, 5]
        },
        {
            'name': '最大分歧处理后',
            'consensus_result': {
                'consensus_score': 3.0,
                'final_scores': [3, 3, 3],
                'consensus_method': 'max_divergence_consensus',
                'processing_rounds': 2
            },
            'original_scores': [1, 3, 5]
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📊 测试场景 {i}: {test_case['name']}")
        print(f"原始评分: {test_case['original_scores']}")
        print(f"最终评分: {test_case['consensus_result']['final_scores']}")
        print(f"共识方法: {test_case['consensus_result']['consensus_method']}")
        print("-" * 50)

        reliability = calculator.calculate_adaptive_reliability(
            test_case['consensus_result'],
            test_case['original_scores']
        )

        print(f"🎯 可靠性评估结果:")
        print(f"  总体可靠性: {reliability['overall_reliability']:.3f}")
        print(f"  共识质量: {reliability['consensus_quality']:.3f}")
        print(f"  评估器多样性: {reliability['evaluator_diversity']:.3f}")
        print(f"  处理效率: {reliability['processing_efficiency']:.3f}")
        print(f"  最终一致性: {reliability['final_agreement']:.3f}")


if __name__ == "__main__":
    demonstrate_adaptive_reliability()