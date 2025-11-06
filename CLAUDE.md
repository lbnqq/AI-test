# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AgentPsyAssessment is a portable, comprehensive psychological assessment framework that combines various psychometric models (Big Five, MBTI, cognitive functions) with AI-powered analysis. The system has two main components:

1. **Assessment Component** - Uses LLMs to respond to psychological questionnaires with various parameters
2. **Analysis Component** - Evaluates responses to generate personality profiles and recommendations

## Core Architecture

### Main Entry Points

- **`production_pipelines/local_batch_production/cli.py`** - Primary CLI interface with `assess`, `analyze`, and `batch` commands
- **`llm_assessment/run_assessment_unified.py`** - Core assessment engine for individual evaluations
- **`production_pipelines/local_batch_production/run_batch_suite.py`** - Batch processing for multiple assessments

### Key Architectural Components

#### LLM Service Layer (`llm_assessment/services/`)
- **LLMClient** (`llm_client.py`) - Unified interface for multiple LLM providers (OpenAI, Anthropic, Ollama, Together AI)
- **ModelManager** (`model_manager.py`) - Centralized model management and service creation
- **Model Service Factory** - Abstract factory pattern for provider-agnostic model handling

#### Assessment Engine
- **Questionnaire System** (`test_files/`) - Big Five 50-item assessment, customer service scenarios, cognitive bias tests
- **Role System** (`llm_assessment/roles/`) - Personality role-playing profiles (a1-a10, b1-b10)
- **Prompt Builder** (`prompt_builder.py`) - Dynamic context-aware prompt generation

#### Analysis Engine
- **Big Five Analysis** (`shared_analysis/analyze_big5_results.py`) - OCEAN trait scoring and MBTI mapping
- **Batch Analysis** (`shared_analysis/batch_analysis.py`) - Multi-assessment aggregation and consistency analysis
- **Report Generation** - JSON exports, Markdown reports, statistical summaries

#### Production Pipelines
- **Local Batch Production** (`production_pipelines/local_batch_production/`) - High-throughput batch processing with error recovery
- **Cloud Fallback Enterprise** (`production_pipelines/cloud_fallback_enterprise/`) - Cloud-based processing with local fallback and multi-model consensus

## Common Development Commands

### Environment Setup
```bash
# Set provider (local or cloud)
export PROVIDER=local  # or cloud

# For local models (Ollama)
export LOCAL_API_BASE=http://localhost:11434
export LOCAL_MODEL_ID=llama3.1

# For cloud models
export OPENAI_API_KEY=your_key
export ANTHROPIC_API_KEY=your_key
```

### Single Assessment
```bash
# Local model assessment
python llm_assessment/run_assessment_unified.py --model llama3.1 --role a1

# Cloud model assessment
python llm_assessment/run_assessment_unified.py --model gpt-4o --role def --provider cloud

# With specific parameters
python llm_assessment/run_assessment_unified.py --model claude-3-5-sonnet --role a1 --temperature 0.2
```

### Batch Processing
```bash
# Batch suite with multiple roles
python production_pipelines/local_batch_production/run_batch_suite.py --model llama3.1 --roles a1,a2,b1

# Enhanced batch processing
python batch_processor.py --input-dir results/readonly-original --output-dir results/filtered-results --enhanced

# Optimized batch with limits
python optimized_batch_processor.py --input-dir results/readonly-original --output-dir results/optimized --max-questions 10 --enhanced
```

### Analysis Operations
```bash
# Analyze single assessment
python shared_analysis/analyze_big5_results.py --input results/assessment_result.json

# Batch analysis
python shared_analysis/batch_analysis.py --input-dir results/batch_results --output-dir results/analysis

# Comprehensive analysis
python cli.py analyze --input results/latest_assessment.json --analysis-type comprehensive
```

### Production Pipeline Commands
```bash
# Main CLI operations
python production_pipelines/local_batch_production/cli.py assess --model gpt-4o --role def
python production_pipelines/local_batch_production/cli.py analyze --input results/assessment.json
python production_pipelines/local_batch_production/cli.py batch --model llama3.1 --roles a1,a2,b1

# End-to-end testing
python test_end_to_end_complete.py
python test_optimized_processor.py
```

### Cloud Pipeline Testing
```bash
# Quick cloud test
python quick_cloud_test.py

# Full cloud pipeline test
python test_cloud_pipeline.py

# Transparent pipeline testing
python -c "
from single_report_pipeline.transparent_pipeline import TransparentPipeline
pipeline = TransparentPipeline(use_cloud=True)
# ... test individual components
"
```

## Configuration

### Model Configuration (`config/ollama_config.json`)
- **Local Models**: mistral, phi3_mini, qwen3_4b via Ollama
- **Cloud Models**: glm_4_6_cloud, deepseek_v3_1_cloud, qwen3_vl_cloud, gpt_oss_120b_cloud
- **Evaluators**: Multi-model consensus configuration with dispute resolution
- **Settings**: Temperature, max tokens, timeout configurations

