#!/usr/bin/env python3
"""
LangGraph State Guardrail - 天赋定制集成

本示例展示如何将天赋定制器深度集成到LangGraph的State Guardrail中
在合适的契机为任务定制并注入天赋Prompt
"""
import os
import sys
from typing import TypedDict, Annotated, Optional
from operator import add

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from talent_loader import load_talent_library
from task_feature_extractor import TaskFeatureExtractor, create_feature_extractor
from talent_customizer import TalentCustomizer, create_customizer
from multi_stage_customizer import MultiStageTalentCustomizer, create_multi_stage_customizer
from task_stage import TaskStage, get_stage_sequence


def create_talent_guardrail():
    """
    创建天赋定制Guardrail节点（单阶段模式）

    这个函数返回一个可以直接用作LangGraph节点的函数
    符合SKILL.md中的API声明

    Returns:
        Guardrail函数
    """
    return talent_customization_guardrail


# ============================================================================
# 数据结构定义
# ============================================================================

class AppState(TypedDict):
    """
    LangGraph State格式

    支持单阶段和多阶段两种模式
    """
    # 基础字段
    task: str                           # 原始任务
    task_features: Optional[dict]       # 任务特征（由Guardrail填充）
    conversation_history: Annotated[list, add]     # 对话历史
    current_node: str                   # 当前节点

    # 单阶段模式字段（向后兼容）
    matched_talents: list               # 匹配到的天赋列表（由Guardrail填充）
    custom_talent_prompt: Optional[str] # 定制的天赋Prompt（由Guardrail填充）
    customization_rationale: str        # 定制理由

    # 多阶段模式字段（新增）
    use_multi_stage: bool               # 是否使用多阶段模式（默认False）
    current_stage: Optional[str]        # 当前阶段（planning/execution/optimization/review）
    planning_prompt: Optional[str]      # 规划阶段Prompt
    execution_prompt: Optional[str]     # 执行阶段Prompt
    optimization_prompt: Optional[str]  # 优化阶段Prompt
    review_prompt: Optional[str]        # 审查阶段Prompt
    stage_history: list                 # 阶段历史记录

    # 执行结果字段
    talent_enhanced: bool               # 是否使用了天赋增强
    execution_result: Optional[str]     # 执行结果


# ============================================================================
# LangGraph State Guardrail
# ============================================================================

def talent_customization_guardrail(state: AppState) -> AppState:
    """
    State Guardrail: 为任务定制天赋Prompt

    在state更新时，提取任务特征，匹配天赋，定制Prompt，注入到state
    在合适的契机（state更新）自动触发

    Args:
        state: LangGraph的State

    Returns:
        更新后的State
    """
    # 提取任务
    task = state.get("task", "")
    if not task:
        # 没有任务，直接返回
        return state

    print(f"\n{'='*60}")
    print(f"🎯 State Guardrail触发：为任务定制天赋Prompt")
    print(f"{'='*60}")
    print(f"当前任务: {task}")

    # 初始化组件（实际使用时应该在外部初始化并传入）
    feature_extractor = create_feature_extractor()
    customizer = create_customizer()

    # 1. 提取任务特征
    print(f"\n📊 步骤1：提取任务特征")
    task_features = feature_extractor.extract(task)

    print(f"  任务类型: {task_features.task_type.value}")
    print(f"  复杂度: {task_features.complexity.value}")
    print(f"  输出格式: {task_features.output_format.value}")
    print(f"  时间压力: {task_features.time_pressure.value}")
    print(f"  精度要求: {task_features.precision.value}")

    # 2. 定制天赋Prompt
    print(f"\n🎨 步骤2：定制天赋Prompt")
    customization_result = customizer.customize(task, task_features)

    # 3. 注入到state（附加属性，不覆盖原有字段）
    state["task_features"] = {
        "task_type": task_features.task_type.value,
        "complexity": task_features.complexity.value,
        "output_format": task_features.output_format.value,
        "time_pressure": task_features.time_pressure.value,
        "precision": task_features.precision.value,
        "domain": task_features.domain,
        "keywords": task_features.keywords
    }
    state["matched_talents"] = customization_result.selected_talents
    state["custom_talent_prompt"] = customization_result.custom_talent_prompt
    state["customization_rationale"] = customization_result.customization_rationale

    print(f"✓ 天赋定制完成")
    print(f"  匹配天赋: {len(customization_result.selected_talents)}个")
    print(f"  天赋列表: {', '.join([t[:10] for t in customization_result.selected_talents])}")

    return state


