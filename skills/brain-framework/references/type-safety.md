# 类型安全指南

## 概览
本文档提供 Brain Framework 中处理弱类型陷阱的完整指南，帮助在代码库改造过程中避免类型相关的 bug 和歧义。

## 目录
1. [常见类型陷阱](#常见类型陷阱)
2. [应对策略](#应对策略)
3. [代码规范](#代码规范)
4. [各阶段检查点](#各阶段检查点)

## 常见类型陷阱

### 1. 隐式类型转换

**问题描述**：
弱类型语言会在运算时自动转换类型，导致意外结果。

**问题示例**：
```python
# Python (强类型，会报错)
"5" + 3  # TypeError: can only concatenate str to str

# JavaScript (弱类型，静默转换)
"5" + 3        # "53" (字符串拼接)
"5" - 3        # 2 (减法转数字)
[] + []        # "" (空字符串)
[] == false    # true
null == undefined  # true
```

**危害**：
- 静默产生错误结果，难以调试
- 类型错误在运行时才暴露
- 代码行为难以预测

### 2. 空值歧义

**问题描述**：
`None`/`null`、`""`、`[]`、`0`、`False` 都能表示"无"，但语义不同。

**问题示例**：
```python
# 所有这些值在条件判断中都为 False
values = [None, "", [], 0, False]

for v in values:
    if not v:
        print(f"{v} is falsy")  # 全部打印

# 问题：可能需要区分 None 和空字符串
def get_config(key: str, default: str = None):
    value = fetch_from_db(key)
    if not value:  # 错误：会把空字符串当作 None
        return default
```

**默认参数陷阱**：
```python
# 可变默认参数被共享
def append_item(item, lst=[]):
    lst.append(item)
    return lst

append_item(1)  # [1]
append_item(2)  # [1, 2]  # 意外！
```

### 3. 类型推断失效

**问题描述**：
Python 类型注解只是提示，运行时不强制检查。

**问题示例**：
```python
def process(data: list[str]) -> str:
    return data[0]

process([1, 2, 3])  # 运行正常，但类型错误
process(123)        # 运行时报错
process([])         # IndexError

# any 类型完全绕过检查
def parse(data: Any) -> Any:
    return data  # 失去类型保护
```

### 4. 容器类型陷阱

**问题描述**：
容器类型的隐式行为可能导致意外结果。

**问题示例**：
```python
# 字典键类型混合
d = {"1": "a", 1: "b"}
d["1"]  # "a"
d[1]    # "b"  # 容易混淆

# 列表浅拷贝
a = [[1, 2], [3, 4]]
b = a[:]
b[0][0] = 999
print(a[0][0])  # 999  # 原列表被修改

# 字典引用
config = {"timeout": 30}
new_config = config
new_config["timeout"] = 60
print(config["timeout"])  # 60  # 原字典被修改
```

## 应对策略

### 1. 隐式类型转换应对

```python
# Python：使用类型注解 + 静态检查
def add(a: int, b: int) -> int:
    return a + b

# 运行时类型检查
def process(value: str | int) -> str:
    if isinstance(value, str):
        return value.upper()
    elif isinstance(value, int):
        return str(value)
    raise TypeError(f"Unexpected type: {type(value)}")
```

```javascript
// JavaScript：使用严格相等
if (value === null) { /* 明确检查 null */ }
if (value === undefined) { /* 明确检查 undefined */ }
if (typeof value === "string") { /* 明确检查类型 */ }

// TypeScript：启用严格模式
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true
  }
}
```

### 2. 空值歧义应对

```python
# 显式区分不同类型的"空"
if data is None:
    # 明确是 None
    pass
elif data == "":
    # 明确是空字符串
    pass
elif data == []:
    # 明确是空列表
    pass
elif not data:
    # 通用的 falsy 检查（需文档说明意图）
    pass

# 使用 sentinel 值区分"未提供参数"
_SENTINEL = object()

def func(value=_SENTINEL):
    if value is _SENTINEL:
        # 真正的"未提供参数"
        value = get_default()
    elif value is None:
        # 明确传入了 None
        pass

# 避免可变默认参数
def append_item(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst
```

### 3. 类型推断应对

```python
# 使用 Pydantic 进行运行时验证
from pydantic import BaseModel, validator

class UserConfig(BaseModel):
    timeout: int
    retries: int = 3
    
    @validator('timeout')
    def validate_timeout(cls, v):
        if v < 0:
            raise ValueError('timeout must be positive')
        return v

# 自动验证类型和值
config = UserConfig(timeout="30")  # 自动转换为 int
# config.timeout == 30

# 使用 TypeGuard 进行类型收窄
from typing import TypeGuard

def is_string_list(value: list) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in value)

def process(items: list):
    if is_string_list(items):
        # 这里 items 被推断为 list[str]
        return [x.upper() for x in items]
```

### 4. 容器类型应对

```python
# 使用 TypedDict 统一字典结构
from typing import TypedDict

class UserDict(TypedDict):
    id: int
    name: str
    email: str

# 类型安全的字典
user: UserDict = {
    "id": 1,
    "name": "Alice",
    "email": "alice@example.com"
}

# 使用 dataclass 替代字典
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    email: str

# 深拷贝嵌套结构
import copy

original = [[1, 2], [3, 4]]
copied = copy.deepcopy(original)
copied[0][0] = 999
print(original[0][0])  # 1 (原列表未被修改)

# 或使用 JSON 序列化
import json
copied = json.loads(json.dumps(original))
```

## 代码规范

### 类型注解规范

```python
# 1. 所有公共函数必须有类型注解
# 正确
def process(data: list[str], config: dict[str, any]) -> str:
    ...

# 错误
def process(data, config):
    ...

# 2. 避免 any，使用更精确的类型
# 错误
def parse(data: Any) -> Any:
    ...

# 正确
def parse(data: str | dict) -> dict:
    ...

# 3. 使用 Optional 明确可能为 None 的返回值
from typing import Optional

def find_user(id: int) -> Optional[User]:
    # 可能返回 None
    ...

# 4. 使用 Union 或 | 处理多种类型
def process(value: str | int | None) -> str:
    ...
```

### 类型检查配置

```yaml
# brain-config.yaml
type_safety:
  require_type_hints: true       # 要求所有函数有类型注解
  runtime_validation: "pydantic" # 使用 Pydantic 运行时验证
  forbid_implicit_conversion: true  # 禁止隐式类型转换
  explicit_none_check: true      # 要求显式 None 检查
  unified_dict_key_type: true    # 要求字典键类型统一
  deep_copy_for_nested: true     # 嵌套结构使用深拷贝
```

### mypy 严格配置

```ini
# mypy.ini
[mypy]
strict = True
disallow_any_generics = True
disallow_subclassing_any = True
disallow_untyped_calls = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_return_any = True
no_implicit_reexport = True
strict_equality = True
```

## 各阶段检查点

### Research 阶段
- [ ] 识别类型热点：隐式转换、any 类型、混合类型容器
- [ ] 标记类型注解覆盖率（当前 %，目标 %）
- [ ] 发现类型相关的 bug 或潜在风险
- [ ] 识别使用 `==` 而非 `is` 的 None 检查

### Plan 阶段
- [ ] 明确类型策略：是否启用严格模式
- [ ] 设定类型注解覆盖率目标
- [ ] 在文件变更清单中标注类型约束
- [ ] 设计数据模型的类型定义（Pydantic/dataclass）

### Annotate 阶段
- [ ] 审查函数签名的类型注解完整性
- [ ] 检查接口契约的类型一致性
- [ ] 确认序列化/反序列化的类型安全
- [ ] 验证 Optional 类型的处理逻辑

### Implement 阶段
- [ ] 启用 `--strict` 模式强制类型检查
- [ ] 禁止 `any`/`unknown` 类型
- [ ] 运行 mypy/pyright 静态检查
- [ ] 使用 Pydantic 进行运行时验证

### Modification Check 阶段
- [ ] 检测类型签名变更
- [ ] 警告新增 `Optional` 可能引入的 None 风险
- [ ] 检查返回类型变更的兼容性
- [ ] 验证泛型类型参数的约束

## 快速参考卡片

### 类型检查清单
```
□ 所有函数有类型注解
□ 无 any/unknown 类型
□ Optional 类型显式处理 None
□ 字典键类型统一
□ 嵌套结构使用深拷贝
□ 无可变默认参数
□ 使用 === 而非 == (JS/TS)
□ mypy --strict 通过
```

### 常见错误速查
```
错误                          修正
─────────────────────────────────────────
if not data:                  if data is None:
def f(x=[]):                  def f(x=None): ...
Any -> Any                    精确类型
a = b (引用)                  a = copy.deepcopy(b)
"5" + 3                       str(5) + 3 或 int("5") + 3
```