### Role Configuration (`llm_assessment/roles/`)
- **Analytical Roles**: a1-a10 for different personality configurations
- **Behavioral Roles**: b1-b10 for behavioral patterns
- **Multilingual**: Chinese and English variants

### Environment Variables
- **PROVIDER**: `local` or `cloud`
- **LOCAL_API_BASE**: Ollama server URL (default: http://localhost:11434)
- **LOCAL_MODEL_ID**: Default local model identifier
- **Cloud API Keys**: OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.

## System Workflows

### Single Assessment Flow
```
CLI → Assessment Runner → LLM Client → Model Service → Questionnaire → Response Extraction → Result Storage
```

### Batch Processing Flow
```
CLI → Batch Suite → Concurrent Assessment Tasks → Result Collection → Analysis → Aggregation → Report Generation
```

### Multi-Model Evaluation Flow
```
Assessment → Multiple Model Evaluation → Consensus Building → Reliability Scoring → Final Report
```

## Data Processing and Results

### Input Formats
- **Assessment Results**: JSON files with questionnaire responses and metadata
- **Batch Directories**: Collections of assessment results for bulk processing
- **Configuration Files**: Model settings, role definitions, analysis parameters

### Output Formats
- **Evaluation Results**: JSON with Big Five scores, MBTI types, confidence metrics
- **Analysis Reports**: Comprehensive personality profiles with recommendations
- **Batch Summaries**: Statistical aggregations across multiple assessments

### Key Result Locations
- **Raw Results**: `results/readonly-original/` - Original assessment data
- **Processed Results**: `results/ok/evaluated/` - Analyzed evaluation results
- **Batch Analysis**: `results/final-*-batch-analysis/` - Batch processing outputs

## Development Notes

### Error Handling and Recovery
- **Retry Mechanisms**: Multiple retry attempts with exponential backoff
- **Fallback Systems**: Cloud models fallback to local models on failure
- **Checkpoint System**: Resume processing from intermediate states
- **Quality Validation**: Cross-model verification and reliability scoring

### Concurrent Processing
- **Multi-threading**: Concurrent assessment processing for batch operations
- **Resource Management**: Optimized model usage and API rate limiting
- **Memory Efficiency**: Streaming processing for large datasets

### Quality Assurance
- **Multi-Model Consensus**: Multiple models evaluate same responses for reliability
- **Statistical Validation**: Consistency checks and confidence scoring
- **Result Verification**: Cross-validation between different evaluation methods

## Testing and Validation

### Unit Testing
```bash
python production_pipelines/cloud_fallback_enterprise/single_report_pipeline/test_modular_integration.py
python production_pipelines/cloud_fallback_enterprise/single_report_pipeline/test_complete_flow.py
```

### Integration Testing
```bash
python test_end_to_end_complete.py
python test_optimized_processor.py
python test_cloud_pipeline.py
```

### Pipeline Validation
```bash
python production_pipelines/cloud_fallback_enterprise/single_report_pipeline/validate_complete_system.py
python production_pipelines/cloud_fallback_enterprise/single_report_pipeline/validate_enhanced_features.py
```

## Performance Optimization

### Batch Processing Optimization
- Use `--max-questions` to limit processing scope for testing
- Enable `--enhanced` mode for improved accuracy
- Configure appropriate concurrency limits based on API rate limits

### Memory Management
- Process large datasets in chunks
- Use streaming for file operations
- Monitor resource usage during batch operations

### Model Selection Guidelines
- **Local Models**: Faster processing, limited capabilities, suitable for testing
- **Cloud Models**: Higher accuracy, API costs, suitable for production
- **Hybrid Approach**: Cloud models with local fallback for reliability

## Troubleshooting

### Common Issues
- **Model Loading**: Check Ollama service status and model availability
- **API Authentication**: Verify environment variables and API keys
- **Memory Issues**: Reduce batch size or enable checkpoint processing
- **Network Timeouts**: Increase timeout values for large assessments

### Debug Commands
```bash
# Check model availability
python production_pipelines/cloud_fallback_enterprise/single_report_pipeline/test_available_models.py

# Debug individual components
python production_pipelines/cloud_fallback_enterprise/single_report_pipeline/debug_reverse_logic.py

# Validate pipeline integrity
python production_pipelines/cloud_fallback_enterprise/single_report_pipeline/validate_pipeline_real_data.py
```

### Log Analysis
- Assessment logs include detailed error information and retry attempts
- Batch processing logs provide progress tracking and performance metrics
- Cloud fallback logs help identify provider-specific issues

## Internationalization

The system supports both Chinese and English:
- **Multilingual Roles**: Role configurations available in both languages
- **Localized Prompts**: Context-aware prompts based on language preference
- **Unicode Support**: Full UTF-8 support for international characters
- **Cultural Adaptation**: Assessment questions adapted for different cultural contexts