# ============================================================================
# 辅助函数
# ============================================================================

def get_active_prompt(state: AppState) -> str:
    """
    获取当前激活的Prompt

    根据State中的模式自动选择合适的Prompt：
    - 如果是多阶段模式且当前阶段有Prompt，返回阶段Prompt
    - 否则返回单阶段Prompt（custom_talent_prompt）

    Args:
        state: LangGraph的State

    Returns:
        当前激活的Prompt字符串
    """
    # 检查是否是多阶段模式
    use_multi_stage = state.get("use_multi_stage", False)
    current_stage = state.get("current_stage")

    if use_multi_stage and current_stage:
        # 多阶段模式：获取当前阶段的Prompt
        stage_prompt_field = f"{current_stage}_prompt"
        stage_prompt = state.get(stage_prompt_field, "")

        if stage_prompt:
            print(f"✓ 使用多阶段Prompt: {current_stage}_prompt")
            return stage_prompt

    # 单阶段模式或后备方案
    single_prompt = state.get("custom_talent_prompt", "")
    if single_prompt:
        print(f"✓ 使用单阶段Prompt")

    return single_prompt


# ============================================================================
# 多阶段LangGraph Guardrail节点
# ============================================================================

def planning_stage_guardrail(state: AppState) -> AppState:
    """
    规划阶段Guardrail：为规划阶段定制天赋Prompt

    Args:
        state: LangGraph的State

    Returns:
        更新后的State
    """
    task = state.get("task", "")
    if not task:
        return state

    print(f"\n{'='*60}")
    print(f"📋 规划阶段Guardrail触发")
    print(f"{'='*60}")

    # 初始化组件
    feature_extractor = create_feature_extractor()
    multi_customizer = create_multi_stage_customizer()

    # 1. 提取任务特征
    task_features = feature_extractor.extract(task)

    # 2. 为规划阶段定制Prompt
    result = multi_customizer.customize_by_stage(task, TaskStage.PLANNING, task_features)

    # 3. 注入到state
    state["use_multi_stage"] = True
    state["current_stage"] = TaskStage.PLANNING.value
    state["planning_prompt"] = result.custom_stage_prompt
    state["task_features"] = result.task_features
    state["matched_talents"] = result.selected_talents

    # 记录阶段历史
    if "stage_history" not in state:
        state["stage_history"] = []
    state["stage_history"].append({
        "stage": TaskStage.PLANNING.value,
        "timestamp": len(state["stage_history"])
    })

    print(f"✓ 规划阶段定制完成")
    print(f"  匹配天赋: {', '.join(result.selected_talents[:3])}...")

    return state


def execution_stage_guardrail(state: AppState) -> AppState:
    """
    执行阶段Guardrail：为执行阶段定制天赋Prompt

    Args:
        state: LangGraph的State

    Returns:
        更新后的State
    """
    task = state.get("task", "")
    if not task:
        return state

    print(f"\n{'='*60}")
    print(f"⚡ 执行阶段Guardrail触发")
    print(f"{'='*60}")

    # 初始化组件
    multi_customizer = create_multi_stage_customizer()

    # 1. 提取任务特征（复用已有的或重新提取）
    if state.get("task_features"):
        from task_feature_extractor import TaskFeatures
        task_features_dict = state["task_features"]
        # 简化：直接使用已提取的特征
        # 实际应该转换为TaskFeatures对象
        task_features = create_feature_extractor().extract(task)
    else:
        task_features = create_feature_extractor().extract(task)

    # 2. 为执行阶段定制Prompt
    result = multi_customizer.customize_by_stage(task, TaskStage.EXECUTION, task_features)

    # 3. 注入到state
    state["current_stage"] = TaskStage.EXECUTION.value
    state["execution_prompt"] = result.custom_stage_prompt
    state["matched_talents"] = result.selected_talents

    # 记录阶段历史
    if "stage_history" not in state:
        state["stage_history"] = []
    state["stage_history"].append({
        "stage": TaskStage.EXECUTION.value,
        "timestamp": len(state["stage_history"])
    })

    print(f"✓ 执行阶段定制完成")
    print(f"  匹配天赋: {', '.join(result.selected_talents[:3])}...")

    return state


