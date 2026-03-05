import time
import json
from typing import List, Dict, Any, Tuple
from datetime import datetime

from rag.run import hr_qa


class RAGEvaluator:
    """
    RAG系统评估器
    """
    
    def __init__(self):
        self.evaluation_results = []
    
    def evaluate_single_question(self, question: str, expected_keywords: List[str] = None) -> Dict[str, Any]:
        """
        评估单个问题的回答质量
        
        Args:
            question: 测试问题
            expected_keywords: 期望答案中包含的关键词
        
        Returns:
            评估结果字典
        """
        start_time = time.time()
        
        # 获取系统回答
        result = hr_qa(question)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # 计算评估指标
        evaluation = {
            'question': question,
            'answer': result['answer'],
            'sources': result.get('sources', []),
            'confidence': result.get('confidence', 0.0),
            'document_count': result.get('document_count', 0),
            'response_time': response_time,
            'timestamp': datetime.now().isoformat()
        }
        
        # 关键词匹配评估
        if expected_keywords:
            answer_lower = result['answer'].lower()
            matched_keywords = [kw for kw in expected_keywords if kw.lower() in answer_lower]
            evaluation['keyword_match_score'] = len(matched_keywords) / len(expected_keywords)
            evaluation['matched_keywords'] = matched_keywords
            evaluation['expected_keywords'] = expected_keywords
        
        # 答案质量评估
        evaluation['answer_quality'] = self._assess_answer_quality(result)
        
        return evaluation
    
    def _assess_answer_quality(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        评估答案质量
        
        Args:
            result: 系统返回结果
        
        Returns:
            质量评估结果
        """
        answer = result['answer']
        sources = result.get('sources', [])
        confidence = result.get('confidence', 0.0)
        
        quality_metrics = {
            'has_answer': len(answer.strip()) > 0,
            'answer_length': len(answer),
            'has_sources': len(sources) > 0,
            'source_count': len(sources),
            'avg_source_confidence': sum(s['confidence'] for s in sources) / len(sources) if sources else 0.0,
            'overall_confidence': confidence,
            'contains_error_message': '错误' in answer or '抱歉' in answer,
            'is_informative': len(answer.split()) >= 10  # 至少10个词
        }
        
        # 计算综合质量分数
        score = 0.0
        if quality_metrics['has_answer']:
            score += 0.2
        if quality_metrics['has_sources']:
            score += 0.2
        if quality_metrics['avg_source_confidence'] > 0.7:
            score += 0.2
        if quality_metrics['is_informative']:
            score += 0.2
        if not quality_metrics['contains_error_message']:
            score += 0.2
        
        quality_metrics['quality_score'] = score
        
        return quality_metrics
    
    def batch_evaluate(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量评估测试用例
        
        Args:
            test_cases: 测试用例列表，每个包含 'question' 和可选的 'expected_keywords'
        
        Returns:
            批量评估结果
        """
        results = []
        total_start_time = time.time()
        
        for test_case in test_cases:
            question = test_case['question']
            expected_keywords = test_case.get('expected_keywords', [])
            
            result = self.evaluate_single_question(question, expected_keywords)
            results.append(result)
            
            print(f"已评估问题: {question[:50]}...")
        
        total_time = time.time() - total_start_time
        
        # 计算统计指标
        stats = self._calculate_batch_statistics(results, total_time)
        
        return {
            'individual_results': results,
            'statistics': stats,
            'total_questions': len(test_cases),
            'total_time': total_time
        }
    
    def _calculate_batch_statistics(self, results: List[Dict[str, Any]], total_time: float) -> Dict[str, Any]:
        """
        计算批量评估的统计指标
        
        Args:
            results: 个别评估结果列表
            total_time: 总耗时
        
        Returns:
            统计指标字典
        """
        if not results:
            return {}
        
        # 响应时间统计
        response_times = [r['response_time'] for r in results]
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        # 置信度统计
        confidences = [r['confidence'] for r in results]
        avg_confidence = sum(confidences) / len(confidences)
        
        # 质量分数统计
        quality_scores = [r['answer_quality']['quality_score'] for r in results]
        avg_quality_score = sum(quality_scores) / len(quality_scores)
        
        # 关键词匹配统计
        keyword_scores = [r.get('keyword_match_score', 0) for r in results if 'keyword_match_score' in r]
        avg_keyword_match = sum(keyword_scores) / len(keyword_scores) if keyword_scores else 0
        
        # 成功率统计
        successful_answers = sum(1 for r in results if not r['answer_quality']['contains_error_message'])
        success_rate = successful_answers / len(results)
        
        return {
            'avg_response_time': avg_response_time,
            'max_response_time': max_response_time,
            'min_response_time': min_response_time,
            'avg_confidence': avg_confidence,
            'avg_quality_score': avg_quality_score,
            'avg_keyword_match': avg_keyword_match,
            'success_rate': success_rate,
            'total_throughput': len(results) / total_time,  # 问题/秒
            'questions_with_sources': sum(1 for r in results if r['answer_quality']['has_sources']),
            'avg_source_count': sum(r['answer_quality']['source_count'] for r in results) / len(results)
        }
    
    def save_evaluation_report(self, evaluation_result: Dict[str, Any], filename: str = None):
        """
        保存评估报告
        
        Args:
            evaluation_result: 评估结果
            filename: 保存文件名
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rag_evaluation_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(evaluation_result, f, ensure_ascii=False, indent=2)
        
        print(f"评估报告已保存到: {filename}")
    
    def print_summary(self, evaluation_result: Dict[str, Any]):
        """
        打印评估摘要
        
        Args:
            evaluation_result: 评估结果
        """
        stats = evaluation_result['statistics']
        
        print("\n=== RAG系统评估报告 ===")
        print(f"总问题数: {evaluation_result['total_questions']}")
        print(f"总耗时: {evaluation_result['total_time']:.2f}秒")
        print(f"平均响应时间: {stats['avg_response_time']:.2f}秒")
        print(f"成功率: {stats['success_rate']:.2%}")
        print(f"平均置信度: {stats['avg_confidence']:.2f}")
        print(f"平均质量分数: {stats['avg_quality_score']:.2f}")
        print(f"平均关键词匹配率: {stats['avg_keyword_match']:.2%}")
        print(f"吞吐量: {stats['total_throughput']:.2f} 问题/秒")
        print(f"有来源的问题数: {stats['questions_with_sources']}")
        print(f"平均来源数量: {stats['avg_source_count']:.1f}")


# 示例测试用例
SAMPLE_TEST_CASES = [
    {
        'question': '张克俭的职务是什么？',
        'expected_keywords': ['张克俭', '职务', '董事长', '总经理']
    },
    {
        'question': '公司的主要业务是什么？',
        'expected_keywords': ['业务', '主营', '经营']
    },
    {
        'question': '2019年的营业收入是多少？',
        'expected_keywords': ['2019', '营业收入', '收入', '亿元', '万元']
    }
]


if __name__ == '__main__':
    # 创建评估器
    evaluator = RAGEvaluator()
    
    # 运行批量评估
    print("开始RAG系统评估...")
    results = evaluator.batch_evaluate(SAMPLE_TEST_CASES)
    
    # 打印摘要
    evaluator.print_summary(results)
    
    # 保存报告
    evaluator.save_evaluation_report(results)