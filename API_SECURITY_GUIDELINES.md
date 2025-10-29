# API密钥安全使用说明

## 重要安全提醒

⚠️ 为了保护您的API密钥安全，请遵循以下最佳实践：

1. **绝对不要**将API密钥硬编码在源代码中
2. **绝对不要**将API密钥提交到版本控制系统
3. **仅使用**环境变量来管理API密钥

## 正确配置API密钥

### 方法1：环境变量
在系统中设置环境变量：

**Linux/macOS:**
```bash
export OPENROUTER_API_KEY="your_actual_api_key_here"
export OLLAMA_BASE_URL="http://localhost:11434"  # 如果使用Ollama
```

**Windows:**
```cmd
set OPENROUTER_API_KEY=your_actual_api_key_here
set OLLAMA_BASE_URL=http://localhost:11434
```

### 方法2：.env文件
1. 复制 `.env.example` 为 `.env`:
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，添加您的实际API密钥

3. 确保 `.env` 文件不在版本控制中（已添加到 `.gitignore`）

## 多级API重试机制

我们的系统包含以下重试机制：

1. **首选服务**: OpenRouter API
2. **备选服务**: Ollama本地API
3. **自动回退**: 如果首选服务失败，系统自动尝试备选服务
4. **指数退避**: 在重试之间使用指数退避策略

## 模型优先级

### 云模型（按优先级）
- Google Gemini 2.0 Flash (高上下文)
- DeepSeek R1
- Qwen3 235B
- Mistral Small
- Llama 3.3 70B
- Moonshot Kimi K2

### Ollama本地模型（备选）
- Qwen3 4B
- Gemma2 2B
- Llama3.2 3B
- Mistral 7B

## 注意事项

- 所有API密钥现在仅通过环境变量获取
- 系统支持多级重试和自动故障转移
- 如果没有配置API密钥，系统会提示相应的错误信息
- 可以通过OLLAMA_BASE_URL环境变量自定义Ollama服务地址

## 重新生成密钥

如果您的密钥已经泄露，请立即：
1. 登录到相应服务提供商的网站
2. 撤销/轮换现有的API密钥
3. 生成新的API密钥
4. 按照上述方法配置新密钥