def optimization_stage_guardrail(state: AppState) -> AppState:
    """
    优化阶段Guardrail：为优化阶段定制天赋Prompt

    Args:
        state: LangGraph的State

    Returns:
        更新后的State
    """
    task = state.get("task", "")
    if not task:
        return state

    print(f"\n{'='*60}")
    print(f"🔄 优化阶段Guardrail触发")
    print(f"{'='*60}")

    # 初始化组件
    multi_customizer = create_multi_stage_customizer()
    task_features = create_feature_extractor().extract(task)

    # 为优化阶段定制Prompt
    result = multi_customizer.customize_by_stage(task, TaskStage.OPTIMIZATION, task_features)

    # 注入到state
    state["current_stage"] = TaskStage.OPTIMIZATION.value
    state["optimization_prompt"] = result.custom_stage_prompt
    state["matched_talents"] = result.selected_talents

    # 记录阶段历史
    if "stage_history" not in state:
        state["stage_history"] = []
    state["stage_history"].append({
        "stage": TaskStage.OPTIMIZATION.value,
        "timestamp": len(state["stage_history"])
    })

    print(f"✓ 优化阶段定制完成")
    print(f"  匹配天赋: {', '.join(result.selected_talents[:3])}...")

    return state


def review_stage_guardrail(state: AppState) -> AppState:
    """
    审查阶段Guardrail：为审查阶段定制天赋Prompt

    Args:
        state: LangGraph的State

    Returns:
        更新后的State
    """
    task = state.get("task", "")
    if not task:
        return state

    print(f"\n{'='*60}")
    print(f"👁️ 审查阶段Guardrail触发")
    print(f"{'='*60}")

    # 初始化组件
    multi_customizer = create_multi_stage_customizer()
    task_features = create_feature_extractor().extract(task)

    # 为审查阶段定制Prompt
    result = multi_customizer.customize_by_stage(task, TaskStage.REVIEW, task_features)

    # 注入到state
    state["current_stage"] = TaskStage.REVIEW.value
    state["review_prompt"] = result.custom_stage_prompt
    state["matched_talents"] = result.selected_talents

    # 记录阶段历史
    if "stage_history" not in state:
        state["stage_history"] = []
    state["stage_history"].append({
        "stage": TaskStage.REVIEW.value,
        "timestamp": len(state["stage_history"])
    })

    print(f"✓ 审查阶段定制完成")
    print(f"  匹配天赋: {', '.join(result.selected_talents[:3])}...")

    return state


# ============================================================================
# LangGraph节点示例
# ============================================================================

def reasoning_node(state: AppState) -> AppState:
    """
    推理节点：使用定制化的天赋Prompt

    支持单阶段和多阶段两种模式，自动选择合适的Prompt

    Args:
        state: LangGraph的State

    Returns:
        更新后的State
    """
    task = state["task"]
    task_features = state.get("task_features", {})

    print(f"\n{'='*60}")
    print(f"🧠 推理节点执行")
    print(f"{'='*60}")

    # 获取当前激活的Prompt（自动选择单阶段或多阶段）
    custom_prompt = get_active_prompt(state)

    if custom_prompt:
        use_multi_stage = state.get("use_multi_stage", False)
        current_stage = state.get("current_stage", "未知")

        print(f"✓ 使用定制天赋Prompt")
        print(f"  模式: {'多阶段' if use_multi_stage else '单阶段'}")
        print(f"  当前阶段: {current_stage}")
        print(f"  任务: {task}")
        print(f"  任务类型: {task_features.get('task_type', '未知')}")
        print(f"  匹配天赋数: {len(state.get('matched_talents', []))}")

        # 在实际使用中，这里会调用模型执行任务
        # 模型可以使用定制化的天赋Prompt
        enhanced_prompt = f"{task}\n\n{custom_prompt}"

        # 模拟模型调用
        response = f"[这是基于定制天赋Prompt的执行结果]\n任务: {task}\n使用天赋: {', '.join(state['matched_talents'])}\n当前阶段: {current_stage}"

        state["talent_enhanced"] = True
    else:
        print(f"✗ 未使用天赋Prompt")
        response = f"[这是常规执行结果]\n任务: {task}"

        state["talent_enhanced"] = False

    # 添加到对话历史
    state["conversation_history"].append({
        "role": "user",
        "content": task
    })
    state["conversation_history"].append({
        "role": "assistant",
        "content": response
    })

    print(f"✅ 推理完成")
    return state


