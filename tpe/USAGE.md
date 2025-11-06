### **Targeted Pressure Executor (TPE) - 使用说明**

#### **核心定位**
`TPE` (Targeted Pressure Executor) 是一个**独立的、专注于执行**的命令行工具。它的核心职责是：**接收一个针对特定LLM（指定模型）或其特定角色扮演（指定模型+角色）的“定向压力测试计划”，并执行该计划，记录模型的原始响应。**

#### **设计哲学 (KISS & SRP)**
`TPE` 严格遵循 KISS (Keep It Simple, Stupid) 和 SRP (Single Responsibility Principle) 原则。
*   **它不负责：**
    *   分析模型的基础人格或角色扮演能力。
    *   生成压力测试计划。
    *   分析执行后的测试结果。
*   **它只负责：**
    *   **精准执行**一个由上游工具（如 `generate_pressure_plan.py`）提供的、**预定义的**压力测试计划。

#### **应用场景与工作流**

`TPE` 是一个压力测试工作流的**下游执行环节**。完整的工作流通常如下：

```
[基础人格分析] --> [生成针对性压力计划] --> [TPE执行计划] --> [结果分析]
      |                                          ^
      |                                          |
      |                              (模型名, 角色名, 计划文件)
      |                                          |
      +--> [角色扮演能力评估] --> [生成针对性压力计划] --+
```

**场景一：测试模型的“基础/先天”人格**
1.  **分析**: 使用 `run_assessment_unified.py` 等工具，让**未加载任何特定角色**的模型（即其“出厂设置”或基础人格）完成 Big Five 等心理评估问卷。
2.  **计划生成**: 使用 `analyze_results.py` 分析评估结果，得到模型基础人格的 Big Five 向量。然后，使用 `generate_pressure_plan.py` 基于此向量，从 `pressure_test_bank.json` 中挑选出最能针对该模型潜在弱点或特质的场景，生成一个 Markdown 格式的压力测试计划文件（例如 `model_xyz_baseline_pressure_plan.md`）。
3.  **执行 (`TPE`)**:
    *   **命令**: `python run_tpe.py --model_name "ollama/model_xyz:latest" --role_name "default" --plan_file "path/to/model_xyz_baseline_pressure_plan.md"`
    *   **行为**: `TPE` 会加载模型，应用 "default"（即无）角色，解析并依次执行 `model_xyz_baseline_pressure_plan.md` 中的每个场景，将模型的原始响应记录到一个结构化的 JSON 日志中。

**场景二：测试模型的“特定/扮演”人格**
1.  **评估**: 使用 `run_assessment_unified.py` 等工具，让模型**加载并扮演**一个特定角色（例如 `a1.txt` 定义的“审计师”）完成心理评估问卷，评估其角色扮演的稳定性和深度。
2.  **计划生成**: 确认模型能稳定扮演该角色后，使用 `analyze_results.py` 分析其在角色状态下的表现，得到其“扮演人格”的 Big Five 向量。然后，使用 `generate_pressure_plan.py` 为此向量生成压力计划（例如 `model_xyz_as_a1_pressure_plan.md`）。
3.  **执行 (`TPE`)**:
    *   **命令**: `python run_tpe.py --model_name "ollama/model_xyz:latest" --role_name "a1" --plan_file "path/to/model_xyz_as_a1_pressure_plan.md"`
    *   **行为**: `TPE` 会加载模型，应用 `roles/a1.txt` 中定义的角色指令作为系统提示，然后解析并执行 `model_xyz_as_a1_pressure_plan.md` 中的场景，记录响应。

#### **核心输入参数**

`TPE` 的设计围绕三个核心输入参数展开，它们共同定义了“**针对谁，在什么设定下，进行什么测试**”：

1.  **`--model_name`**:
    *   **含义**: 指定要进行压力测试的 LLM 模型标识符。
    *   **示例**: `ollama/gemma3:latest`, `cloud/gpt-4`, `local/my_custom_model`

2.  **`--role_name`**:
    *   **含义**: 指定模型在执行测试时应扮演的角色。角色定义存储在 `roles/` 目录下的 `.txt` 文件中。如果设置为 `default` 或留空，则不应用任何特定角色。
    *   **示例**: `a1`, `b2`, `default`

3.  **`--plan_file`**:
    *   **含义**: 指向一个 **Markdown 格式** 的压力测试计划文件。此文件是整个测试流程的**核心输入**，它精确地定义了要执行的测试场景。
    *   **来源**: 此文件应由上游工具（例如 `generate_pressure_plan.py`）生成。
    *   **示例**: `path/to/pressure_plan_for_model_X_with_role_Y.md`

#### **总结**

`TPE` 的强大之处在于其**解耦和聚焦**。它本身不关心模型的基础人格或角色是如何被分析和选择的，它只关心如何**精确、可靠地执行一个给定的、针对性的测试指令序列**。这种设计使得 `TPE` 成为了整个压力测试 pipeline 中一个稳定、可复用的执行引擎。