"""
工具模块 - 数据验证器

职责：验证输入输出数据格式
"""

import json
from typing import Dict, Any
from pathlib import Path


class ValidationError(Exception):
    """数据验证错误"""
    pass


class DataValidator:
    """数据验证器"""
    
    @staticmethod
    def validate_environment_profile(data: Dict[str, Any]) -> bool:
        """验证环境画像格式"""
        required_fields = ["task_type", "domain", "time_sensitivity", "data_type"]
        
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"环境画像缺少必需字段: {field}")
        
        # 验证枚举值
        valid_task_types = ["信息检索", "深度分析", "内容创作", "问题解决"]
        if data["task_type"] not in valid_task_types:
            raise ValidationError(f"无效的任务类型: {data['task_type']}")
        
        valid_time_sensitivities = ["静态", "实时", "预测"]
        if data["time_sensitivity"] not in valid_time_sensitivities:
            raise ValidationError(f"无效的时效性: {data['time_sensitivity']}")
        
        return True
    
    @staticmethod
    def validate_capability_registry(data: Dict[str, Any]) -> bool:
        """验证能力清单格式"""
        required_layers = ["L1", "L2", "L3", "L4", "L5"]
        
        for layer in required_layers:
            if layer not in data:
                raise ValidationError(f"能力清单缺少必需层级: {layer}")
            
            if not isinstance(data[layer], dict):
                raise ValidationError(f"层级 {layer} 必须是字典类型")
        
        return True
    
    @staticmethod
    def validate_mapping_result(data: Dict[str, Any]) -> bool:
        """验证映射结果格式"""
        required_fields = ["match_score", "layer_scores", "shortages"]
        
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"映射结果缺少必需字段: {field}")
        
        if not (0 <= data["match_score"] <= 1):
            raise ValidationError("匹配分数必须在0-1之间")
        
        return True
    
    @staticmethod
    def validate_execution_status(data: Dict[str, Any]) -> bool:
        """验证执行状态格式"""
        required_fields = ["current_step", "status"]
        
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"执行状态缺少必需字段: {field}")
        
        valid_statuses = ["running", "success", "failed", "timeout", "new_requirement"]
        if data["status"] not in valid_statuses:
            raise ValidationError(f"无效的执行状态: {data['status']}")
        
        return True
    
    @staticmethod
    def validate_json_file(file_path: str, schema_type: str = None) -> Dict[str, Any]:
        """验证JSON文件并返回数据"""
        path = Path(file_path)
        
        if not path.exists():
            raise ValidationError(f"文件不存在: {file_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValidationError(f"JSON解析错误: {e}")
        
        # 根据类型验证
        validators = {
            "environment_profile": DataValidator.validate_environment_profile,
            "capability_registry": DataValidator.validate_capability_registry,
            "mapping_result": DataValidator.validate_mapping_result,
            "execution_status": DataValidator.validate_execution_status
        }
        
        if schema_type and schema_type in validators:
            validators[schema_type](data)
        
        return data