# ============================================================================
# LangGraph工作流示例
# ============================================================================

def create_workflow():
    """
    创建LangGraph工作流

    工作流：
    State Guardrail（天赋定制）→ 推理节点（使用定制Prompt）

    Returns:
        LangGraph的CompiledGraph对象
    """
    try:
        from langgraph.graph import StateGraph, END

        # 创建工作流
        workflow = StateGraph(AppState)

        # 添加节点
        workflow.add_node("talent_customization", talent_customization_guardrail)
        workflow.add_node("reasoning", reasoning_node)

        # 添加边
        workflow.set_entry_point("talent_customization")
        workflow.add_edge("talent_customization", "reasoning")
        workflow.add_edge("reasoning", END)

        # 编译工作流
        app = workflow.compile()

        return app

    except ImportError:
        print("⚠️  langgraph库未安装，无法创建工作流")
        print("   安装命令: pip install langgraph")
        return None


def create_multi_stage_workflow():
    """
    创建多阶段LangGraph工作流

    工作流：
    规划阶段 → 执行阶段 → 优化阶段 → 审查阶段
    每个阶段都有对应的Guardrail注入定制Prompt

    Returns:
        LangGraph的CompiledGraph对象
    """
    try:
        from langgraph.graph import StateGraph, END

        # 创建工作流
        workflow = StateGraph(AppState)

        # 添加多阶段节点
        workflow.add_node("planning_stage", planning_stage_guardrail)
        workflow.add_node("execution_stage", execution_stage_guardrail)
        workflow.add_node("optimization_stage", optimization_stage_guardrail)
        workflow.add_node("review_stage", review_stage_guardrail)

        # 添加推理节点（在每个阶段后执行）
        workflow.add_node("planning_reasoning", reasoning_node)
        workflow.add_node("execution_reasoning", reasoning_node)
        workflow.add_node("optimization_reasoning", reasoning_node)
        workflow.add_node("review_reasoning", reasoning_node)

        # 设置流程：规划 → 规划推理 → 执行 → 执行推理 → 优化 → 优化推理 → 审查 → 审查推理 → 结束
        workflow.set_entry_point("planning_stage")
        workflow.add_edge("planning_stage", "planning_reasoning")
        workflow.add_edge("planning_reasoning", "execution_stage")
        workflow.add_edge("execution_stage", "execution_reasoning")
        workflow.add_edge("execution_reasoning", "optimization_stage")
        workflow.add_edge("optimization_stage", "optimization_reasoning")
        workflow.add_edge("optimization_reasoning", "review_stage")
        workflow.add_edge("review_stage", "review_reasoning")
        workflow.add_edge("review_reasoning", END)

        # 编译工作流
        app = workflow.compile()

        return app

    except ImportError:
        print("⚠️  langgraph库未安装，无法创建工作流")
        print("   安装命令: pip install langgraph")
        return None


# ============================================================================
# 示例使用
# ============================================================================

def example_usage_without_langgraph():
    """
    不使用LangGraph的示例用法
    直接调用State Guardrail函数
    """
    print("=" * 60)
    print("示例：直接使用State Guardrail（无需LangGraph）")
    print("=" * 60)

    # 初始化State
    state: AppState = {
        "task": "帮我制定一个详细的3年职业发展计划",
        "task_features": None,
        "matched_talents": [],
        "custom_talent_prompt": None,
        "customization_rationale": "",
        "conversation_history": [],
        "current_node": "start"
    }

    # 执行天赋定制Guardrail
    print("\n步骤1：天赋定制Guardrail")
    state = talent_customization_guardrail(state)

    # 执行推理节点
    print("\n步骤2：推理节点")
    state = reasoning_node(state)

    # 输出结果
    print("\n" + "=" * 60)
    print("最终结果")
    print("=" * 60)
    print(f"任务：{state['task']}")
    print(f"任务特征：{state['task_features']}")
    print(f"匹配天赋：{state['matched_talents']}")
    print(f"是否使用天赋增强：{state.get('talent_enhanced', False)}")
    print(f"\n定制Prompt：")
    print(state['custom_talent_prompt'])


