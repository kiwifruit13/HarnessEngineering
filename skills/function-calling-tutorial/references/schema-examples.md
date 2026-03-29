# Function Calling Schema 示例集合

## 目录
1. [基础示例](#基础示例)
2. [复杂对象示例](#复杂对象示例)
3. [枚举与约束示例](#枚举与约束示例)
4. [嵌套结构示例](#嵌套结构示例)
5. [数组参数示例](#数组参数示例)
6. [可选参数示例](#可选参数示例)

## 概览
本文档提供 Function Calling 中常见场景的完整 Schema 示例，涵盖基础类型、复杂对象、枚举约束、嵌套结构等多种使用场景。

## 基础示例

### 获取当前天气
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

### 发送邮件
```json
{
  "name": "send_email",
  "description": "发送电子邮件给指定收件人",
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
        "description": "邮件正文内容"
      },
      "is_html": {
        "type": "boolean",
        "description": "是否为 HTML 格式邮件，默认为 false"
      }
    },
    "required": ["to", "subject", "content"]
  }
}
```

### 计算器功能
```json
{
  "name": "calculate",
  "description": "执行基本数学运算，包括加、减、乘、除",
  "parameters": {
    "type": "object",
    "properties": {
      "operation": {
        "type": "string",
        "enum": ["add", "subtract", "multiply", "divide"],
        "description": "运算类型：'add'加法，'subtract'减法，'multiply'乘法，'divide'除法"
      },
      "a": {
        "type": "number",
        "description": "第一个操作数"
      },
      "b": {
        "type": "number",
        "description": "第二个操作数"
      }
    },
    "required": ["operation", "a", "b"]
  }
}
```

## 复杂对象示例

### 创建用户
```json
{
  "name": "create_user",
  "description": "创建新用户账户，包括基本信息和联系方式",
  "parameters": {
    "type": "object",
    "properties": {
      "username": {
        "type": "string",
        "description": "用户名，长度3-20个字符，只能包含字母、数字和下划线"
      },
      "email": {
        "type": "string",
        "description": "电子邮箱地址，格式需符合标准邮箱格式"
      },
      "password": {
        "type": "string",
        "description": "密码，长度至少8个字符，需包含字母和数字"
      },
      "full_name": {
        "type": "string",
        "description": "用户全名"
      },
      "age": {
        "type": "number",
        "description": "用户年龄，必须大于等于18",
        "minimum": 18
      },
      "avatar_url": {
        "type": "string",
        "description": "头像图片URL"
      }
    },
    "required": ["username", "email", "password", "full_name"]
  }
}
```

### 查询股票信息
```json
{
  "name": "get_stock_info",
  "description": "查询指定股票的详细信息，包括当前价格、涨跌幅、成交量等",
  "parameters": {
    "type": "object",
    "properties": {
      "symbol": {
        "type": "string",
        "description": "股票代码，如'AAPL'、'TSLA'、'MSFT'"
      },
      "market": {
        "type": "string",
        "enum": ["US", "HK", "CN"],
        "description": "市场：'US'美股，'HK'港股，'CN'A股"
      },
      "include_history": {
        "type": "boolean",
        "description": "是否包含历史数据，默认为 false"
      },
      "history_days": {
        "type": "number",
        "description": "历史数据天数，当 include_history 为 true 时有效，最多30天",
        "maximum": 30,
        "minimum": 1
      }
    },
    "required": ["symbol", "market"]
  }
}
```

## 枚举与约束示例

### 设置用户状态
```json
{
  "name": "set_user_status",
  "description": "更新用户账户状态",
  "parameters": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "description": "用户唯一标识符"
      },
      "status": {
        "type": "string",
        "enum": ["active", "inactive", "suspended", "deleted"],
        "description": "用户状态：'active'激活，'inactive'未激活，'suspended'暂停，'deleted'已删除"
      },
      "reason": {
        "type": "string",
        "description": "状态变更原因，当 status 为 suspended 或 deleted 时必填"
      }
    },
    "required": ["user_id", "status"]
  }
}
```

### 搜索商品
```json
{
  "name": "search_products",
  "description": "根据关键词和条件搜索商品",
  "parameters": {
    "type": "object",
    "properties": {
      "keyword": {
        "type": "string",
        "description": "搜索关键词"
      },
      "category": {
        "type": "string",
        "enum": ["electronics", "clothing", "books", "home", "sports"],
        "description": "商品分类：'electronics'电子产品，'clothing'服装，'books'图书，'home'家居，'sports'运动"
      },
      "price_range": {
        "type": "string",
        "enum": ["0-100", "100-500", "500-1000", "1000+"],
        "description": "价格区间"
      },
      "sort_by": {
        "type": "string",
        "enum": ["price_asc", "price_desc", "rating", "sales"],
        "description": "排序方式：'price_asc'价格升序，'price_desc'价格降序，'rating'评分，'sales'销量"
      }
    },
    "required": ["keyword"]
  }
}
```

## 嵌套结构示例

### 更新用户资料
```json
{
  "name": "update_user_profile",
  "description": "更新用户的详细资料信息",
  "parameters": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "description": "用户唯一标识符"
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
            "description": "电子邮箱地址"
          },
          "phone": {
            "type": "string",
            "description": "联系电话"
          },
          "birthday": {
            "type": "string",
            "description": "生日，格式：YYYY-MM-DD"
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
                "description": "省份或州"
              },
              "city": {
                "type": "string",
                "description": "城市"
              },
              "street": {
                "type": "string",
                "description": "街道地址"
              },
              "postal_code": {
                "type": "string",
                "description": "邮政编码"
              }
            },
            "required": ["country", "city"]
          },
          "preferences": {
            "type": "object",
            "description": "用户偏好设置",
            "properties": {
              "language": {
                "type": "string",
                "enum": ["zh-CN", "en-US", "ja-JP"],
                "description": "语言偏好"
              },
              "timezone": {
                "type": "string",
                "description": "时区，如'Asia/Shanghai'、'America/New_York'"
              },
              "notifications": {
                "type": "object",
                "description": "通知设置",
                "properties": {
                  "email": {
                    "type": "boolean",
                    "description": "是否接收邮件通知"
                  },
                  "sms": {
                    "type": "boolean",
                    "description": "是否接收短信通知"
                  },
                  "push": {
                    "type": "boolean",
                    "description": "是否接收推送通知"
                  }
                }
              }
            }
          }
        },
        "required": ["name", "email"]
      }
    },
    "required": ["user_id", "profile"]
  }
}
```

### 创建订单
```json
{
  "name": "create_order",
  "description": "创建新订单，包含商品列表、配送地址和支付信息",
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
            },
            "price": {
              "type": "number",
              "description": "单价"
            },
            "discount": {
              "type": "number",
              "description": "折扣金额"
            }
          },
          "required": ["product_id", "quantity"]
        }
      },
      "shipping_address": {
        "type": "object",
        "description": "配送地址",
        "properties": {
          "recipient_name": {
            "type": "string",
            "description": "收件人姓名"
          },
          "phone": {
            "type": "string",
            "description": "联系电话"
          },
          "address": {
            "type": "string",
            "description": "详细地址"
          },
          "city": {
            "type": "string",
            "description": "城市"
          },
          "postal_code": {
            "type": "string",
            "description": "邮政编码"
          }
        },
        "required": ["recipient_name", "phone", "address", "city"]
      },
      "payment_method": {
        "type": "string",
        "enum": ["credit_card", "debit_card", "paypal", "alipay", "wechat_pay"],
        "description": "支付方式"
      },
      "coupon_code": {
        "type": "string",
        "description": "优惠券代码"
      }
    },
    "required": ["customer_id", "items", "shipping_address", "payment_method"]
  }
}
```

## 数组参数示例

### 批量发送通知
```json
{
  "name": "send_bulk_notifications",
  "description": "批量发送通知消息给多个用户",
  "parameters": {
    "type": "object",
    "properties": {
      "recipients": {
        "type": "array",
        "description": "收件人列表",
        "items": {
          "type": "object",
          "properties": {
            "user_id": {
              "type": "string",
              "description": "用户ID"
            },
            "message": {
              "type": "string",
              "description": "通知消息内容"
            },
            "priority": {
              "type": "string",
              "enum": ["low", "normal", "high", "urgent"],
              "description": "优先级"
            }
          },
          "required": ["user_id", "message"]
        }
      },
      "channel": {
        "type": "string",
        "enum": ["email", "sms", "push", "in_app"],
        "description": "通知渠道"
      },
      "scheduled_time": {
        "type": "string",
        "description": "定时发送时间，格式：YYYY-MM-DD HH:MM:SS，不填则立即发送"
      }
    },
    "required": ["recipients", "channel"]
  }
}
```

### 批量查询数据
```json
{
  "name": "batch_query_data",
  "description": "批量查询多个数据记录",
  "parameters": {
    "type": "object",
    "properties": {
      "ids": {
        "type": "array",
        "description": "数据ID列表",
        "items": {
          "type": "string"
        },
        "minItems": 1,
        "maxItems": 100
      },
      "fields": {
        "type": "array",
        "description": "需要返回的字段列表",
        "items": {
          "type": "string"
        }
      }
    },
    "required": ["ids"]
  }
}
```

## 可选参数示例

### 搜索文档
```json
{
  "name": "search_documents",
  "description": "在文档库中搜索符合条件的文档",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "搜索关键词或短语"
      },
      "document_type": {
        "type": "string",
        "enum": ["pdf", "docx", "txt", "html"],
        "description": "文档类型过滤"
      },
      "author": {
        "type": "string",
        "description": "作者过滤"
      },
      "date_range": {
        "type": "object",
        "description": "日期范围过滤",
        "properties": {
          "start_date": {
            "type": "string",
            "description": "开始日期，格式：YYYY-MM-DD"
          },
          "end_date": {
            "type": "string",
            "description": "结束日期，格式：YYYY-MM-DD"
          }
        }
      },
      "page": {
        "type": "number",
        "description": "页码，从1开始，默认为1"
      },
      "page_size": {
        "type": "number",
        "description": "每页结果数，默认为10，最大100",
        "maximum": 100,
        "minimum": 1
      },
      "sort_by": {
        "type": "string",
        "enum": ["relevance", "date_asc", "date_desc", "title"],
        "description": "排序方式"
      }
    },
    "required": ["query"]
  }
}
```

### 生成报告
```json
{
  "name": "generate_report",
  "description": "生成数据分析报告",
  "parameters": {
    "type": "object",
    "properties": {
      "report_type": {
        "type": "string",
        "enum": ["sales", "traffic", "user", "revenue"],
        "description": "报告类型"
      },
      "start_date": {
        "type": "string",
        "description": "开始日期，格式：YYYY-MM-DD"
      },
      "end_date": {
        "type": "string",
        "description": "结束日期，格式：YYYY-MM-DD"
      },
      "include_charts": {
        "type": "boolean",
        "description": "是否包含图表，默认为 true"
      },
      "format": {
        "type": "string",
        "enum": ["pdf", "excel", "html"],
        "description": "输出格式，默认为 pdf"
      },
      "language": {
        "type": "string",
        "enum": ["zh-CN", "en-US"],
        "description": "报告语言，默认为 zh-CN"
      },
      "custom_title": {
        "type": "string",
        "description": "自定义报告标题"
      }
    },
    "required": ["report_type", "start_date", "end_date"]
  }
}
```
