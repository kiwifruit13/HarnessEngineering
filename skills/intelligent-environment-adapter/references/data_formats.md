# 数据格式规范

## 概览

本文档定义了智能环境适配器Skill中所有输入输出数据的格式规范，包括JSON Schema、验证规则和示例数据。

## 目录

1. [环境画像格式](#环境画像格式)
2. [能力清单格式](#能力清单格式)
3. [映射结果格式](#映射结果格式)
4. [诊断报告格式](#诊断报告格式)
5. [补齐计划格式](#补齐计划格式)
6. [补齐建议格式](#补齐建议格式)
7. [成本预算格式](#成本预算格式)

---

## 环境画像格式

### JSON Schema

```json
{
  "type": "object",
  "properties": {
    "task_type": {
      "type": "string",
      "enum": ["信息检索", "深度分析", "内容创作", "问题解决"],
      "description": "任务类型"
    },
    "domain": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "涉及的领域列表"
    },
    "time_sensitivity": {
      "type": "string",
      "enum": ["静态", "实时", "预测"],
      "description": "时效性要求"
    },
    "data_type": {
      "type": "string",
      "enum": ["纯文本", "多模态", "大规模"],
      "description": "数据类型"
    },
    "complexity": {
      "type": "string",
      "enum": ["简单", "中等", "复杂", "极复杂"],
      "description": "任务复杂度"
    }
  },
  "required": ["task_type", "domain", "time_sensitivity", "data_type"]
}
```

### 示例数据

```json
{
  "task_type": "深度分析",
  "domain": ["法律", "AI技术"],
  "time_sensitivity": "实时",
  "data_type": "政策文档",
  "complexity": "复杂"
}
```

### 验证规则

1. `task_type` 必须是枚举值之一
2. `domain` 数组至少包含一个元素
3. `time_sensitivity` 必须是枚举值之一
4. `data_type` 必须是枚举值之一

---

## 能力清单格式

### JSON Schema

```json
{
  "type": "object",
  "properties": {
    "L1": {
      "type": "object",
      "properties": {
        "info_retrieval": {"type": "number", "minimum": 0, "maximum": 1},
        "data_source_availability": {"type": "number", "minimum": 0, "maximum": 1},
        "realtime_capability": {"type": "number", "minimum": 0, "maximum": 1}
      }
    },
    "L2": {
      "type": "object",
      "properties": {
        "analysis_depth": {"type": "number", "minimum": 0, "maximum": 1},
        "logical_reasoning": {"type": "number", "minimum": 0, "maximum": 1},
        "domain_knowledge": {"type": "number", "minimum": 0, "maximum": 1}
      }
    },
    "L3": {
      "type": "object",
      "properties": {
        "output_format": {"type": "number", "minimum": 0, "maximum": 1},
        "presentation_quality": {"type": "number", "minimum": 0, "maximum": 1},
        "multimodal_support": {"type": "number", "minimum": 0, "maximum": 1}
      }
    },
    "L4": {
      "type": "object",
      "properties": {
        "task_decomposition": {"type": "number", "minimum": 0, "maximum": 1},
        "skill_composition": {"type": "number", "minimum": 0, "maximum": 1},
        "state_management": {"type": "number", "minimum": 0, "maximum": 1}
      }
    },
    "L5": {
      "type": "object",
      "properties": {
        "feedback_mechanism": {"type": "number", "minimum": 0, "maximum": 1},
        "learning_capability": {"type": "number", "minimum": 0, "maximum": 1},
        "optimization_mechanism": {"type": "number", "minimum": 0, "maximum": 1}
      }
    }
  },
  "required": ["L1", "L2", "L3", "L4", "L5"]
}
```

### 示例数据

```json
{
  "L1": {
    "info_retrieval": 0.8,
    "data_source_availability": 0.6,
    "realtime_capability": 0.5
  },
  "L2": {
    "analysis_depth": 0.7,
    "logical_reasoning": 0.8,
    "domain_knowledge": 0.6
  },
  "L3": {
    "output_format": 0.9,
    "presentation_quality": 0.8,
    "multimodal_support": 0.8
  },
  "L4": {
    "task_decomposition": 0.8,
    "skill_composition": 0.8,
    "state_management": 0.8
  },
  "L5": {
    "feedback_mechanism": 0.7,
    "learning_capability": 0.8,
    "optimization_mechanism": 0.7
  }
}
```

### 验证规则

1. 所有评分必须在 0.0 到 1.0 之间
2. 每一层必须包含所有评估维度

---

## 映射结果格式

### JSON Schema

```json
{
  "type": "object",
  "properties": {
    "match_score": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "layer_scores": {
      "type": "object",
      "properties": {
        "L1": {"type": "number"},
        "L2": {"type": "number"},
        "L3": {"type": "number"},
        "L4": {"type": "number"},
        "L5": {"type": "number"}
      }
    },
    "shortages": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {"type": "string"},
          "layer": {"type": "string"},
          "type": {"type": "string"},
          "description": {"type": "string"},
          "severity": {"type": "string"},
          "impact_core": {"type": "boolean"}
        }
      }
    }
  },
  "required": ["match_score", "layer_scores", "shortages"]
}
```

### 示例数据

```json
{
  "match_score": 0.75,
  "layer_scores": {
    "L1": 0.65,
    "L2": 0.70,
    "L3": 0.85,
    "L4": 0.80,
    "L5": 0.75
  },
  "shortages": [
    {
      "id": "shortage_1",
      "layer": "L1",
      "type": "data_source_gap",
      "description": "缺乏实时政策数据源",
      "severity": "moderate",
      "impact_core": true
    },
    {
      "id": "shortage_2",
      "layer": "L2",
      "type": "knowledge_gap",
      "description": "缺乏法律专业知识",
      "severity": "critical",
      "impact_core": true
    }
  ]
}
```

### 验证规则

1. `match_score` 必须在 0.0 到 1.0 之间
2. `shortages` 数组中每个元素必须包含所有必需字段
3. `severity` 必须是 `critical`、`moderate` 或 `minor` 之一

---

## 诊断报告格式

### JSON Schema

```json
{
  "type": "object",
  "properties": {
    "diagnostic_report": {
      "type": "object",
      "properties": {
        "overall_status": {
          "type": "string",
          "enum": ["excellent", "good", "fair", "poor", "critical"]
        },
        "match_score": {"type": "number"},
        "critical_shortages_count": {"type": "integer"},
        "moderate_shortages_count": {"type": "integer"},
        "minor_shortages_count": {"type": "integer"},
        "shortage_details": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "id": {"type": "string"},
              "layer": {"type": "string"},
              "type": {"type": "string"},
              "description": {"type": "string"},
              "severity": {"type": "string"},
              "impact_core": {"type": "boolean"},
              "remediation_suggestions": {
                "type": "array",
                "items": {"type": "string"}
              }
            }
          }
        }
      }
    }
  }
}
```

### 示例数据

```json
{
  "diagnostic_report": {
    "overall_status": "fair",
    "match_score": 0.75,
    "critical_shortages_count": 1,
    "moderate_shortages_count": 1,
    "minor_shortages_count": 0,
    "shortage_details": [
      {
        "id": "shortage_1",
        "layer": "L1",
        "type": "data_source_gap",
        "description": "缺乏实时政策数据源",
        "severity": "moderate",
        "impact_core": true,
        "remediation_suggestions": [
          "搜索实时数据API",
          "集成政策数据源"
        ]
      },
      {
        "id": "shortage_2",
        "layer": "L2",
        "type": "knowledge_gap",
        "description": "缺乏法律专业知识",
        "severity": "critical",
        "impact_core": true,
        "remediation_suggestions": [
          "搜索法律分析技能",
          "构建法律知识图谱",
          "获取专业法律文档"
        ]
      }
    ]
  }
}
```

### 验证规则

1. `overall_status` 必须是枚举值之一
2. `remediation_suggestions` 数组不能为空

---

## 补齐计划格式

### JSON Schema

```json
{
  "type": "object",
  "properties": {
    "remediation_plan": {
      "type": "object",
      "properties": {
        "overall_strategy": {
          "type": "string",
          "enum": ["immediate", "planned", "degraded", "ignore"]
        },
        "actions": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "shortage_id": {"type": "string"},
              "strategy": {"type": "string"},
              "priority": {"type": "number"},
              "expected_improvement": {"type": "number"},
              "estimated_cost": {
                "type": "object",
                "properties": {
                  "time": {"type": "number"},
                  "tokens": {"type": "number"},
                  "compute": {"type": "string"}
                }
              },
              "execution_mode": {
                "type": "string",
                "enum": ["sequential", "parallel"]
              }
            }
          }
        },
        "total_estimated_cost": {
          "type": "object",
          "properties": {
            "time": {"type": "number"},
            "tokens": {"type": "number"},
            "compute": {"type": "string"}
          }
        }
      }
    }
  }
}
```

### 示例数据

```json
{
  "remediation_plan": {
    "overall_strategy": "mixed",
    "actions": [
      {
        "shortage_id": "shortage_1",
        "strategy": "build_domain_model",
        "priority": 0.9,
        "expected_improvement": 0.3,
        "estimated_cost": {
          "time": 120,
          "tokens": 5000,
          "compute": "low"
        },
        "execution_mode": "sequential"
      },
      {
        "shortage_id": "shortage_2",
        "strategy": "search_alternative_sources",
        "priority": 0.7,
        "expected_improvement": 0.15,
        "estimated_cost": {
          "time": 30,
          "tokens": 1000,
          "compute": "low"
        },
        "execution_mode": "parallel"
      }
    ],
    "total_estimated_cost": {
      "time": 150,
      "tokens": 6000,
      "compute": "low"
    }
  }
}
```

### 验证规则

1. `priority` 必须在 0.0 到 1.0 之间
2. `expected_improvement` 必须在 0.0 到 1.0 之间
3. `estimated_cost` 不能为空

---

## 补齐建议格式

### JSON Schema

```json
{
  "type": "object",
  "properties": {
    "remediation_suggestions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "suggestion_id": {"type": "string"},
          "type": {
            "type": "string",
            "enum": ["search_and_load_skill", "build_domain_model", "search_external_knowledge", "compose_multiple_skills", "delegate_to_human"]
          },
          "description": {"type": "string"},
          "priority": {"type": "number"},
          "expected_improvement": {"type": "number"},
          "requires_approval": {"type": "boolean"},
          "estimated_cost": {
            "type": "object",
            "properties": {
              "time": {"type": "number"},
              "tokens": {"type": "number"},
              "compute": {"type": "string"}
            }
          },
          "skill_query": {
            "type": "string",
            "description": "如果类型是search_and_load_skill，提供搜索查询"
          },
          "action_steps": {
            "type": "array",
            "items": {"type": "string"}
          }
        }
      }
    }
  }
}
```

### 示例数据

```json
{
  "remediation_suggestions": [
    {
      "suggestion_id": "suggestion_1",
      "type": "search_and_load_skill",
      "description": "搜索并加载法律分析相关的skill",
      "priority": 0.9,
      "expected_improvement": 0.3,
      "requires_approval": true,
      "estimated_cost": {
        "time": 45,
        "tokens": 1500,
        "compute": "low"
      },
      "skill_query": "法律分析 政策解读 专业文档",
      "action_steps": [
        "使用skill_search工具搜索相关skills",
        "评估候选skills的匹配度",
        "选择最优skill并请求用户审批",
        "加载skill并集成到工作流"
      ]
    },
    {
      "suggestion_id": "suggestion_2",
      "type": "build_domain_model",
      "description": "构建法律领域的知识模型",
      "priority": 0.8,
      "expected_improvement": 0.25,
      "requires_approval": false,
      "estimated_cost": {
        "time": 90,
        "tokens": 5000,
        "compute": "medium"
      },
      "action_steps": [
        "收集法律核心概念",
        "构建知识图谱",
        "验证模型完整性"
      ]
    }
  ]
}
```

### 验证规则

1. `requires_approval` 为 `true` 时，`type` 必须是 `search_and_load_skill` 或 `compose_multiple_skills`
2. 如果 `type` 是 `search_and_load_skill`，必须提供 `skill_query`
3. `action_steps` 数组不能为空

---

## 成本预算格式

### JSON Schema

```json
{
  "type": "object",
  "properties": {
    "cost_budget": {
      "type": "object",
      "properties": {
        "time_limit": {
          "type": "number",
          "description": "时间限制（秒）"
        },
        "token_limit": {
          "type": "number",
          "description": "Tokens限制"
        },
        "compute_limit": {
          "type": "string",
          "enum": ["low", "medium", "high"],
          "description": "计算资源限制"
        }
      }
    }
  }
}
```

### 示例数据

```json
{
  "cost_budget": {
    "time_limit": 300,
    "token_limit": 10000,
    "compute_limit": "medium"
  }
}
```

### 验证规则

1. `time_limit` 必须大于 0
2. `token_limit` 必须大于 0
3. `compute_limit` 必须是枚举值之一