def example_usage_with_langgraph():
    """
    使用LangGraph的示例用法

    注意：需要先安装langgraph库
    """
    print("=" * 60)
    print("示例：使用LangGraph工作流")
    print("=" * 60)

    # 创建工作流
    app = create_workflow()

    if app is None:
        return

    # 初始化State
    initial_state: AppState = {
        "task": "我想设计一个创意的产品方案",
        "task_features": None,
        "matched_talents": [],
        "custom_talent_prompt": None,
        "customization_rationale": "",
        "conversation_history": [],
        "current_node": "start",
        # 多阶段字段（默认值）
        "use_multi_stage": False,
        "current_stage": None,
        "planning_prompt": None,
        "execution_prompt": None,
        "optimization_prompt": None,
        "review_prompt": None,
        "stage_history": [],
        "talent_enhanced": False,
        "execution_result": None
    }

    # 执行工作流
    print("\n执行工作流...")
    result = app.invoke(initial_state)

    # 输出结果
    print("\n" + "=" * 60)
    print("工作流执行结果")
    print("=" * 60)
    print(f"任务：{result['task']}")
    print(f"任务特征：{result['task_features']}")
    print(f"匹配天赋：{result['matched_talents']}")
    print(f"是否使用天赋增强：{result.get('talent_enhanced', False)}")


def example_usage_multi_stage():
    """
    多阶段工作流示例

    展示如何在LangGraph中使用多阶段天赋定制
    """
    print("=" * 80)
    print("示例：多阶段天赋定制工作流")
    print("=" * 80)

    # 创建多阶段工作流
    app = create_multi_stage_workflow()

    if app is None:
        return

    # 初始化State
    initial_state: AppState = {
        "task": "帮我制定一个详细的3年职业发展计划",
        "task_features": None,
        "matched_talents": [],
        "custom_talent_prompt": None,
        "customization_rationale": "",
        "conversation_history": [],
        "current_node": "start",
        # 多阶段字段
        "use_multi_stage": True,
        "current_stage": None,
        "planning_prompt": None,
        "execution_prompt": None,
        "optimization_prompt": None,
        "review_prompt": None,
        "stage_history": [],
        "talent_enhanced": False,
        "execution_result": None
    }

    # 执行工作流
    print("\n执行多阶段工作流...")
    print("将依次经过：规划 → 执行 → 优化 → 审查 四个阶段\n")
    result = app.invoke(initial_state)

    # 输出结果
    print("\n" + "=" * 80)
    print("多阶段工作流执行结果")
    print("=" * 80)
    print(f"任务：{result['task']}")
    print(f"使用多阶段模式：{result.get('use_multi_stage', False)}")
    print(f"阶段历史：{result.get('stage_history', [])}")
    print(f"是否使用天赋增强：{result.get('talent_enhanced', False)}")

    # 展示每个阶段的Prompt
    print("\n" + "=" * 80)
    print("各阶段定制Prompt")
    print("=" * 80)

    stages = ["planning", "execution", "optimization", "review"]
    stage_names = {
        "planning": "规划阶段",
        "execution": "执行阶段",
        "optimization": "优化阶段",
        "review": "审查阶段"
    }

    for stage in stages:
        prompt_field = f"{stage}_prompt"
        prompt = result.get(prompt_field)
        if prompt:
            print(f"\n【{stage_names[stage]}】")
            print("-" * 80)
            print(prompt[:300] + "...")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='LangGraph Guardrail集成示例')
    parser.add_argument(
        '--with-langgraph',
        action='store_true',
        help='使用LangGraph工作流（需要安装langgraph库）'
    )
    parser.add_argument(
        '--multi-stage',
        action='store_true',
        help='使用多阶段工作流（需要安装langgraph库）'
    )

    args = parser.parse_args()

    if args.multi_stage:
        example_usage_multi_stage()
    elif args.with_langgraph:
        example_usage_with_langgraph()
    else:
        example_usage_without_langgraph()
