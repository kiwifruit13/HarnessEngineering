#!/usr/bin/env python3
"""
RAG系统评估脚本

使用方法：
    python evaluate.py --config config.json --test-data test_cases.json

输出：
    - 评估报告（JSON）
    - 可览化图表（可选）
"""

import os
import argparse
import json
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class TestCase:
    """测试用例"""
    query: str
    expected_answer: str
    expected_doc_ids: List[str]
    category: Optional[str] = None
    difficulty: Optional[str] = None  # easy, medium, hard


@dataclass
class EvaluationResult:
    """评估结果"""
    query: str
    retrieved_docs: List[str]
    generated_answer: str
    retrieval_metrics: Dict[str, float]
    generation_metrics: Dict[str, float]
    latency_ms: float


class RAGEvaluator:
    """RAG系统评估器"""

    # 豆包 API 配置
    DOUBAO_API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    DOUBAO_MODEL = "ep-20250325180736-fc9d8"  # 默认豆包模型端点 ID

    def __init__(self, rag_system, config: Dict = None):
        """
        初始化评估器

        Args:
            rag_system: RAG系统实例
            config: 评估配置
        """
        self.rag = rag_system
        self.config = config or {}

        # 获取 Doubao API 凭证（支持自动获取和手动配置）
        self.api_key, self.credential_source = self._get_doubao_api_key()

        # 使用平台 SDK 的 requests
        self.requests_client = None
        if self.api_key:
            try:
                from coze_workload_identity import requests
                self.requests_client = requests
                logger.info(f"✓ 凭证获取成功（来源: {self.credential_source}），使用平台 SDK 进行 API 调用")
                logger.info(f"✓ 使用豆包（Doubao）大模型进行评估")
            except Exception as e:
                logger.warning(f"平台 SDK 初始化失败: {e}")
        else:
            logger.warning("✗ 未找到 Doubao API Key，LLM 评估功能将不可用")

        # 默认配置
        self.metrics_config = {
            'recall_k': [5, 10, 20],
            'precision_k': [5, 10],
            'use_llm_judge': True,
            'llm_model': self.DOUBAO_MODEL
        }
        self.metrics_config.update(self.config.get('metrics', {}))

    def _get_doubao_api_key(self) -> tuple[Optional[str], str]:
        """
        获取 Doubao API Key

        优先级：
        1. Workload Identity 自动获取（如果环境支持）
        2. 环境变量读取（用户手动配置）
        3. 返回 None（降级使用简单指标）

        Returns:
            (API Key 或 None, 凭证来源描述)
        """
        skill_id = "7625263899650293803"

        # 方式 1：尝试使用 Workload Identity 自动获取
        try:
            from coze_workload_identity.client import Client
            client = Client()
            api_key = client.get_integration_credential("doubao")

            if api_key:
                source = "Workload Identity (自动获取)"
                logger.info(f"✓ 通过 Workload Identity 自动获取 Doubao 凭证")
                return api_key, source
        except ImportError:
            logger.debug("coze_workload_identity.client 不可用")
        except Exception as e:
            logger.debug(f"Workload Identity 获取失败: {type(e).__name__}")

        # 方式 2：从环境变量读取（用户手动配置）
        api_key = os.getenv(f"COZE_DOUBAO_API_KEY_{skill_id}")
        if api_key:
            source = f"环境变量 COZE_DOUBAO_API_KEY_{skill_id} (手动配置)"
            logger.info(f"✓ 从环境变量读取 Doubao API Key")
            return api_key, source

        # 方式 3：尝试通用环境变量（备用）
        api_key = os.getenv("DOUBAO_API_KEY")
        if api_key:
            source = "环境变量 DOUBAO_API_KEY (备用)"
            logger.info(f"✓ 从 DOUBAO_API_KEY 读取")
            return api_key, source

        # 全部失败
        logger.warning("✗ 无法获取 Doubao API Key（所有方式均失败）")
        logger.warning("  可用方式：")
        logger.warning("    1. Workload Identity（需要环境变量支持）")
        logger.warning(f"    2. 环境变量 COZE_DOUBAO_API_KEY_{skill_id}")
        logger.warning("    3. 环境变量 DOUBAO_API_KEY（备用）")
        return None, "none"

    def evaluate(self, test_cases: List[TestCase]) -> Dict[str, Any]:
        """
        执行完整评估

        Args:
            test_cases: 测试用例列表

        Returns:
            评估报告
        """
        logger.info(f"开始评估，共 {len(test_cases)} 个测试用例")
        if self.api_key:
            logger.info(f"凭证来源: {self.credential_source}")
            logger.info(f"使用模型: {self.metrics_config['llm_model']}")
        else:
            logger.info("将使用简单指标（LLM 评估不可用）")

        results = []

        for i, case in enumerate(test_cases):
            logger.info(f"处理测试用例 {i+1}/{len(test_cases)}: {case.query[:50]}...")

            # 执行查询
            import time
            start_time = time.time()
            response = self.rag.query(case.query)
            latency = (time.time() - start_time) * 1000

            # 计算指标
            retrieval_metrics = self._calc_retrieval_metrics(
                response.get('sources', []),
                case.expected_doc_ids
            )

            generation_metrics = self._calc_generation_metrics(
                response.get('answer', ''),
                case.expected_answer,
                response.get('sources', []),
                case.query
            )

            results.append(EvaluationResult(
                query=case.query,
                retrieved_docs=response.get('sources', []),
                generated_answer=response.get('answer', ''),
                retrieval_metrics=retrieval_metrics,
                generation_metrics=generation_metrics,
                latency_ms=latency
            ))

        # 汇总报告
        report = self._generate_report(results, test_cases)

        return report

    def _calc_retrieval_metrics(self, retrieved: List, expected: List[str]) -> Dict[str, float]:
        """计算检索指标"""
        # 防御性处理：确保参数不为 None
        retrieved = retrieved or []
        expected = expected or []

        retrieved_ids = [doc.get('id', doc) if isinstance(doc, dict) else doc for doc in retrieved]

        metrics = {}

        # Recall@K
        for k in self.metrics_config['recall_k']:
            top_k = retrieved_ids[:k]
            if expected:
                recall = len(set(top_k) & set(expected)) / len(expected)
            else:
                recall = 0
            metrics[f'recall@{k}'] = recall

        # Precision@K
        for k in self.metrics_config['precision_k']:
            top_k = retrieved_ids[:k]
            if top_k:
                precision = len(set(top_k) & set(expected)) / len(top_k)
            else:
                precision = 0
            metrics[f'precision@{k}'] = precision

        # MRR (Mean Reciprocal Rank)
        mrr = 0
        for i, doc_id in enumerate(retrieved_ids):
            if expected and doc_id in expected:  # 修复：先检查 expected 不为空
                mrr = 1 / (i + 1)
                break
        metrics['mrr'] = mrr

        return metrics

    def _calc_generation_metrics(self, answer: str, expected: str,
                                  sources: List, query: str) -> Dict[str, float]:
        """计算生成指标"""
        metrics = {}

        if self.metrics_config['use_llm_judge'] and self.requests_client:
            # 使用LLM评估
            metrics['relevance'] = self._llm_judge_relevance(query, answer)
            metrics['faithfulness'] = self._llm_judge_faithfulness(answer, sources)
            metrics['completeness'] = self._llm_judge_completeness(answer, expected)
        else:
            # 使用简单指标
            metrics['answer_length'] = len(answer)
            metrics['overlap_score'] = self._calc_overlap(answer, expected)

        return metrics

    def _llm_judge_relevance(self, query: str, answer: str) -> float:
        """LLM评估相关性 - 使用豆包 API"""
        if not self.requests_client:
            logger.warning("平台 SDK 未初始化，使用默认值 0.5")
            return 0.5

        try:
            url = self.DOUBAO_API_URL
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": self.metrics_config['llm_model'],
                "messages": [{
                    "role": "user",
                    "content": f"""请评估答案与问题的相关性（0-1分）：

问题：{query}
答案：{answer}

只返回一个0到1之间的数字，不要其他内容。"""
                }],
                "max_tokens": 10,
                "temperature": 0.0
            }

            response = self.requests_client.post(
                url,
                headers=headers,
                json=data,
                timeout=30
            )

            # 检查HTTP状态码
            if response.status_code >= 400:
                raise Exception(f"HTTP请求失败: 状态码 {response.status_code}, 响应内容: {response.text}")

            result = response.json()

            # 错误处理
            if "error" in result:
                raise Exception(f"API错误: {result['error']}")

            # 豆包 API 响应格式（兼容 OpenAI）
            content = result['choices'][0]['message']['content']
            return float(content.strip())
        except Exception as e:
            logger.warning(f"LLM评估失败: {e}")
            return 0.5

    def _llm_judge_faithfulness(self, answer: str, sources: List) -> float:
        """LLM评估忠实度 - 使用豆包 API"""
        if not self.requests_client:
            logger.warning("平台 SDK 未初始化，使用默认值 0.5")
            return 0.5

        try:
            url = self.DOUBAO_API_URL
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            context = '\n\n'.join([str(s) for s in sources])
            data = {
                "model": self.metrics_config['llm_model'],
                "messages": [{
                    "role": "user",
                    "content": f"""请评估答案是否基于提供的上下文生成，有无幻觉（0-1分）：

上下文：{context}
答案：{answer}

只返回一个0到1之间的数字，不要其他内容。
1分表示完全基于上下文，0分表示完全无关或有明显幻觉。"""
                }],
                "max_tokens": 10,
                "temperature": 0.0
            }

            response = self.requests_client.post(
                url,
                headers=headers,
                json=data,
                timeout=30
            )

            # 检查HTTP状态码
            if response.status_code >= 400:
                raise Exception(f"HTTP请求失败: 状态码 {response.status_code}, 响应内容: {response.text}")

            result = response.json()

            # 错误处理
            if "error" in result:
                raise Exception(f"API错误: {result['error']}")

            # 豆包 API 响应格式（兼容 OpenAI）
            content = result['choices'][0]['message']['content']
            return float(content.strip())
        except Exception as e:
            logger.warning(f"LLM评估失败: {e}")
            return 0.5

    def _llm_judge_completeness(self, answer: str, expected: str) -> float:
        """LLM评估完整性 - 使用豆包 API"""
        if not self.requests_client:
            logger.warning("平台 SDK 未初始化，使用默认值 0.5")
            return 0.5

        try:
            url = self.DOUBAO_API_URL
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": self.metrics_config['llm_model'],
                "messages": [{
                    "role": "user",
                    "content": f"""请评估答案的完整性（0-1分）：

期望答案要点：{expected}
实际答案：{answer}

只返回一个0到1之间的数字，不要其他内容。"""
                }],
                "max_tokens": 10,
                "temperature": 0.0
            }

            response = self.requests_client.post(
                url,
                headers=headers,
                json=data,
                timeout=30
            )

            # 检查HTTP状态码
            if response.status_code >= 400:
                raise Exception(f"HTTP请求失败: 状态码 {response.status_code}, 响应内容: {response.text}")

            result = response.json()

            # 错误处理
            if "error" in result:
                raise Exception(f"API错误: {result['error']}")

            # 豆包 API 响应格式（兼容 OpenAI）
            content = result['choices'][0]['message']['content']
            return float(content.strip())
        except Exception as e:
            logger.warning(f"LLM评估失败: {e}")
            return 0.5

    def _calc_overlap(self, answer: str, expected: str) -> float:
        """计算文本重叠度"""
        # 防御性处理
        answer = answer or ""
        expected = expected or ""

        answer_words = set(answer.lower().split())
        expected_words = set(expected.lower().split())

        if not expected_words:
            return 0

        overlap = len(answer_words & expected_words) / len(expected_words)
        return overlap

    def _generate_report(self, results: List[EvaluationResult],
                         test_cases: List[TestCase]) -> Dict[str, Any]:
        """生成评估报告"""
        # 防御性处理：检查结果是否为空
        if not results:
            return {
                'summary': {
                    'total_cases': 0,
                    'retrieval': {},
                    'generation': {},
                    'performance': {}
                },
                'category_analysis': {},
                'difficulty_analysis': {},
                'detailed_results': []
            }

        # 汇总检索指标
        retrieval_summary = {}
        if results[0].retrieval_metrics:
            for metric in results[0].retrieval_metrics.keys():
                values = [r.retrieval_metrics.get(metric, 0) for r in results]
                retrieval_summary[metric] = {
                    'mean': sum(values) / len(values) if values else 0,
                    'min': min(values) if values else 0,
                    'max': max(values) if values else 0,
                    'median': sorted(values)[len(values) // 2] if values else 0
                }

        # 汇总生成指标
        generation_summary = {}
        if results[0].generation_metrics:
            for metric in results[0].generation_metrics.keys():
                values = [r.generation_metrics.get(metric, 0) for r in results]
                generation_summary[metric] = {
                    'mean': sum(values) / len(values) if values else 0,
                    'min': min(values) if values else 0,
                    'max': max(values) if values else 0,
                    'median': sorted(values)[len(values) // 2] if values else 0
                }

        # 汇总性能指标
        latencies = [r.latency_ms for r in results]
        performance_summary = {
            'avg_latency_ms': sum(latencies) / len(latencies) if latencies else 0,
            'p50_latency_ms': sorted(latencies)[len(latencies) // 2] if latencies else 0,
            'p95_latency_ms': sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 1 else (latencies[0] if latencies else 0),
            'p99_latency_ms': sorted(latencies)[int(len(latencies) * 0.99)] if len(latencies) > 1 else (latencies[0] if latencies else 0)
        }

        # 按类别分析
        category_analysis = {}
        for case, result in zip(test_cases, results):
            if case.category:
                if case.category not in category_analysis:
                    category_analysis[case.category] = []
                category_analysis[case.category].append(result)

        category_summary = {}
        for category, cat_results in category_analysis.items():
            category_summary[category] = {
                'count': len(cat_results),
                'avg_recall@5': sum(r.retrieval_metrics.get('recall@5', 0) for r in cat_results) / len(cat_results),
                'avg_relevance': sum(r.generation_metrics.get('relevance', 0) for r in cat_results) / len(cat_results)
            }

        # 按难度分析
        difficulty_analysis = {}
        for case, result in zip(test_cases, results):
            if case.difficulty:
                if case.difficulty not in difficulty_analysis:
                    difficulty_analysis[case.difficulty] = []
                difficulty_analysis[case.difficulty].append(result)

        difficulty_summary = {}
        for difficulty, diff_results in difficulty_analysis.items():
            difficulty_summary[difficulty] = {
                'count': len(diff_results),
                'avg_recall@5': sum(r.retrieval_metrics.get('recall@5', 0) for r in diff_results) / len(diff_results),
                'avg_relevance': sum(r.generation_metrics.get('relevance', 0) for r in diff_results) / len(diff_results)
            }

        return {
            'summary': {
                'total_cases': len(test_cases),
                'retrieval': retrieval_summary,
                'generation': generation_summary,
                'performance': performance_summary
            },
            'category_analysis': category_summary,
            'difficulty_analysis': difficulty_summary,
            'detailed_results': [
                {
                    'query': r.query,
                    'retrieval': r.retrieval_metrics,
                    'generation': r.generation_metrics,
                    'latency_ms': r.latency_ms
                }
                for r in results
            ]
        }


def load_test_cases(file_path: str) -> List[TestCase]:
    """加载测试用例"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return [
        TestCase(
            query=item['query'],
            expected_answer=item.get('expected_answer', ''),
            expected_doc_ids=item.get('expected_doc_ids', []),
            category=item.get('category'),
            difficulty=item.get('difficulty')
        )
        for item in data
    ]


def save_report(report: Dict, output_path: str):
    """保存评估报告"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    logger.info(f"报告已保存到: {output_path}")


def print_summary(report: Dict):
    """打印摘要"""
    print("\n" + "="*60)
    print("RAG系统评估报告")
    print("="*60)

    summary = report.get('summary', {})

    # 检索性能
    retrieval = summary.get('retrieval', {})
    if retrieval:
        print("\n📊 检索性能:")
        for metric, values in retrieval.items():
            if values and isinstance(values, dict):
                print(f"  {metric}: {values.get('mean', 0):.3f} (中位数: {values.get('median', 0):.3f})")

    # 生成质量
    generation = summary.get('generation', {})
    if generation:
        print("\n📝 生成质量:")
        for metric, values in generation.items():
            if values and isinstance(values, dict):
                print(f"  {metric}: {values.get('mean', 0):.3f}")

    # 性能指标
    performance = summary.get('performance', {})
    if performance:
        print("\n⚡ 性能指标:")
        print(f"  平均延迟: {performance.get('avg_latency_ms', 0):.1f}ms")
        print(f"  P95延迟: {performance.get('p95_latency_ms', 0):.1f}ms")

    if report.get('category_analysis'):
        print("\n📂 分类分析:")
        for category, stats in report['category_analysis'].items():
            if stats:
                print(f"  {category}: Recall@5={stats.get('avg_recall@5', 0):.3f}, 相关性={stats.get('avg_relevance', 0):.3f}")

    if report.get('difficulty_analysis'):
        print("\n🎯 难度分析:")
        for difficulty, stats in report['difficulty_analysis'].items():
            if stats:
                print(f"  {difficulty}: Recall@5={stats.get('avg_recall@5', 0):.3f}, 相关性={stats.get('avg_relevance', 0):.3f}")

    print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(description='RAG系统评估工具')
    parser.add_argument('--config', type=str, default='config.json', help='配置文件路径')
    parser.add_argument('--test-data', type=str, required=True, help='测试数据路径')
    parser.add_argument('--output', type=str, default='evaluation_report.json', help='输出报告路径')
    parser.add_argument('--verbose', action='store_true', help='详细输出')

    args = parser.parse_args()

    # 加载测试用例
    test_cases = load_test_cases(args.test_data)
    logger.info(f"已加载 {len(test_cases)} 个测试用例")

    # 这里需要替换为你的RAG系统实例
    # from your_rag import YourRAGSystem
    # rag = YourRAGSystem(config_path=args.config)

    # 示例：使用mock进行演示
    class MockRAG:
        def query(self, q):
            return {
                'answer': f"这是对'{q}'的回答",
                'sources': [{'id': f'doc_{i}'} for i in range(5)]
            }

    rag = MockRAG()

    # 执行评估
    evaluator = RAGEvaluator(rag)
    report = evaluator.evaluate(test_cases)

    # 保存报告
    save_report(report, args.output)

    # 打印摘要
    print_summary(report)


if __name__ == '__main__':
    main()
