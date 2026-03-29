# Function Calling 常见陷阱与解决方案

## 目录
1. [参数生成问题](#参数生成问题)
2. [函数调用问题](#函数调用问题)
3. [结果处理问题](#结果处理问题)
4. [性能问题](#性能问题)
5. [安全问题](#安全问题)

## 概览
本文档列举 Function Calling 开发中常见的陷阱和错误，提供识别方法和解决方案，帮助开发者避免典型问题。

## 参数生成问题

### 陷阱 1：必填参数缺失
**问题描述**：
模型生成的参数中缺少必填字段，导致函数调用失败。

**常见原因**：
- 函数描述不够清晰，模型未能理解参数的必要性
- 参数描述过于简略，模型不知道该参数的作用
- 模型认为可以从上下文推断该参数值

**解决方案**：
1. 在参数描述中明确说明为什么该参数是必需的
2. 提供参数的示例值或默认值说明
3. 在函数描述中强调该参数的作用

**示例**：
```json
{
  "name": "get_weather",
  "parameters": {
    "properties": {
      "location": {
        "type": "string",
        "description": "城市名称（必需），无法从上下文推断，必须由用户提供。支持中文和英文，如'北京'、'Shanghai'"
      }
    },
    "required": ["location"]
  }
}
```

### 陷阱 2：参数类型错误
**问题描述**：
模型生成的参数类型与 Schema 定义不符，如应该为数字却生成了字符串。

**常见原因**：
- 参数类型定义不明确
- 描述中使用了模糊的表述
- 模型对类型理解有偏差

**解决方案**：
1. 在描述中明确说明参数类型和格式
2. 提供类型示例
3. 使用枚举限制取值范围

**示例**：
```json
{
  "name": "calculate",
  "parameters": {
    "properties": {
      "a": {
        "type": "number",
        "description": "第一个操作数，必须是数字（整数或小数），如 10、3.14、-5"
      },
      "b": {
        "type": "number",
        "description": "第二个操作数，必须是数字（整数或小数），如 10、3.14、-5"
      }
    },
    "required": ["a", "b"]
  }
}
```

### 陷阱 3：枚举值超出范围
**问题描述**：
模型生成的参数值不在枚举定义的范围内。

**常见原因**：
- 枚举描述不清晰
- 枚举值命名不够直观
- 缺少枚举值的详细说明

**解决方案**：
1. 为每个枚举值提供清晰的描述
2. 在参数描述中列举所有合法值
3. 使用有意义的枚举值名称

**示例**：
```json
{
  "name": "set_user_status",
  "parameters": {
    "properties": {
      "status": {
        "type": "string",
        "enum": ["active", "inactive", "suspended", "deleted"],
        "description": "用户状态，必须是以下四个值之一：'active'（激活）、'inactive'（未激活）、'suspended'（暂停）、'deleted'（已删除）"
      }
    }
  }
}
```

### 陷阱 4：参数格式错误
**问题描述**：
参数类型正确但格式不符合要求，如日期格式错误、邮箱格式错误。

**常见原因**：
- 格式要求未在描述中说明
- 缺少格式示例
- 模型对特定格式理解不足

**解决方案**：
1. 明确说明参数的格式要求
2. 提供格式示例
3. 对特殊格式进行详细说明

**示例**：
```json
{
  "name": "schedule_meeting",
  "parameters": {
    "properties": {
      "date": {
        "type": "string",
        "description": "会议日期，格式必须为 YYYY-MM-DD，如 2024-03-16"
      },
      "time": {
        "type": "string",
        "description": "会议时间，格式必须为 HH:MM，使用24小时制，如 14:30"
      },
      "email": {
        "type": "string",
        "description": "联系邮箱，格式必须符合标准邮箱格式，如 user@example.com"
      }
    }
  }
}
```

## 函数调用问题

### 陷阱 5：错误的函数选择
**问题描述**：
模型选择了错误的函数，或者应该调用函数时没有调用。

**常见原因**：
- 函数名称不够清晰
- 函数描述不够准确
- 函数之间的职责划分不清

**解决方案**：
1. 使用清晰、描述性的函数名称
2. 在函数描述中明确说明适用场景
3. 避免功能重叠，确保每个函数职责单一

**示例**：
```json
{
  "name": "get_current_weather",
  "description": "获取指定城市的当前天气，包括实时温度、湿度、天气状况等，用于查询'现在'的天气情况"
}
```

### 陷阱 6：多次调用同一函数
**问题描述**：
模型在单次对话中多次调用同一函数，造成资源浪费。

**常见原因**：
- 消息上下文管理不当
- 没有将函数调用结果正确注入上下文
- 模型未能识别已经执行过相同操作

**解决方案**：
1. 正确维护消息上下文，将函数调用和执行结果都纳入上下文
2. 在函数描述中说明是否需要重复调用
3. 客户端层面实现去重逻辑

**示例**：
```python
# 正确的上下文管理
messages = [
    {"role": "user", "content": "查询北京天气"},
    {"role": "assistant", "content": None, "tool_calls": [{"function": {"name": "get_weather", "arguments": '{"location": "北京"}"}}]},
    {"role": "tool", "content": '{"temperature": 25, "weather": "晴"}'},
    {"role": "assistant", "content": "北京当前天气：晴，温度25度"}
]
```

### 陷阱 7：函数调用失败未处理
**问题描述**：
函数执行失败后，模型无法正确处理错误，导致对话中断或返回错误信息。

**常见原因**：
- 错误信息不够明确
- 模型没有接收到执行结果
- 缺少错误处理指导

**解决方案**：
1. 函数返回明确的结构化错误信息
2. 将错误结果正确注入消息上下文
3. 在函数描述中说明可能的错误类型和处理方式

**示例**：
```python
# 函数返回结构化错误
def get_weather(location):
    try:
        result = api_call(location)
        return {"success": True, "data": result}
    except Exception as e:
        return {
            "success": False,
            "error": "weather_fetch_failed",
            "message": f"无法获取{location}的天气信息：{str(e)}",
            "retryable": True
        }
```

## 结果处理问题

### 陷阱 8：结果解析错误
**问题描述**：
函数执行结果格式不规范，导致模型无法正确解析和使用。

**常见原因**：
- 结果格式不一致
- 缺少必要的字段
- 字段命名不清晰

**解决方案**：
1. 统一结果格式，使用一致的结构
2. 确保所有字段都有清晰的命名
3. 在函数描述中说明返回值的结构

**示例**：
```python
def get_user(user_id):
    user = db.query(user_id)
    return {
        "success": True,
        "data": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "status": user.status,
            "created_at": user.created_at.isoformat()
        }
    }
```

### 陷阱 9：上下文污染
**问题描述**：
过多或过长的函数调用结果导致消息上下文过大，影响模型性能和成本。

**常见原因**：
- 函数返回了过多数据
- 没有对结果进行精简
- 多次调用积累了大量历史数据

**解决方案**：
1. 只返回必要的数据字段
2. 对大数据量实现分页或摘要
3. 定期清理过时的上下文

**示例**：
```python
def search_products(keyword):
    results = db.search(keyword, limit=100)
    # 只返回关键字段，避免返回过多数据
    return {
        "success": True,
        "data": [
            {"id": r.id, "name": r.name, "price": r.price}
            for r in results[:20]  # 只返回前20条
        ],
        "total": len(results)
    }
```

### 陷阱 10：多轮对话状态丢失
**问题描述**：
在多轮对话中，模型丢失了之前函数调用的上下文，导致无法正确执行后续操作。

**常见原因**：
- 上下文管理不当
- 没有持续维护对话历史
- 消息上下文被截断或清空

**解决方案**：
1. 持续维护完整的消息上下文
2. 确保所有函数调用和结果都纳入上下文
3. 实现上下文压缩或摘要机制

**示例**：
```python
# 持续维护上下文
def maintain_context(conversation_history, new_message, tool_call, tool_result):
    conversation_history.append({"role": "user", "content": new_message})
    conversation_history.append({
        "role": "assistant",
        "content": None,
        "tool_calls": [tool_call]
    })
    conversation_history.append({"role": "tool", "content": tool_result})
    return conversation_history
```

## 性能问题

### 陷阱 11：函数执行时间过长
**问题描述**：
函数执行时间过长，导致用户等待时间过长或超时。

**常见原因**：
- 网络请求超时
- 数据库查询慢
- 计算任务复杂

**解决方案**：
1. 设置合理的超时时间
2. 实现异步调用
3. 使用缓存优化性能

**示例**：
```python
import asyncio

async def fetch_data_with_timeout(api_url, timeout=10):
    try:
        return await asyncio.wait_for(fetch_data(api_url), timeout=timeout)
    except asyncio.TimeoutError:
        return {"success": False, "error": "请求超时"}
```

### 陷阱 12：过度调用
**问题描述**：
模型频繁调用函数，造成不必要的资源消耗。

**常见原因**：
- 函数描述不够准确
- 模型过度依赖外部工具
- 缺少调用频率控制

**解决方案**：
1. 在函数描述中说明调用时机和频率
2. 实现调用频率限制
3. 使用缓存减少重复调用

**示例**：
```python
from functools import lru_cache
from datetime import datetime, timedelta

# 缓存结果，5分钟内重复查询直接返回缓存
@lru_cache(maxsize=128)
def get_weather_cached(location):
    # 检查缓存时间
    if location in _cache and datetime.now() - _cache_time[location] < timedelta(minutes=5):
        return _cache[location]
    result = fetch_weather(location)
    _cache[location] = result
    _cache_time[location] = datetime.now()
    return result
```

## 安全问题

### 陷阱 13：参数注入攻击
**问题描述**：
恶意用户通过参数注入执行未授权操作。

**常见原因**：
- 缺少参数验证
- 直接使用模型生成的参数执行操作
- 没有实现权限控制

**解决方案**：
1. 严格验证所有参数
2. 实现权限控制机制
3. 对敏感操作增加二次确认

**示例**：
```python
def validate_and_execute(user_id, command, params):
    # 验证用户权限
    if not has_permission(user_id, command):
        raise PermissionError("权限不足")

    # 验证参数
    if not validate_params(command, params):
        raise ValueError("参数无效")

    # 执行操作
    return execute_command(command, params)
```

### 陷阱 14：敏感信息泄露
**问题描述**：
函数返回的结果中包含敏感信息，导致数据泄露。

**常见原因**：
- 返回了过多的数据字段
- 没有对敏感数据进行脱敏
- 缺少访问控制

**解决方案**：
1. 只返回必要的字段
2. 对敏感数据进行脱敏处理
3. 实现细粒度的访问控制

**示例**：
```python
def get_user(user_id, request_user_id):
    user = db.query(user_id)
    
    # 检查访问权限
    if user_id != request_user_id and not has_permission(request_user_id, "user.view_all"):
        raise PermissionError("权限不足")
    
    # 脱敏处理
    return {
        "id": user.id,
        "name": user.name,
        "email": mask_email(user.email) if not has_permission(request_user_id, "user.view_email") else user.email,
        "phone": mask_phone(user.phone)
    }
```

### 陷阱 15：未授权操作
**问题描述**：
模型调用函数执行了未授权的操作。

**常见原因**：
- 缺少权限检查
- 函数描述中未说明权限要求
- 模型误解用户意图

**解决方案**：
1. 在每个函数中实现权限检查
2. 在函数描述中明确权限要求
3. 对敏感操作增加确认机制

**示例**：
```json
{
  "name": "delete_user",
  "description": "删除用户账户（需要管理员权限，操作不可恢复，请谨慎使用）",
  "parameters": {
    "properties": {
      "user_id": {
        "type": "string",
        "description": "要删除的用户ID"
      }
    },
    "required": ["user_id"]
  }
}
```
