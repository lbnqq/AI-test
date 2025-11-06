# TPE QA Analyzer 使用指南

## 简介

TPE QA Analyzer 是一个用于分析 TPE (Targeted Pressure Executor) 工具生成的 JSON 日志文件的命令行工具。它通过对模型响应进行关键词匹配、规则检测和统计分析，提供定量的评估报告，帮助研究人员评估模型在压力测试下的角色一致性、稳定性和响应质量。

## 安装

1. 确保已安装 Python 3.7+。
2. （可选，但推荐）在虚拟环境中安装依赖。

## 快速开始

```bash
# 假设你已经运行过 TPE 并生成了一个日志文件
python analyze_tpe_log.py --log_file sample_log.json --output_dir reports
```

这将在 `reports` 目录下生成分析报告。

## 使用方法

### 命令行参数

* `--log_file LOG_FILE`: (必需) TPE 生成的 JSON 日志文件路径。
* `--output_dir OUTPUT_DIR`: (可选) 分析报告的输出目录。默认为 `./analysis_reports`。
* `--config CONFIG`: (可选) 自定义配置文件路径。默认加载 `config/config.json`。

### 配置

工具的行为主要通过 `config/config.json` 和 `config/keywords/` 目录下的词典文件进行配置。用户可以修改这些文件来自定义关键词、禁语和分析规则。

初始配置包含了针对项目中已有角色（如a1, b1）和常见冲突类型（如Duty vs. Empathy）的关键词词典。用户可以根据需要扩展这些词典以适应特定的分析需求。

## 运行测试

```bash
# 运行所有单元测试
python run_tests.py
```

## 生成的报告

工具会生成三种格式的报告：
1. CSV 格式：包含详细的分析数据表
2. JSON 格式：结构化的数据报告，便于程序处理
3. Markdown 格式：易读的摘要报告

## 开发

本项目遵循 TDD (测试驱动开发) 原则。所有核心功能均需先编写测试用例。

* 运行测试: `python run_tests.py`