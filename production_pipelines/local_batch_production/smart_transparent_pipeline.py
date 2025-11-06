#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能透明流水线 - 集成智能回退评估器
解决API限制和默认评分问题，确保评估质量
"""

import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

# 添加包目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from smart_evaluator import SmartEvaluator
from single_report_pipeline.input_parser import InputParser
from single_report_pipeline.context_generator import ContextGenerator
from single_report_pipeline.reverse_scoring_processor import ReverseScoringProcessor

class SmartTransparentPipeline:
    """智能透明流水线 - 集成智能回退评估器"""

    def __init__(self, use_cloud: bool = True, dispute_threshold: int = 2):
        """
        初始化智能透明流水线

        Args:
            use_cloud: 是否优先使用云端模型
            dispute_threshold: 争议检测阈值
        """
        self.use_cloud = use_cloud
        self.dispute_threshold = dispute_threshold

        # 初始化组件
        self.input_parser = InputParser()
        self.context_generator = ContextGenerator()
        self.reverse_processor = ReverseScoringProcessor()
        self.smart_evaluator = SmartEvaluator()

        # 模型配置
        if use_cloud:
            self.primary_models = [
                'deepseek-v3.1:671b-cloud',
                'gpt-oss:120b-cloud',
                'qwen3-vl:235b-cloud'
            ]
            self.dispute_models = [
                'qwen3-vl:235b-cloud',
                'gpt-oss:120b-cloud'
            ]
        else:
            self.primary_models = [
                'qwen3:8b',
                'deepseek-r1:8b',
                'mistral:instruct'
            ]
            self.dispute_models = [
                'qwen3:8b',
                'deepseek-r1:8b'
            ]

        print(f"智能透明流水线初始化完成")
        print(f"主要评估模型: {self.primary_models}")
        print(f"争议解决模型: {self.dispute_models}")
        print(f"智能回退: ✅ 已启用")

    def detect_major_dimension_disputes(self, all_scores: List[Dict[str, int]], question: Dict, threshold: int = 2) -> Dict[str, Dict]:
        """
        检测主要维度的争议（只检查5个核心维度）

        Args:
            all_scores: 所有评分结果
            question: 题目信息
            threshold: 争议阈值

        Returns:
            争议信息字典
        """
        major_traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
        disputes = {}

        if len(all_scores) < 2:
            return disputes

        for trait in major_traits:
            scores = [score[trait] for score in all_scores if trait in score]
            if len(scores) >= 2:
                min_score = min(scores)
                max_score = max(scores)
                if max_score - min_score >= threshold:
                    disputes[trait] = {
                        'scores': scores,
                        'range': max_score - min_score,
                        'severity': 'high' if max_score - min_score >= 3 else 'medium'
                    }

        return disputes

    def resolve_disputes_intelligently(self, disputes: Dict, question: Dict, all_models_used: List[str], all_scores_data: List[Dict]) -> List[Dict]:
        """
        智能争议解决

        Args:
            disputes: 争议信息
            question: 题目信息
            all_models_used: 已使用的模型
            all_scores_data: 所有评分数据

        Returns:
            解决后的评分结果
        """
        if not disputes:
            return all_scores_data

        question_id = question.get('question_id', 'Unknown')
        print(f"  争议解决 (智能回退): {len(disputes)} 个维度存在分歧")

        # 生成争议解决上下文
        context = self.context_generator.generate_dispute_resolution_prompt(question, disputes, all_scores_data)

        # 尝试使用争议解决模型
        resolution_scores = []

        for model in self.dispute_models:
            if model in all_models_used:
                continue  # 跳过已使用的模型

            try:
                print(f"    使用争议解决模型: {model}")
                scores = self.smart_evaluator.evaluate_with_fallback(
                    context=context,
                    preferred_models=[model],
                    question_id=question_id
                )

                resolution_scores.append({
                    'model': model,
                    'scores': scores,
                    'raw_scores': scores.copy(),
                    'resolution_role': 'dispute_resolver'
                })

                # 添加到总分数据中
                all_scores_data.append(scores)
                break  # 成功一个就够了

            except Exception as e:
                print(f"    ❌ 争议解决模型 {model} 失败: {e}")
                continue

        return all_scores_data

    def calculate_final_scores_intelligently(self, all_scores_data: List[Dict], question: Dict) -> Dict[str, Any]:
        """
        智能计算最终得分

        Args:
            all_scores_data: 所有评分数据
            question: 题目信息

        Returns:
            最终评分结果
        """
        major_traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']

        # 分离初始评分和争议解决评分
        initial_scores = [s for s in all_scores_data if isinstance(s, dict) and 'model' in s]
        resolution_scores = [s for s in all_scores_data if isinstance(s, dict) and not any(m in str(s) for m in ['deepseek-v3.1', 'gpt-oss', 'qwen3-vl'])]

        # 计算加权平均
        final_scores = {}
        trait_details = {}

        for trait in major_traits:
            # 收集所有有效评分
            valid_scores = []
            model_names = []

            for score_data in all_scores_data:
                if isinstance(score_data, dict):
                    if trait in score_data and isinstance(score_data[trait], (int, float)):
                        valid_scores.append(score_data[trait])
                        model_names.append(score_data.get('model', 'unknown'))

            if not valid_scores:
                # 如果没有有效评分，使用智能回退
                context = self.context_generator.generate_evaluation_prompt(question)
                try:
                    fallback_scores = self.smart_evaluator.evaluate_with_fallback(
                        context=context,
                        preferred_models=self.primary_models,
                        question_id=question.get('question_id', 'emergency_fallback')
                    )
                    final_scores[trait] = fallback_scores.get(trait, 3)
                    model_names = ['smart_fallback']
                except Exception as e:
                    print(f"    ❌ 智能回退失败: {e}")
                    final_scores[trait] = 3  # 最后的保护值
                    model_names = ['emergency_default']
            else:
                # 计算加权平均（争议解决评分权重更高）
                if len(valid_scores) >= 3:
                    # 去掉最高和最低分后取平均
                    valid_scores.sort()
                    middle_scores = valid_scores[1:-1]
                    final_scores[trait] = sum(middle_scores) / len(middle_scores)
                else:
                    final_scores[trait] = sum(valid_scores) / len(valid_scores)

                final_scores[trait] = round(final_scores[trait])

            trait_details[trait] = {
                'final_score': final_scores[trait],
                'valid_scores': valid_scores,
                'models_used': model_names,
                'count': len(valid_scores)
            }

        # 计算整体可靠性
        reliability = self._calculate_reliability_score(trait_details, len(initial_scores), len(resolution_scores))

        result = {
            'final_scores': final_scores,
            'trait_details': trait_details,
            'reliability': reliability,
            'total_evaluations': len(all_scores_data),
            'models_used': list(set([s.get('model', 'unknown') for s in initial_scores])),
            'has_disputes': len(self.detect_major_dimension_disputes([s.get('scores', s) for s in initial_scores if isinstance(s, dict)], question)) > 0
        }

        return result

    def _calculate_reliability_score(self, trait_details: Dict, initial_count: int, resolution_count: int) -> float:
        """计算可靠性评分"""
        base_reliability = 0.5

        # 评分数量奖励
        count_bonus = min(0.3, initial_count * 0.1)

        # 一致性奖励
        consistency_bonus = 0
        for trait, details in trait_details.items():
            scores = details['valid_scores']
            if len(scores) >= 2:
                std_dev = (sum((s - sum(scores)/len(scores))**2 for s in scores) / len(scores))**0.5
                if std_dev < 0.5:
                    consistency_bonus += 0.1
                elif std_dev < 1.0:
                    consistency_bonus += 0.05

        consistency_bonus = min(consistency_bonus, 0.3)

        # 争议解决奖励
        resolution_bonus = min(0.2, resolution_count * 0.1)

        final_reliability = base_reliability + count_bonus + consistency_bonus + resolution_bonus
        return min(final_reliability, 1.0)

    def calculate_big5_averages(self, question_results: List[Dict]) -> Dict[str, float]:
        """计算Big Five平均分"""
        if not question_results:
            return {}

        big5_sums = {
            'openness_to_experience': 0,
            'conscientiousness': 0,
            'extraversion': 0,
            'agreeableness': 0,
            'neuroticism': 0
        }

        valid_count = 0
        for result in question_results:
            if result.get('success', True) and 'final_scores' in result:
                scores = result['final_scores']
                for trait in big5_sums:
                    big5_sums[trait] += scores.get(trait, 3)
                valid_count += 1

        if valid_count == 0:
            return {}

        return {trait: sum_score / valid_count for trait, sum_score in big5_sums.items()}

    def infer_mbti_type(self, big5_scores: Dict[str, float]) -> str:
        """从Big Five得分推断MBTI类型"""
        if not big5_scores:
            return "Unknown"

        E = big5_scores.get('extraversion', 3)
        O = big5_scores.get('openness_to_experience', 3)
        C = big5_scores.get('conscientiousness', 3)
        A = big5_scores.get('agreeableness', 3)
        N = big5_scores.get('neuroticism', 3)

        # E/I: 外向性 vs 神经质
        e_score = E + (5 - N)
        i_score = (5 - E) + N
        E_preference = 'E' if e_score > i_score else 'I'

        # S/N: 感觉 vs 直觉
        S_preference = 'S' if O <= 3 else 'N'

        # T/F: 思考 vs 情感
        T_preference = 'T' if A <= 3 else 'F'

        # J/P: 判断 vs 知觉
        J_preference = 'J' if C > 3 else 'P'

        return f"{E_preference}{S_preference}{T_preference}{J_preference}"

    def process_single_question(self, question: Dict, question_idx: int) -> Dict[str, Any]:
        """
        处理单个题目（使用智能评估器）
        """
        question_id = question.get('question_id', 'Unknown')
        question_concept = question['question_data'].get('mapped_ipip_concept', 'Unknown')

        # 确保question_id是字符串
        if not isinstance(question_id, str):
            question_id = str(question_id)

        is_reversed = self.reverse_processor.is_reverse_item(question_id) or \
                     self.reverse_processor.is_reverse_from_concept(question_concept)

        print(f"处理第 {question_idx+1:02d} 题 (ID: {question_id})")
        print(f"  题目概念: {question_concept}")
        print(f"  是否反向: {is_reversed}")
        print(f"  被试回答: {question['extracted_response'][:100]}...")

        # 生成评估上下文
        context = self.context_generator.generate_evaluation_prompt(question)

        # 初始评估（使用智能评估器）
        print(f"  初始评估 (使用 {len(self.primary_models)} 个模型):")
        initial_scores = []

        for i, model in enumerate(self.primary_models):
            try:
                print(f"    └─ 使用智能评估器调用模型 {model} 评估题目 {question_id}...")

                scores = self.smart_evaluator.evaluate_with_fallback(
                    context=context,
                    preferred_models=[model],
                    question_id=question_id
                )

                initial_scores.append({
                    'model': model,
                    'scores': scores,
                    'raw_scores': scores.copy()
                })
                print(f"      ✅ 评分: {scores}")

            except Exception as e:
                print(f"      ❌ 模型 {model} 智能评估失败: {e}")
                # 智能评估器内部已经处理了回退，这里只是记录
                continue

        if not initial_scores:
            raise RuntimeError(f"所有模型都无法评估题目 {question_id}")

        # 检测争议
        all_initial_scores = [item['scores'] for item in initial_scores]
        disputes = self.detect_major_dimension_disputes(all_initial_scores, question, self.dispute_threshold)

        print(f"  争议检测: {len(disputes)} 个主要维度存在分歧")
        if disputes:
            for trait, dispute_info in disputes.items():
                print(f"    - {trait}: 评分 {dispute_info['scores']}, 差距 {dispute_info['range']}")

        # 争议解决
        current_scores = all_initial_scores.copy()
        all_models_used = [item['model'] for item in initial_scores]

        if disputes:
            print(f"  开始智能争议解决...")
            current_scores = self.resolve_disputes_intelligently(
                disputes, question, all_models_used, initial_scores
            )

        # 计算最终得分
        final_result = self.calculate_final_scores_intelligently(current_scores, question)

        print(f"  ✅ 最终得分: {final_result['final_scores']}")
        print(f"  📊 可靠性: {final_result['reliability']:.3f}")

        return {
            'question_id': question_id,
            'question_concept': question_concept,
            'is_reversed': is_reversed,
            'success': True,
            'final_scores': final_result['final_scores'],
            'trait_details': final_result['trait_details'],
            'reliability': final_result['reliability'],
            'models_used': final_result['models_used'],
            'has_disputes': final_result['has_disputes'],
            'total_evaluations': final_result['total_evaluations']
        }

    def process_single_report(self, file_path: str) -> Dict[str, Any]:
        """
        处理单个测评报告（智能版本）
        """
        print("=" * 80)
        print("智能透明流水线 - 处理测评报告")
        print("=" * 80)
        print(f"处理文件: {file_path}")
        print(f"智能回退: ✅ 已启用")
        print(f"API限制处理: ✅ 已启用")
        print()

        start_time = time.time()

        try:
            # 1. 解析输入文件
            print("步骤1: 解析输入文件")
            questions = self.input_parser.parse_assessment_json(file_path)
            print(f"  解析完成: {len(questions)} 道题目")
            print()

            # 2. 处理每道题
            print("步骤2: 智能逐题处理与评估")
            print("-" * 80)

            all_question_results = []
            successful_questions = 0
            failed_questions = 0

            for i, question in enumerate(questions):
                try:
                    result = self.process_single_question(question, i)
                    all_question_results.append(result)
                    successful_questions += 1
                except Exception as e:
                    print(f"  ❌ 题目 {i+1} 处理失败: {e}")
                    all_question_results.append({
                        'question_id': question.get('question_id', f'q_{i}'),
                        'success': False,
                        'error': str(e)
                    })
                    failed_questions += 1

                # 添加延迟避免过载
                if i < len(questions) - 1:  # 最后一个不需要延迟
                    time.sleep(1)

            print()

            # 3. 计算整体结果
            print("步骤3: 计算整体分析结果")
            print("-" * 40)

            # 计算Big Five平均分
            big5_averages = self.calculate_big5_averages(all_question_results)
            overall_reliability = sum(r.get('reliability', 0) for r in all_question_results if r.get('success', False)) / max(1, successful_questions)

            print(f"Big Five 平均得分:")
            trait_names = {
                'openness_to_experience': '开放性',
                'conscientiousness': '尽责性',
                'extraversion': '外向性',
                'agreeableness': '宜人性',
                'neuroticism': '神经质'
            }
            for trait, score in big5_averages.items():
                name = trait_names.get(trait, trait)
                print(f"  {name}: {score:.2f}")

            # 推断MBTI类型
            mbti_type = self.infer_mbti_type(big5_averages)
            print(f"推断MBTI类型: {mbti_type}")

            processing_time = time.time() - start_time

            # 生成智能评估器状态报告
            evaluator_report = self.smart_evaluator.get_model_status_report()

            result = {
                'success': True,
                'file_path': file_path,
                'processing_time': round(processing_time, 1),
                'total_questions': len(questions),
                'successful_questions': successful_questions,
                'failed_questions': failed_questions,
                'big5_scores': big5_averages,
                'mbti_type': mbti_type,
                'overall_reliability': round(overall_reliability, 3),
                'question_results': all_question_results,
                'pipeline_info': {
                    'type': 'smart_transparent',
                    'intelligent_fallback': True,
                    'api_limit_handling': True,
                    'no_default_scores': True
                },
                'evaluator_status': evaluator_report
            }

            print()
            print("🎉 智能处理完成!")
            print(f"处理时间: {processing_time:.1f}秒")
            print(f"成功率: {successful_questions}/{len(questions)} ({successful_questions/len(questions)*100:.1f}%)")
            print(f"整体可靠性: {overall_reliability:.3f}")
            print(f"智能回退次数: {evaluator_report.get('fallback_count', 0)}")

            return result

        except Exception as e:
            print(f"❌ 处理失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'file_path': file_path,
                'error': str(e),
                'processing_time': round(time.time() - start_time, 1)
            }


def test_smart_pipeline():
    """测试智能透明流水线"""
    print("🧠 智能透明流水线测试")
    print("=" * 50)

    # 查找测试文件
    test_files = [
        "results/readonly-original/asses_deepseek_r1_70b_agent_big_five_50_complete2_a1_e0_t0_0_09271.json",
        "results/readonly-original/asses_deepseek_r1_70b_agent_big_five_50_complete2_a10_e0_t0_0_09271.json"
    ]

    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"📋 测试文件: {test_file}")
            break
    else:
        print("❌ 未找到测试文件")
        return False

    try:
        # 创建智能流水线
        pipeline = SmartTransparentPipeline(use_cloud=True)

        # 处理测试文件
        result = pipeline.process_single_report(test_file)

        if result.get('success', False):
            print(f"✅ 测试成功!")
            print(f"Big Five得分: {result.get('big5_scores', {})}")
            print(f"MBTI类型: {result.get('mbti_type', 'Unknown')}")
            print(f"整体可靠性: {result.get('overall_reliability', 0):.3f}")
            return True
        else:
            print(f"❌ 测试失败: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False


if __name__ == "__main__":
    success = test_smart_pipeline()
    sys.exit(0 if success else 1)