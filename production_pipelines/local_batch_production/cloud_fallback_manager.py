#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云模型优先替补管理器
实现三层fallback策略：Ollama云模型 → OpenRouter → 本地模型
"""

import os
import json
import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import time


class ModelProvider(Enum):
    """模型提供商枚举"""
    OLLAMA_CLOUD = "ollama_cloud"
    OPENROUTER = "openrouter"
    LOCAL = "local"


@dataclass
class ModelConfig:
    """模型配置"""
    provider: ModelProvider
    model_name: str
    base_url: str
    api_key: Optional[str] = None
    timeout: int = 60
    max_retries: int = 2


@dataclass
class EvaluationResult:
    """评估结果"""
    success: bool
    scores: Dict[str, int]
    provider: ModelProvider
    model_name: str
    response_time: float
    error_message: Optional[str] = None


class FallbackException(Exception):
    """Fallback过程中的异常"""
    pass


class ModelUnavailableError(FallbackException):
    """模型不可用异常"""
    pass


class TimeoutError(FallbackException):
    """超时异常"""
    pass


class CloudFallbackManager:
    """云模型优先替补管理器"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化Fallback管理器

        Args:
            config_path: 配置文件路径，默认使用config/model_fallback.yaml
        """
        self.logger = self._setup_logger()
        self.model_mapping = self._load_model_mapping(config_path)
        self.timeout_config = self._load_timeout_config()
        self.session = None

    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger("CloudFallbackManager")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _load_model_mapping(self, config_path: Optional[str]) -> Dict[str, List[ModelConfig]]:
        """加载模型映射配置"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            # 使用默认配置
            config = self._get_default_config()

        model_mapping = {}
        for brand, models in config['model_fallback_mapping'].items():
            model_mapping[brand] = []
            for provider_config in models:
                provider = ModelProvider(provider_config['provider'])
                model_config = ModelConfig(
                    provider=provider,
                    model_name=provider_config['model_name'],
                    base_url=provider_config['base_url'],
                    api_key=provider_config.get('api_key'),
                    timeout=provider_config.get('timeout', 60)
                )
                model_mapping[brand].append(model_config)

        return model_mapping

    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "model_fallback_mapping": {
                "qwen": [
                    {
                        "provider": "ollama_cloud",
                        "model_name": "qwen2.5:latest",
                        "base_url": "https://api.ollama.ai",
                        "api_key": os.getenv("OLLAMA_CLOUD_API_KEY"),
                        "timeout": 60
                    },
                    {
                        "provider": "openrouter",
                        "model_name": "qwen/qwen-2.5-72b-instruct",
                        "base_url": "https://openrouter.ai/api/v1",
                        "api_key": os.getenv("OPENROUTER_API_KEY"),
                        "timeout": 90
                    },
                    {
                        "provider": "local",
                        "model_name": "qwen2.5:latest",
                        "base_url": "http://localhost:11434",
                        "timeout": 120
                    }
                ],
                "deepseek": [
                    {
                        "provider": "ollama_cloud",
                        "model_name": "deepseek-r1:70b",
                        "base_url": "https://api.ollama.ai",
                        "api_key": os.getenv("OLLAMA_CLOUD_API_KEY"),
                        "timeout": 60
                    },
                    {
                        "provider": "openrouter",
                        "model_name": "deepseek/deepseek-r1-distill-llama-70b",
                        "base_url": "https://openrouter.ai/api/v1",
                        "api_key": os.getenv("OPENROUTER_API_KEY"),
                        "timeout": 90
                    },
                    {
                        "provider": "local",
                        "model_name": "deepseek-r1:8b",
                        "base_url": "http://localhost:11434",
                        "timeout": 120
                    }
                ]
            },
            "timeout_config": {
                "ollama_cloud": 60,
                "openrouter": 90,
                "local": 120
            },
            "retry_config": {
                "max_retries": 2,
                "retry_delay": 5,
                "exponential_backoff": True
            }
        }

    def _load_timeout_config(self) -> Dict:
        """加载超时配置"""
        return self._get_default_config()['timeout_config']

    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()

    async def evaluate_with_fallback(self,
                                   model_family: str,
                                   prompt: str,
                                   context: Dict[str, Any]) -> EvaluationResult:
        """
        带fallback的评估调用

        Args:
            model_family: 模型系列 (如 'qwen', 'deepseek')
            prompt: 评估提示词
            context: 上下文信息

        Returns:
            EvaluationResult: 评估结果
        """
        if model_family not in self.model_mapping:
            raise ValueError(f"不支持的模型系列: {model_family}")

        model_configs = self.model_mapping[model_family]

        for i, model_config in enumerate(model_configs):
            try:
                self.logger.info(f"尝试使用 {model_config.provider.value} 模型: {model_config.model_name}")

                result = await self._try_model(model_config, prompt, context)

                if result.success:
                    self.logger.info(
                        f"✅ 成功使用 {model_config.provider.value} - {model_config.model_name} "
                        f"(响应时间: {result.response_time:.2f}s)"
                    )
                    return result
                else:
                    self.logger.warning(
                        f"❌ {model_config.provider.value} 失败: {result.error_message}"
                    )

            except Exception as e:
                self.logger.warning(
                    f"❌ {model_config.provider.value} 异常: {str(e)}"
                )
                continue

        # 所有模型都失败
        return EvaluationResult(
            success=False,
            scores={},
            provider=ModelProvider.LOCAL,
            model_name="none",
            response_time=0.0,
            error_message="所有模型都不可用"
        )

    async def _try_model(self,
                        model_config: ModelConfig,
                        prompt: str,
                        context: Dict[str, Any]) -> EvaluationResult:
        """
        尝试使用特定模型进行评估

        Args:
            model_config: 模型配置
            prompt: 评估提示词
            context: 上下文信息

        Returns:
            EvaluationResult: 评估结果
        """
        start_time = time.time()

        try:
            if model_config.provider == ModelProvider.OLLAMA_CLOUD:
                result = await self._try_ollama_cloud(model_config, prompt, context)
            elif model_config.provider == ModelProvider.OPENROUTER:
                result = await self._try_openrouter(model_config, prompt, context)
            elif model_config.provider == ModelProvider.LOCAL:
                result = await self._try_local_model(model_config, prompt, context)
            else:
                raise ValueError(f"不支持的提供商: {model_config.provider}")

            response_time = time.time() - start_time
            result.response_time = response_time
            return result

        except asyncio.TimeoutError:
            response_time = time.time() - start_time
            return EvaluationResult(
                success=False,
                scores={},
                provider=model_config.provider,
                model_name=model_config.model_name,
                response_time=response_time,
                error_message="请求超时"
            )
        except Exception as e:
            response_time = time.time() - start_time
            return EvaluationResult(
                success=False,
                scores={},
                provider=model_config.provider,
                model_name=model_config.model_name,
                response_time=response_time,
                error_message=str(e)
            )

    async def _try_ollama_cloud(self,
                               model_config: ModelConfig,
                               prompt: str,
                               context: Dict[str, Any]) -> EvaluationResult:
        """尝试Ollama云模型"""
        # Phase 1: 实现Ollama云模型调用
        self.logger.info(f"🌩️ 调用Ollama云模型: {model_config.model_name}")

        # TODO: 实现具体的Ollama云API调用
        # 这里先返回模拟结果
        await asyncio.sleep(1)  # 模拟网络延迟

        return EvaluationResult(
            success=True,
            scores={
                'openness_to_experience': 4,
                'conscientiousness': 3,
                'extraversion': 5,
                'agreeableness': 3,
                'neuroticism': 2
            },
            provider=ModelProvider.OLLAMA_CLOUD,
            model_name=model_config.model_name,
            response_time=0.0
        )

    async def _try_openrouter(self,
                             model_config: ModelConfig,
                             prompt: str,
                             context: Dict[str, Any]) -> EvaluationResult:
        """尝试OpenRouter模型"""
        # Phase 2: 实现OpenRouter API调用
        self.logger.info(f"🔗 调用OpenRouter模型: {model_config.model_name}")

        if not model_config.api_key:
            raise ValueError("OpenRouter API密钥未配置")

        try:
            # 构建OpenRouter API请求
            headers = {
                "Authorization": f"Bearer {model_config.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/portable-psyagent",
                "X-Title": "Big Five Personality Assessment"
            }

            # 构建评估提示词
            evaluation_prompt = self._build_evaluation_prompt(prompt, context)

            payload = {
                "model": model_config.model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的大五人格评估专家。请根据用户的回答，评估其在五个维度上的得分(1-5分)。"
                    },
                    {
                        "role": "user",
                        "content": evaluation_prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 500
            }

            # 发送请求
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{model_config.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=model_config.timeout)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"OpenRouter API错误: {response.status} - {error_text}")

                    result_data = await response.json()

                    # 解析响应
                    scores = self._parse_openrouter_response(result_data)

                    self.logger.info(f"✅ OpenRouter评估成功: {scores}")

                    return EvaluationResult(
                        success=True,
                        scores=scores,
                        provider=ModelProvider.OPENROUTER,
                        model_name=model_config.model_name,
                        response_time=0.0
                    )

        except asyncio.TimeoutError:
            raise Exception("OpenRouter API调用超时")
        except Exception as e:
            self.logger.error(f"❌ OpenRouter调用失败: {str(e)}")
            raise Exception(f"OpenRouter API调用失败: {str(e)}")

    def _build_evaluation_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """构建评估提示词"""
        question_id = context.get("question_id", "Unknown")
        concept = context.get("concept", "")
        is_reversed = context.get("is_reversed", False)

        evaluation_prompt = f"""
请根据以下内容，评估用户的大五人格特质得分(1-5分):

题目ID: {question_id}
概念: {concept}
是否反向计分: {is_reversed}
用户回答: {prompt}

请以JSON格式返回评估结果，包含以下五个维度的得分：
- openness_to_experience (开放性)
- conscientiousness (尽责性)
- extraversion (外向性)
- agreeableness (宜人性)
- neuroticism (神经质)

每个维度得分范围为1-5分，其中1分表示该特质表现很弱，5分表示该特质表现很强。
如果是反向计分题目，请相应调整评分逻辑。

返回格式:
{{"openness_to_experience": 数值, "conscientiousness": 数值, "extraversion": 数值, "agreeableness": 数值, "neuroticism": 数值}}
"""
        return evaluation_prompt

    def _parse_openrouter_response(self, response_data: Dict) -> Dict[str, int]:
        """解析OpenRouter响应"""
        try:
            content = response_data["choices"][0]["message"]["content"]

            # 尝试解析JSON响应
            import json
            import re

            # 查找JSON模式
            json_match = re.search(r'\{[^}]+\}', content)
            if json_match:
                scores_json = json_match.group(0)
                scores = json.loads(scores_json)

                # 验证并清理分数
                cleaned_scores = {}
                for dimension, score in scores.items():
                    if dimension in ['openness_to_experience', 'conscientiousness',
                                   'extraversion', 'agreeableness', 'neuroticism']:
                        try:
                            score_int = int(score)
                            if 1 <= score_int <= 5:
                                cleaned_scores[dimension] = score_int
                            else:
                                cleaned_scores[dimension] = 3  # 默认中性分
                        except (ValueError, TypeError):
                            cleaned_scores[dimension] = 3

                # 确保所有维度都有值
                for dimension in ['openness_to_experience', 'conscientiousness',
                                 'extraversion', 'agreeableness', 'neuroticism']:
                    if dimension not in cleaned_scores:
                        cleaned_scores[dimension] = 3

                return cleaned_scores
            else:
                # 如果无法解析JSON，返回默认分数
                self.logger.warning("无法解析OpenRouter响应JSON，使用默认分数")
                return {
                    'openness_to_experience': 3,
                    'conscientiousness': 3,
                    'extraversion': 3,
                    'agreeableness': 3,
                    'neuroticism': 3
                }

        except (KeyError, IndexError, json.JSONDecodeError) as e:
            self.logger.error(f"解析OpenRouter响应失败: {str(e)}")
            return {
                'openness_to_experience': 3,
                'conscientiousness': 3,
                'extraversion': 3,
                'agreeableness': 3,
                'neuroticism': 3
            }

    async def _try_local_model(self,
                              model_config: ModelConfig,
                              prompt: str,
                              context: Dict[str, Any]) -> EvaluationResult:
        """尝试本地模型"""
        # Phase 3: 实现本地模型调用
        self.logger.info(f"🏠 调用本地模型: {model_config.model_name}")

        try:
            # 构建本地Ollama API请求
            headers = {
                "Content-Type": "application/json"
            }

            # 构建评估提示词
            evaluation_prompt = self._build_evaluation_prompt(prompt, context)

            payload = {
                "model": model_config.model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的大五人格评估专家。请根据用户的回答，评估其在五个维度上的得分(1-5分)。"
                    },
                    {
                        "role": "user",
                        "content": evaluation_prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 500,
                "stream": False
            }

            # 发送请求到本地Ollama服务
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{model_config.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=model_config.timeout)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"本地Ollama API错误: {response.status} - {error_text}")

                    result_data = await response.json()

                    # 解析响应
                    scores = self._parse_openrouter_response(result_data)  # 复用OpenRouter的解析逻辑

                    self.logger.info(f"✅ 本地Ollama评估成功: {scores}")

                    return EvaluationResult(
                        success=True,
                        scores=scores,
                        provider=ModelProvider.LOCAL,
                        model_name=model_config.model_name,
                        response_time=0.0
                    )

        except asyncio.TimeoutError:
            raise Exception("本地Ollama API调用超时")
        except aiohttp.ClientConnectorError:
            raise Exception("本地Ollama服务不可达，请确认服务已启动")
        except Exception as e:
            self.logger.error(f"❌ 本地Ollama调用失败: {str(e)}")
            raise Exception(f"本地Ollama API调用失败: {str(e)}")

    async def check_local_model_availability(self, model_config: ModelConfig) -> bool:
        """检查本地模型可用性"""
        try:
            headers = {"Content-Type": "application/json"}

            # 使用Ollama的tags API检查模型是否可用
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{model_config.base_url}/api/tags",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        models_data = await response.json()
                        available_models = [model['name'].split(':')[0] for model in models_data.get('models', [])]
                        return model_config.model_name.split(':')[0] in available_models
                    else:
                        return False
        except Exception as e:
            self.logger.warning(f"检查本地模型可用性失败: {str(e)}")
            return False

    def get_supported_models(self) -> List[str]:
        """获取支持的模型系列"""
        return list(self.model_mapping.keys())

    def get_fallback_chain(self, model_family: str) -> List[str]:
        """获取指定模型系列的fallback链"""
        if model_family not in self.model_mapping:
            return []

        return [
            f"{config.provider.value}:{config.model_name}"
            for config in self.model_mapping[model_family]
        ]


# 工厂函数
async def create_fallback_manager(config_path: Optional[str] = None) -> CloudFallbackManager:
    """创建并初始化Fallback管理器"""
    manager = CloudFallbackManager(config_path)
    await manager.__aenter__()
    return manager