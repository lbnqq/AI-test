#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloud Fallback 性能监控和优化模块
实时监控fallback性能，提供优化建议
"""

import time
import asyncio
import json
import statistics
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict, deque
import logging

from cloud_fallback_manager import (
    CloudFallbackManager,
    ModelProvider,
    ModelConfig,
    EvaluationResult
)


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    provider: str
    model_name: str
    response_time: float
    success: bool
    error_message: Optional[str] = None
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class ProviderStats:
    """提供商统计数据"""
    provider: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    success_rate: float
    error_types: Dict[str, int]


class FallbackPerformanceMonitor:
    """Fallback性能监控器"""

    def __init__(self, max_history: int = 1000):
        """
        初始化性能监控器

        Args:
            max_history: 最大历史记录数量
        """
        self.max_history = max_history
        self.metrics_history: deque = deque(maxlen=max_history)
        self.provider_stats: Dict[str, ProviderStats] = {}
        self.session_stats = {
            'start_time': time.time(),
            'total_requests': 0,
            'successful_fallbacks': 0,
            'complete_failures': 0
        }

        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger("FallbackPerformanceMonitor")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def record_metric(self, result: EvaluationResult, fallback_chain_used: List[str] = None):
        """
        记录性能指标

        Args:
            result: 评估结果
            fallback_chain_used: 使用的fallback链
        """
        metric = PerformanceMetrics(
            provider=result.provider.value,
            model_name=result.model_name,
            response_time=result.response_time,
            success=result.success,
            error_message=result.error_message
        )

        # 添加到历史记录
        self.metrics_history.append(metric)

        # 更新提供商统计
        self._update_provider_stats(metric)

        # 更新会话统计
        self.session_stats['total_requests'] += 1

        if result.success:
            self.session_stats['successful_fallbacks'] += 1
        else:
            self.session_stats['complete_failures'] += 1

        # 记录日志
        if result.success:
            self.logger.info(
                f"✅ 成功评估: {result.provider.value} - {result.model_name} "
                f"(响应时间: {result.response_time:.2f}s)"
            )
        else:
            self.logger.warning(
                f"❌ 评估失败: {result.provider.value} - {result.error_message}"
            )

        # 记录fallback链使用情况
        if fallback_chain_used:
            self.logger.info(f"🔄 Fallback链: {' → '.join(fallback_chain_used)}")

    def _update_provider_stats(self, metric: PerformanceMetrics):
        """更新提供商统计"""
        provider_key = f"{metric.provider}:{metric.model_name}"

        if provider_key not in self.provider_stats:
            self.provider_stats[provider_key] = ProviderStats(
                provider=metric.provider,
                model_name=metric.model_name,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                avg_response_time=0.0,
                success_rate=0.0,
                error_types={}
            )

        stats = self.provider_stats[provider_key]
        stats.total_requests += 1

        if metric.success:
            stats.successful_requests += 1
        else:
            stats.failed_requests += 1
            if metric.error_message:
                error_type = metric.error_message.split(':')[0]  # 取错误类型
                stats.error_types[error_type] = stats.error_types.get(error_type, 0) + 1

        # 计算成功率
        stats.success_rate = stats.successful_requests / stats.total_requests

        # 更新平均响应时间（只计算成功的请求）
        if metric.success:
            total_time = stats.avg_response_time * (stats.successful_requests - 1) + metric.response_time
            stats.avg_response_time = total_time / stats.successful_requests

    def get_performance_summary(self) -> Dict:
        """获取性能摘要"""
        current_time = time.time()
        session_duration = current_time - self.session_stats['start_time']

        # 计算总体统计
        total_requests = self.session_stats['total_requests']
        successful_requests = self.session_stats['successful_fallbacks']

        overall_success_rate = successful_requests / total_requests if total_requests > 0 else 0

        # 提供商排名
        provider_ranking = sorted(
            self.provider_stats.items(),
            key=lambda x: x[1].success_rate,
            reverse=True
        )

        # 最近性能趋势（最近50次请求）
        recent_metrics = list(self.metrics_history)[-50:]
        recent_success_rate = sum(1 for m in recent_metrics if m.success) / len(recent_metrics) if recent_metrics else 0

        summary = {
            'session_info': {
                'start_time': datetime.fromtimestamp(self.session_stats['start_time']).isoformat(),
                'duration_seconds': session_duration,
                'total_requests': total_requests,
                'successful_requests': successful_requests,
                'complete_failures': self.session_stats['complete_failures']
            },
            'overall_performance': {
                'success_rate': overall_success_rate,
                'recent_success_rate': recent_success_rate,
                'requests_per_minute': (total_requests / session_duration) * 60 if session_duration > 0 else 0
            },
            'provider_ranking': [
                {
                    'provider_model': key,
                    'success_rate': stats.success_rate,
                    'avg_response_time': stats.avg_response_time,
                    'total_requests': stats.total_requests,
                    'error_types': stats.error_types
                }
                for key, stats in provider_ranking
            ],
            'recommendations': self._generate_recommendations()
        }

        return summary

    def _generate_recommendations(self) -> List[str]:
        """生成性能优化建议"""
        recommendations = []

        if not self.provider_stats:
            return ["暂无足够数据生成建议"]

        # 分析成功率
        low_success_providers = [
            key for key, stats in self.provider_stats.items()
            if stats.success_rate < 0.8 and stats.total_requests >= 5
        ]

        if low_success_providers:
            recommendations.append(
                f"⚠️ 低成功率提供商: {', '.join(low_success_providers)} "
                f"(成功率 < 80%)，建议检查配置或网络连接"
            )

        # 分析响应时间
        slow_providers = [
            key for key, stats in self.provider_stats.items()
            if stats.avg_response_time > 10.0 and stats.successful_requests >= 3
        ]

        if slow_providers:
            recommendations.append(
                f"🐌 响应缓慢的提供商: {', '.join(slow_providers)} "
                f"(平均响应时间 > 10s)，建议优化超时设置或更换模型"
            )

        # 分析fallback模式
        if len(self.metrics_history) >= 10:
            recent_metrics = list(self.metrics_history)[-10:]
            fallback_usage = defaultdict(int)

            for metric in recent_metrics:
                if metric.success:
                    fallback_usage[metric.provider] += 1

            total_successful = sum(fallback_usage.values())
            if total_successful > 0:
                primary_usage = fallback_usage.get('ollama_cloud', 0) / total_successful
                if primary_usage < 0.7:
                    recommendations.append(
                        f"🔄 Ollama Cloud使用率较低: {primary_usage:.1%}，"
                        f"建议检查云服务可用性或调整fallback策略"
                    )

        # 错误类型分析
        common_errors = defaultdict(int)
        for stats in self.provider_stats.values():
            for error_type, count in stats.error_types.items():
                common_errors[error_type] += count

        if common_errors:
            most_common_error = max(common_errors.items(), key=lambda x: x[1])
            if most_common_error[1] >= 3:
                recommendations.append(
                    f"❌ 常见错误类型: {most_common_error[0]} "
                    f"(出现{most_common_error[1]}次)，建议针对性解决"
                )

        if not recommendations:
            recommendations.append("✅ 系统运行良好，无明显性能问题")

        return recommendations

    def get_provider_health_score(self, provider: str, model_name: str) -> float:
        """
        获取提供商健康评分 (0-100)

        Args:
            provider: 提供商名称
            model_name: 模型名称

        Returns:
            健康评分
        """
        key = f"{provider}:{model_name}"
        if key not in self.provider_stats:
            return 0.0

        stats = self.provider_stats[key]

        # 基础分数：成功率 * 60%
        success_score = stats.success_rate * 60

        # 响应时间分数：响应时间越短分数越高 * 30%
        # 响应时间 < 2s = 30分, 2-10s = 30-10分, >10s = 0-10分
        if stats.avg_response_time <= 2:
            response_score = 30
        elif stats.avg_response_time <= 10:
            response_score = 30 - (stats.avg_response_time - 2) * 2.5
        else:
            response_score = max(0, 10 - (stats.avg_response_time - 10))

        # 稳定性分数：请求数量 * 10%
        # 请求数 >= 10 = 10分, 5-10 = 5-10分, <5 = 0-5分
        if stats.total_requests >= 10:
            stability_score = 10
        elif stats.total_requests >= 5:
            stability_score = 5 + (stats.total_requests - 5)
        else:
            stability_score = stats.total_requests

        total_score = success_score + response_score + stability_score
        return min(100, max(0, total_score))

    def export_metrics(self, filepath: str):
        """
        导出性能指标到文件

        Args:
            filepath: 文件路径
        """
        metrics_data = {
            'export_time': datetime.now().isoformat(),
            'session_stats': self.session_stats,
            'provider_stats': {key: asdict(stats) for key, stats in self.provider_stats.items()},
            'performance_summary': self.get_performance_summary(),
            'recent_metrics': [asdict(m) for m in list(self.metrics_history)[-100:]]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metrics_data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"📊 性能指标已导出到: {filepath}")

    def reset_metrics(self):
        """重置所有性能指标"""
        self.metrics_history.clear()
        self.provider_stats.clear()
        self.session_stats = {
            'start_time': time.time(),
            'total_requests': 0,
            'successful_fallbacks': 0,
            'complete_failures': 0
        }
        self.logger.info("🔄 性能指标已重置")


class PerformanceOptimizedFallbackManager(CloudFallbackManager):
    """性能优化的Fallback管理器"""

    def __init__(self, config_path: Optional[str] = None, enable_monitoring: bool = True):
        """
        初始化性能优化的Fallback管理器

        Args:
            config_path: 配置文件路径
            enable_monitoring: 是否启用性能监控
        """
        super().__init__(config_path)

        self.monitor = FallbackPerformanceMonitor() if enable_monitoring else None
        self.adaptive_timeout = True
        self.circuit_breaker = {}  # 熔断器状态

    async def evaluate_with_fallback(self,
                                   model_family: str,
                                   prompt: str,
                                   context: Dict[str, Any]) -> EvaluationResult:
        """
        带性能监控的fallback评估

        Args:
            model_family: 模型系列
            prompt: 评估提示词
            context: 上下文信息

        Returns:
            评估结果
        """
        if model_family not in self.model_mapping:
            raise ValueError(f"不支持的模型系列: {model_family}")

        model_configs = self.model_mapping[model_family]
        fallback_chain_used = []

        for i, model_config in enumerate(model_configs):
            provider_key = f"{model_config.provider.value}:{model_config.model_name}"

            # 检查熔断器状态
            if self._is_circuit_open(provider_key):
                self.logger.warning(f"⚠️ 熔断器开启，跳过: {provider_key}")
                continue

            try:
                self.logger.info(f"尝试使用 {model_config.provider.value} 模型: {model_config.model_name}")

                # 自适应超时调整
                if self.adaptive_timeout:
                    adjusted_config = self._adjust_timeout(model_config)
                else:
                    adjusted_config = model_config

                start_time = time.time()
                result = await self._try_model(adjusted_config, prompt, context)
                result.response_time = time.time() - start_time

                if result.success:
                    fallback_chain_used.append(f"{model_config.provider.value}:{model_config.model_name}")

                    # 重置熔断器
                    self._reset_circuit_breaker(provider_key)

                    # 记录性能指标
                    if self.monitor:
                        self.monitor.record_metric(result, fallback_chain_used)

                    self.logger.info(
                        f"✅ 成功使用 {model_config.provider.value} - {model_config.model_name} "
                        f"(响应时间: {result.response_time:.2f}s)"
                    )
                    return result
                else:
                    self.logger.warning(
                        f"❌ {model_config.provider.value} 失败: {result.error_message}"
                    )
                    # 触发熔断器
                    self._trigger_circuit_breaker(provider_key)

            except Exception as e:
                self.logger.warning(
                    f"❌ {model_config.provider.value} 异常: {str(e)}"
                )
                # 触发熔断器
                self._trigger_circuit_breaker(provider_key)
                continue

        # 所有模型都失败
        fallback_result = EvaluationResult(
            success=False,
            scores={},
            provider=ModelProvider.LOCAL,
            model_name="none",
            response_time=0.0,
            error_message="所有模型都不可用"
        )

        # 记录失败指标
        if self.monitor:
            self.monitor.record_metric(fallback_result, fallback_chain_used)

        return fallback_result

    def _is_circuit_open(self, provider_key: str) -> bool:
        """检查熔断器是否开启"""
        if provider_key not in self.circuit_breaker:
            return False

        breaker = self.circuit_breaker[provider_key]

        # 如果在冷却期内，检查是否可以恢复
        if breaker['state'] == 'open':
            if time.time() - breaker['last_failure'] > breaker['cooldown']:
                breaker['state'] = 'half_open'
                return False
            return True

        return breaker['state'] == 'open'

    def _trigger_circuit_breaker(self, provider_key: str):
        """触发熔断器"""
        if provider_key not in self.circuit_breaker:
            self.circuit_breaker[provider_key] = {
                'failures': 0,
                'last_failure': 0,
                'state': 'closed',
                'cooldown': 300  # 5分钟冷却期
            }

        breaker = self.circuit_breaker[provider_key]
        breaker['failures'] += 1
        breaker['last_failure'] = time.time()

        # 连续失败3次触发熔断
        if breaker['failures'] >= 3:
            breaker['state'] = 'open'
            self.logger.warning(f"🔴 熔断器触发: {provider_key}")

    def _reset_circuit_breaker(self, provider_key: str):
        """重置熔断器"""
        if provider_key in self.circuit_breaker:
            self.circuit_breaker[provider_key] = {
                'failures': 0,
                'last_failure': 0,
                'state': 'closed',
                'cooldown': 300
            }

    def _adjust_timeout(self, model_config) -> ModelConfig:
        """自适应调整超时时间"""
        if not self.monitor:
            return model_config

        # 获取提供商历史平均响应时间
        provider_key = f"{model_config.provider.value}:{model_config.model_name}"
        if provider_key in self.monitor.provider_stats:
            stats = self.monitor.provider_stats[provider_key]
            # 使用历史平均响应时间的1.5倍作为新超时时间
            adaptive_timeout = max(30, min(300, stats.avg_response_time * 1.5))

            # 创建新的配置对象
            adjusted_config = ModelConfig(
                provider=model_config.provider,
                model_name=model_config.model_name,
                base_url=model_config.base_url,
                api_key=model_config.api_key,
                timeout=int(adaptive_timeout),
                max_retries=model_config.max_retries
            )

            self.logger.info(
                f"📊 自适应超时调整: {provider_key} "
                f"{model_config.timeout}s → {adjusted_config.timeout}s"
            )

            return adjusted_config

        return model_config

    def get_performance_dashboard(self) -> Dict:
        """获取性能仪表板数据"""
        if not self.monitor:
            return {"error": "性能监控未启用"}

        dashboard = self.monitor.get_performance_summary()

        # 添加熔断器状态
        dashboard['circuit_breaker_status'] = {
            provider: {
                'state': breaker['state'],
                'failures': breaker['failures'],
                'last_failure': datetime.fromtimestamp(breaker['last_failure']).isoformat() if breaker['last_failure'] > 0 else None
            }
            for provider, breaker in self.circuit_breaker.items()
        }

        # 添加健康评分
        dashboard['health_scores'] = {}
        for provider_key in self.monitor.provider_stats.keys():
            provider, model_name = provider_key.split(':', 1)
            dashboard['health_scores'][provider_key] = self.monitor.get_provider_health_score(provider, model_name)

        return dashboard