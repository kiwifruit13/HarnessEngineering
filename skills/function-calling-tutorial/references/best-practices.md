# Function Calling 最佳实践详解

## 目录
1. [函数设计原则](#函数设计原则)
2. [Schema 编写规范](#schema-编写规范)
3. [错误处理策略](#错误处理策略)
4. [性能优化建议](#性能优化建议)
5. [安全防护措施](#安全防护措施)

## 概览
本文档提供 Function Calling 开发的最佳实践指导，涵盖函数设计、Schema 定义、错误处理、性能优化和安全防护等核心主题。

## 函数设计原则

### 单一职责原则
每个函数只应实现一个明确的功能，避免函数承担过多职责。

**优点**：
- 提高函数的可复用性
- 降低模型的理解难度
- 简化错误排查和维护

**示例对比**：
- ❌ 不推荐：`manage_user`（包含创建、更新、删除多个操作）
- ✅ 推荐：`create_user`、`update_user`、`delete_user`

### 参数精简化
只包含函数执行所必需的参数，避免冗余参数增加模型理解负担。

**原则**：
- 优先考虑必填参数，将可选参数设为非必填
- 避免参数过多，建议不超过 5-8 个
- 对于复杂对象，使用嵌套结构而非扁平化参数

**示例**：
```json
{
  "name": "send_email",
  "description": "发送邮件",
  "parameters": {
    "type": "object",
    "properties": {
      "to": {
        "type": "string",
        "description": "收件人邮箱地址"
      },
      "subject": {
        "type": "string",
        "description": "邮件主题"
      },
      "content": {
        "type": "string",
        "description": "邮件正文"
      }
    },
    "required": ["to", "subject", "content"]
  }
}
```

### 命名语义化
使用清晰、描述性的函数名称，遵循一致的命名约定。

**命名规范**：
- 使用动词-名词组合：`get_weather`、`create_user`、`delete_file`
- 使用小写字母和下划线分隔：`calculate_total_price`、`verify_user_identity`
- 避免缩写和模糊词汇：使用 `calculate_average` 而非 `calc_avg`

### 描述详尽化
为函数和参数提供清晰、准确、详尽的描述，帮助模型理解功能和使用方式。

**描述编写要点**：
- **函数描述**：说明功能、用途、适用场景
- **参数描述**：说明参数的含义、格式、取值范围
- **返回值描述**：说明返回值的结构和含义

**示例**：
```json
{
  "name": "get_current_weather",
  "description": "获取指定城市的当前天气信息，包括温度、湿度、天气状况等",
  "parameters": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "城市名称，支持中文和英文，如'北京'、'Shanghai'、'New York'"
      },
      "unit": {
        "type": "string",
        "enum": ["celsius", "fahrenheit"],
        "description": "温度单位，'celsius'表示摄氏度，'fahrenheit'表示华氏度"
      }
    },
    "required": ["location"]
  }
}
```

## Schema 编写规范

### 参数类型选择
根据实际需求选择合适的参数类型，避免类型不匹配导致的调用失败。

**常用类型及使用场景**：
- `string`：文本数据，如名称、描述、标识符
- `number`：数值数据，包括整数和浮点数，如数量、价格、温度
- `boolean`：布尔值，如开关、状态标识
- `object`：结构化对象，如地址、配置信息
- `array`：数组，如列表、集合

**示例**：
```json
{
  "name": "create_order",
  "parameters": {
    "type": "object",
    "properties": {
      "customer_id": {
        "type": "string",
        "description": "客户ID"
      },
      "items": {
        "type": "array",
        "description": "商品列表",
        "items": {
          "type": "object",
          "properties": {
            "product_id": {
              "type": "string",
              "description": "商品ID"
            },
            "quantity": {
              "type": "number",
              "description": "购买数量"
            }
          },
          "required": ["product_id", "quantity"]
        }
      },
      "is_vip": {
        "type": "boolean",
        "description": "是否为VIP客户"
      }
    },
    "required": ["customer_id", "items"]
  }
}
```

### 必填字段标识
使用 `required` 数组明确标识必需参数，帮助模型识别哪些参数必须提供。

**原则**：
- 必填参数：函数执行所必需的参数
- 可选参数：有默认值或可推断的参数
- 避免所有参数都设为必填，降低调用门槛

**示例**：
```json
{
  "name": "search_products",
  "parameters": {
    "type": "object",
    "properties": {
      "keyword": {
        "type": "string",
        "description": "搜索关键词"
      },
      "category": {
        "type": "string",
        "description": "商品分类"
      },
      "min_price": {
        "type": "number",
        "description": "最低价格"
      },
      "max_price": {
        "type": "number",
        "description": "最高价格"
      }
    },
    "required": ["keyword"]
  }
}
```

### 枚举约束定义
使用 `enum` 字段限制参数的取值范围，确保模型生成的参数在合法范围内。

**适用场景**：
- 参数取值只有有限几个选项
- 需要严格限制参数输入
- 提高参数生成的准确性

**示例**：
```json
{
  "name": "set_user_status",
  "parameters": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "description": "用户ID"
      },
      "status": {
        "type": "string",
        "enum": ["active", "inactive", "suspended", "deleted"],
        "description": "用户状态：'active'表示激活，'inactive'表示未激活，'suspended'表示暂停，'deleted'表示已删除"
      }
    },
    "required": ["user_id", "status"]
  }
}
```

### 嵌套结构定义
对于复杂的参数结构，使用嵌套的 `properties` 定义，提高 Schema 的可读性和可维护性。

**示例**：
```json
{
  "name": "update_user_profile",
  "parameters": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "description": "用户ID"
      },
      "profile": {
        "type": "object",
        "description": "用户资料信息",
        "properties": {
          "name": {
            "type": "string",
            "description": "用户姓名"
          },
          "email": {
            "type": "string",
            "description": "电子邮箱"
          },
          "phone": {
            "type": "string",
            "description": "联系电话"
          },
          "address": {
            "type": "object",
            "description": "地址信息",
            "properties": {
              "country": {
                "type": "string",
                "description": "国家"
              },
              "province": {
                "type": "string",
                "description": "省份"
              },
              "city": {
                "type": "string",
                "description": "城市"
              },
              "street": {
                "type": "string",
                "description": "街道地址"
              }
            },
            "required": ["country", "city"]
          }
        },
        "required": ["name", "email"]
      }
    },
    "required": ["user_id", "profile"]
  }
}
```

## 错误处理策略

### 参数验证
客户端必须验证模型生成的参数是否符合 Schema 定义，防止无效参数导致执行错误。

**验证要点**：
- 参数类型是否正确
- 必填参数是否完整
- 枚举值是否在合法范围内
- 数值范围是否符合要求

**示例代码**：
```python
import json
from jsonschema import validate, ValidationError

def validate_params(schema, params):
    try:
        validate(instance=params, schema=schema)
        return True, None
    except ValidationError as e:
        return False, str(e)

# 使用示例
schema = {
    "type": "object",
    "properties": {
        "location": {"type": "string"},
        "unit": {"enum": ["celsius", "fahrenheit"]}
    },
    "required": ["location"]
}

params = {"location": "北京", "unit": "kelvin"}
valid, error = validate_params(schema, params)
if not valid:
    print(f"参数验证失败: {error}")
```

### 执行错误捕获
捕获函数执行过程中可能出现的异常，返回明确的错误信息，便于模型理解和处理。

**常见错误类型**：
- 网络错误：连接超时、服务不可用
- 权限错误：认证失败、权限不足
- 数据错误：参数无效、数据不存在
- 系统错误：资源不足、服务异常

**错误处理示例**：
```python
import requests

def get_weather(location):
    try:
        response = requests.get(f"https://api.weather.com/current?location={location}", timeout=10)
        response.raise_for_status()
        return {"success": True, "data": response.json()}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "请求超时，请稍后重试"}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {"success": False, "error": f"未找到城市: {location}"}
        elif e.response.status_code == 403:
            return {"success": False, "error": "API 密钥无效或权限不足"}
        else:
            return {"success": False, "error": f"服务错误: HTTP {e.response.status_code}"}
    except Exception as e:
        return {"success": False, "error": f"未知错误: {str(e)}"}
```

### 超时处理
设置合理的函数执行超时时间，避免长时间阻塞影响用户体验。

**超时设置原则**：
- 根据函数实际执行时间设置超时
- IO 密集型操作设置较长超时（30-60秒）
- 计算密集型操作设置较短超时（5-10秒）
- 提供超时后的降级方案

**示例**：
```python
import signal
from contextlib import contextmanager

@contextmanager
def timeout_handler(seconds):
    def timeout_handler_func(signum, frame):
        raise TimeoutError(f"操作超时，超过 {seconds} 秒")

    signal.signal(signal.SIGALRM, timeout_handler_func)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

# 使用示例
try:
    with timeout_handler(30):
        result = execute_long_operation()
except TimeoutError:
    result = {"success": False, "error": "操作超时，请稍后重试"}
```

### 降级策略
当函数执行失败时，提供备选方案或默认值，确保系统能够继续运行。

**降级策略类型**：
- 返回缓存结果：使用历史缓存数据
- 返回默认值：提供合理的默认数据
- 重试机制：指数退避重试
- 提供替代功能：使用备用服务或方法

**示例**：
```python
import time
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        return {"success": False, "error": f"重试 {max_retries} 次后仍然失败: {str(e)}"}
                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)
        return wrapper
    return decorator

@retry_with_backoff(max_retries=3, base_delay=1)
def fetch_data():
    response = requests.get("https://api.example.com/data")
    response.raise_for_status()
    return response.json()
```

## 性能优化建议

### 并发调用
利用模型支持的多函数并发调用能力，在无依赖关系时同时执行多个函数，提高响应速度。

**并发调用场景**：
- 查询多个独立的数据源
- 执行多个无依赖的操作
- 批量处理多个请求

**示例**：
```python
import asyncio
import aiohttp

async def call_function_async(url, params):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=params) as response:
            return await response.json()

async def concurrent_execution(functions):
    tasks = [call_function_async(func["url"], func["params"]) for func in functions]
    return await asyncio.gather(*tasks)

# 使用示例
functions = [
    {"url": "https://api.example.com/weather", "params": {"location": "北京"}},
    {"url": "https://api.example.com/news", "params": {"category": "科技"}},
    {"url": "https://api.example.com/stock", "params": {"symbol": "AAPL"}}
]

results = asyncio.run(concurrent_execution(functions))
```

### 结果缓存
对频繁调用且结果稳定的函数实施缓存，减少重复计算和网络请求。

**缓存策略**：
- 基于参数的缓存：相同的参数返回缓存结果
- 缓存过期时间：设置合理的过期时间（如 5 分钟）
- 缓存更新策略：主动更新或被动过期
- 缓存清理机制：定期清理过期缓存

**示例**：
```python
from functools import lru_cache
import time

@lru_cache(maxsize=128)
def get_weather_cached(location, unit="celsius"):
    # 模拟 API 调用
    time.sleep(1)  # 模拟网络延迟
    return {"location": location, "temperature": 25, "unit": unit}

# 使用示例
print(get_weather_cached("北京"))  # 第一次调用，执行实际请求
print(get_weather_cached("北京"))  # 第二次调用，返回缓存结果
```

### 超时控制
设置合理的函数执行超时时间，避免长时间阻塞影响系统性能。

**超时控制原则**：
- 根据函数实际执行时间设置超时
- IO 密集型操作设置较长超时
- 计算密集型操作设置较短超时
- 提供超时后的降级方案

## 安全防护措施

### 参数校验
严格验证模型生成的参数，防止注入攻击和恶意操作。

**校验要点**：
- 类型校验：确保参数类型正确
- 范围校验：确保数值在合理范围内
- 格式校验：使用正则表达式验证格式
- 内容校验：过滤恶意字符和代码注入

**示例**：
```python
import re

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValueError("邮箱格式不正确")
    return email

def sanitize_input(input_str):
    # 移除危险字符
    dangerous_chars = ['<', '>', "'", '"', ';', '&', '|', '`', '$', '(', ')']
    for char in dangerous_chars:
        input_str = input_str.replace(char, '')
    return input_str
```

### 权限控制
根据用户身份和权限限制函数调用，防止未授权访问。

**权限控制策略**：
- 基于角色的访问控制（RBAC）
- 基于用户的权限检查
- 敏感操作需要额外认证
- 审计日志记录

**示例**：
```python
def check_permission(user_id, required_permission):
    user_permissions = get_user_permissions(user_id)
    return required_permission in user_permissions

def delete_user(user_id, current_user_id):
    if not check_permission(current_user_id, "user.delete"):
        return {"success": False, "error": "权限不足"}
    # 执行删除操作
    return {"success": True, "message": "用户已删除"}
```

### 审计日志
记录所有函数调用，便于追踪、调试和审计。

**日志记录内容**：
- 调用时间戳
- 用户身份
- 函数名称
- 调用参数
- 执行结果
- 错误信息（如有）

**示例**：
```python
import logging
import json
from datetime import datetime

def log_function_call(user_id, function_name, params, result):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "function_name": function_name,
        "params": params,
        "result": result
    }
    logging.info(json.dumps(log_entry))

# 使用示例
result = get_weather("北京")
log_function_call("user123", "get_weather", {"location": "北京"}, result)
```
