"""
补全效果评估器模块

职责：评估补全效果，记录经验数据，优化推荐策略
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class EffectivenessMetrics:
    """效果指标数据结构"""
    match_score_improvement: float  # 能力匹配度提升
    task_completion_rate_improvement: float  # 任务完成率提升
    execution_time_reduction: float  # 执行时间减少
    error_rate_reduction: float  # 错误率降低
    overall_effectiveness: float  # 综合效果分数


@dataclass
class LessonLearned:
    """经验教训数据结构"""
    lesson_id: str
    gap_type: str
    recommended_skills: List[str]
    effectiveness_score: float
    success: bool
    reason: str
    timestamp: str


class RemediationEffectivenessEvaluator:
    """
    补全效果评估器（模块N）

    职责边界：
    - 对比补全前后的能力变化
    - 量化补全效果
    - 记录经验教训
    - 优化推荐策略
    """

    def __init__(self):
        self.lessons_database = {}  # 经验数据库
        self.learning_db_path = None

    def load_lessons_database(self, db_path: str):
        """加载经验数据库"""
        self.learning_db_path = db_path
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                self.lessons_database = json.load(f)
        except Exception as e:
            print(f"加载经验数据库失败: {e}")
            self.lessons_database = {}

    def save_lessons_database(self, db_path: Optional[str] = None):
        """保存经验数据库"""
        path = db_path or self.learning_db_path
        if not path:
            print("未指定数据库路径")
            return

        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.lessons_database, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存经验数据库失败: {e}")

    def evaluate_effectiveness(
        self,
        pre_remediation_state: Dict[str, Any],
        post_remediation_state: Dict[str, Any],
        remedy_plan: Dict[str, Any],
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        评估补全效果

        Args:
            pre_remediation_state: 补全前状态
            post_remediation_state: 补全后状态
            remedy_plan: 补全方案
            execution_result: 执行结果

        Returns:
            效果评估报告
        """
        # 1. 计算效果指标
        metrics = self._calculate_metrics(
            pre_remediation_state,
            post_remediation_state
        )

        # 2. 判断是否成功
        success = self._determine_success(metrics, execution_result)

        # 3. 记录经验教训
        lesson = self._extract_lesson(
            remedy_plan,
            metrics,
            success,
            execution_result
        )

        # 4. 更新数据库
        self._update_lessons_database(lesson)

        # 5. 生成评估报告
        return {
            "effectiveness_metrics": self._metrics_to_dict(metrics),
            "success": success,
            "lesson": self._lesson_to_dict(lesson),
            "recommendation_updates": self._generate_recommendation_updates(lesson),
            "evaluated_at": datetime.now().isoformat()
        }

    def _calculate_metrics(
        self,
        pre_state: Dict[str, Any],
        post_state: Dict[str, Any]
    ) -> EffectivenessMetrics:
        """
        计算效果指标

        Args:
            pre_state: 补全前状态
            post_state: 补全后状态

        Returns:
            效果指标
        """
        # 1. 能力匹配度提升
        pre_match = pre_state.get("match_score", 0.0)
        post_match = post_state.get("match_score", 0.0)
        match_improvement = post_match - pre_match

        # 2. 任务完成率提升
        pre_task_rate = pre_state.get("task_completion_rate", 0.5)
        post_task_rate = post_state.get("task_completion_rate", 0.5)
        task_rate_improvement = post_task_rate - pre_task_rate

        # 3. 执行时间减少
        pre_time = pre_state.get("execution_time", 100.0)
        post_time = post_state.get("execution_time", 100.0)
        time_reduction = (pre_time - post_time) / pre_time if pre_time > 0 else 0.0

        # 4. 错误率降低
        pre_error = pre_state.get("error_count", 10)
        post_error = post_state.get("error_count", 10)
        error_reduction = (pre_error - post_error) / pre_error if pre_error > 0 else 0.0

        # 5. 综合效果分数
        overall = (
            0.4 * max(match_improvement, 0) +
            0.3 * max(task_rate_improvement, 0) +
            0.2 * max(time_reduction, 0) +
            0.1 * max(error_reduction, 0)
        )

        return EffectivenessMetrics(
            match_score_improvement=match_improvement,
            task_completion_rate_improvement=task_rate_improvement,
            execution_time_reduction=time_reduction,
            error_rate_reduction=error_reduction,
            overall_effectiveness=overall
        )

    def _determine_success(
        self,
        metrics: EffectivenessMetrics,
        execution_result: Dict[str, Any]
    ) -> bool:
        """
        判断补全是否成功

        Args:
            metrics: 效果指标
            execution_result: 执行结果

        Returns:
            是否成功
        """
        # 综合效果分数 >= 0.3 认为成功
        if metrics.overall_effectiveness >= 0.3:
            return True

        # 或者执行结果明确表示成功
        if execution_result.get("status") == "success":
            return True

        return False

    def _extract_lesson(
        self,
        remedy_plan: Dict[str, Any],
        metrics: EffectivenessMetrics,
        success: bool,
        execution_result: Dict[str, Any]
    ) -> LessonLearned:
        """
        提取经验教训

        Args:
            remedy_plan: 补全方案
            metrics: 效果指标
            success: 是否成功
            execution_result: 执行结果

        Returns:
            经验教训
        """
        # 获取推荐技能列表
        recommended_skills = []
        for plan in ["primary_plan", "alternative_plan", "quick_fix_plan"]:
            plan_data = remedy_plan.get("recommendations", {}).get(plan, {})
            skills = plan_data.get("recommended_skills", [])
            for skill in skills:
                recommended_skills.append(skill.get("skill_id", ""))

        # 生成原因描述
        reason = self._generate_reason(metrics, success, execution_result)

        return LessonLearned(
            lesson_id=f"lesson_{datetime.now().timestamp()}",
            gap_type=remedy_plan.get("gap_analysis", {}).get("gaps", [{}])[0].get("gap_type", "unknown"),
            recommended_skills=list(set(recommended_skills)),
            effectiveness_score=metrics.overall_effectiveness,
            success=success,
            reason=reason,
            timestamp=datetime.now().isoformat()
        )

    def _generate_reason(
        self,
        metrics: EffectivenessMetrics,
        success: bool,
        execution_result: Dict[str, Any]
    ) -> str:
        """生成原因描述"""
        if success:
            reasons = []
            if metrics.match_score_improvement > 0.2:
                reasons.append(f"能力匹配度提升{metrics.match_score_improvement:.1%}")
            if metrics.task_completion_rate_improvement > 0.2:
                reasons.append(f"任务完成率提升{metrics.task_completion_rate_improvement:.1%}")
            if metrics.execution_time_reduction > 0.1:
                reasons.append(f"执行时间减少{metrics.execution_time_reduction:.1%}")
            return "；".join(reasons) if reasons else "整体效果良好"
        else:
            # 失败原因
            if metrics.overall_effectiveness < 0.1:
                return "效果不明显，可能技能匹配度不够"
            elif execution_result.get("error"):
                return f"执行错误: {execution_result.get('error', '未知错误')}"
            else:
                return "未达到预期效果"

    def _update_lessons_database(self, lesson: LessonLearned):
        """
        更新经验数据库

        Args:
            lesson: 经验教训
        """
        # 为每个技能更新统计
        for skill_id in lesson.recommended_skills:
            if skill_id not in self.lessons_database:
                self.lessons_database[skill_id] = {
                    "skill_id": skill_id,
                    "total_count": 0,
                    "success_count": 0,
                    "total_effectiveness": 0.0,
                    "last_used": None,
                    "lessons": []
                }

            # 更新统计
            self.lessons_database[skill_id]["total_count"] += 1
            if lesson.success:
                self.lessons_database[skill_id]["success_count"] += 1
            self.lessons_database[skill_id]["total_effectiveness"] += lesson.effectiveness_score
            self.lessons_database[skill_id]["last_used"] = lesson.timestamp

            # 添加经验记录
            self.lessons_database[skill_id]["lessons"].append(self._lesson_to_dict(lesson))

        # 自动保存
        self.save_lessons_database()

    def _generate_recommendation_updates(
        self,
        lesson: LessonLearned
    ) -> Dict[str, Any]:
        """
        生成推荐策略更新建议

        Args:
            lesson: 经验教训

        Returns:
            更新建议
        """
        updates = {}

        for skill_id in lesson.recommended_skills:
            if skill_id in self.lessons_database:
                skill_data = self.lessons_database[skill_id]

                # 计算成功率
                success_rate = skill_data["success_count"] / skill_data["total_count"] if skill_data["total_count"] > 0 else 0
                avg_effectiveness = skill_data["total_effectiveness"] / skill_data["total_count"] if skill_data["total_count"] > 0 else 0

                # 生成更新建议
                if success_rate < 0.5:
                    updates[skill_id] = {
                        "action": "reduce_weight",
                        "reason": f"成功率较低({success_rate:.1%})",
                        "new_weight": 0.5
                    }
                elif success_rate > 0.8 and avg_effectiveness > 0.4:
                    updates[skill_id] = {
                        "action": "increase_weight",
                        "reason": f"成功率高({success_rate:.1%})且效果好({avg_effectiveness:.2f})",
                        "new_weight": 1.2
                    }
                else:
                    updates[skill_id] = {
                        "action": "maintain",
                        "reason": "表现稳定",
                        "new_weight": 1.0
                    }

        return updates

    def _metrics_to_dict(self, metrics: EffectivenessMetrics) -> Dict[str, float]:
        """将指标对象转换为字典"""
        return {
            "match_score_improvement": metrics.match_score_improvement,
            "task_completion_rate_improvement": metrics.task_completion_rate_improvement,
            "execution_time_reduction": metrics.execution_time_reduction,
            "error_rate_reduction": metrics.error_rate_reduction,
            "overall_effectiveness": metrics.overall_effectiveness
        }

    def _lesson_to_dict(self, lesson: LessonLearned) -> Dict[str, Any]:
        """将经验对象转换为字典"""
        return {
            "lesson_id": lesson.lesson_id,
            "gap_type": lesson.gap_type,
            "recommended_skills": lesson.recommended_skills,
            "effectiveness_score": lesson.effectiveness_score,
            "success": lesson.success,
            "reason": lesson.reason,
            "timestamp": lesson.timestamp
        }

    def get_skill_statistics(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """
        获取技能统计信息

        Args:
            skill_id: 技能ID

        Returns:
            统计信息
        """
        if skill_id not in self.lessons_database:
            return None

        data = self.lessons_database[skill_id]
        total_count = data["total_count"]

        return {
            "skill_id": skill_id,
            "total_count": total_count,
            "success_count": data["success_count"],
            "success_rate": data["success_count"] / total_count if total_count > 0 else 0,
            "average_effectiveness": data["total_effectiveness"] / total_count if total_count > 0 else 0,
            "last_used": data["last_used"],
            "recent_lessons": data["lessons"][-5:]  # 最近5条经验
        }


def main():
    """命令行接口（用于测试）"""
    import argparse

    parser = argparse.ArgumentParser(description="补全效果评估器")
    parser.add_argument("--pre-state", required=True, help="补全前状态JSON文件")
    parser.add_argument("--post-state", required=True, help="补全后状态JSON文件")
    parser.add_argument("--remedy-plan", required=True, help="补全方案JSON文件")
    parser.add_argument("--execution-result", required=True, help="执行结果JSON文件")
    parser.add_argument("--lessons-db", default="lessons_database.json", help="经验数据库JSON文件")
    parser.add_argument("--output", required=True, help="输出文件路径")

    args = parser.parse_args()

    # 创建评估器
    evaluator = RemediationEffectivenessEvaluator()

    # 加载经验数据库
    evaluator.load_lessons_database(args.lessons_db)

    # 加载数据
    with open(args.pre_state, 'r', encoding='utf-8') as f:
        pre_state = json.load(f)

    with open(args.post_state, 'r', encoding='utf-8') as f:
        post_state = json.load(f)

    with open(args.remedy_plan, 'r', encoding='utf-8') as f:
        remedy_plan = json.load(f)

    with open(args.execution_result, 'r', encoding='utf-8') as f:
        execution_result = json.load(f)

    # 评估效果
    evaluation = evaluator.evaluate_effectiveness(
        pre_state,
        post_state,
        remedy_plan,
        execution_result
    )

    # 输出结果
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(evaluation, f, ensure_ascii=False, indent=2)

    print(f"效果评估已完成: {args.output}")
    print(f"是否成功: {evaluation['success']}")
    print(f"综合效果分数: {evaluation['effectiveness_metrics']['overall_effectiveness']:.2f}")
    print(f"经验数据库已更新: {args.lessons_db}")


if __name__ == "__main__":
    main()
