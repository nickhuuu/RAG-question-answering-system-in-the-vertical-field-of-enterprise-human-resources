#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG知识问答系统演示脚本

展示改进后的RAG系统功能，包括：
1. 多文档检索和重排序
2. 答案溯源机制
3. 置信度评估
4. 性能监控
5. 配置管理
"""

import json
import time
from typing import List, Dict, Any

from rag.run import hr_qa, hr_qa_simple
from rag.evaluation import RAGEvaluator
from rag.config import RAGConfig, apply_preset


def print_separator(title: str = ""):
    """打印分隔线"""
    print("\n" + "=" * 60)
    if title:
        print(f" {title} ")
        print("=" * 60)


def print_qa_result(result: Dict[str, Any], show_details: bool = True):
    """格式化打印问答结果"""
    print(f"\n问题: {result['question']}")
    print(f"\n答案: {result['answer']}")
    
    if show_details:
        print(f"\n置信度: {result.get('confidence', 0):.2f}")
        print(f"文档数量: {result.get('document_count', 0)}")
        print(f"处理时间: {result.get('processing_time', 0):.2f}秒")
        
        # 显示来源信息
        sources = result.get('sources', [])
        if sources:
            print("\n来源信息:")
            for i, source in enumerate(sources, 1):
                print(f"  {i}. {source['source']} (置信度: {source['confidence']:.2f})")
        
        # 显示性能指标
        metrics = result.get('performance_metrics', {})
        if metrics:
            print("\n性能指标:")
            print(f"  检索时间: {metrics.get('retrieval_time', 0):.2f}秒")
            print(f"  生成时间: {metrics.get('generation_time', 0):.2f}秒")
            if metrics.get('rerank_time', 0) > 0:
                print(f"  重排序时间: {metrics.get('rerank_time', 0):.2f}秒")


def demo_basic_qa():
    """演示基本问答功能"""
    print_separator("基本问答功能演示")
    
    questions = [
        "张克俭的职务是什么？",
        "公司的主要业务是什么？",
        "2019年的营业收入是多少？"
    ]
    
    for question in questions:
        print(f"\n正在处理问题: {question}")
        result = hr_qa(question)
        print_qa_result(result, show_details=False)


def demo_advanced_features():
    """演示高级功能"""
    print_separator("高级功能演示")
    
    question = "张克俭的职务是什么？"
    
    print("\n1. 标准模式（启用重排序）:")
    result1 = hr_qa(question, top_k=3, enable_rerank=True)
    print_qa_result(result1)
    
    print("\n2. 快速模式（禁用重排序）:")
    result2 = hr_qa(question, top_k=1, enable_rerank=False)
    print_qa_result(result2)
    
    print("\n3. 详细模式（更多文档）:")
    result3 = hr_qa(question, top_k=5, enable_rerank=True)
    print_qa_result(result3)


def demo_config_presets():
    """演示配置预设功能"""
    print_separator("配置预设演示")
    
    question = "公司的主要业务是什么？"
    presets = ['fast', 'balanced', 'comprehensive']
    
    for preset in presets:
        print(f"\n应用 {preset} 预设配置:")
        apply_preset(preset)
        
        start_time = time.time()
        result = hr_qa(question)
        end_time = time.time()
        
        print(f"配置: {preset}")
        print(f"答案: {result['answer'][:100]}...")
        print(f"文档数量: {result.get('document_count', 0)}")
        print(f"置信度: {result.get('confidence', 0):.2f}")
        print(f"处理时间: {end_time - start_time:.2f}秒")


def demo_evaluation():
    """演示评估功能"""
    print_separator("系统评估演示")
    
    # 创建测试用例
    test_cases = [
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
            'expected_keywords': ['2019', '营业收入', '收入']
        }
    ]
    
    # 创建评估器
    evaluator = RAGEvaluator()
    
    print("开始批量评估...")
    results = evaluator.batch_evaluate(test_cases)
    
    # 打印评估摘要
    evaluator.print_summary(results)
    
    # 显示详细结果
    print("\n详细评估结果:")
    for i, result in enumerate(results['individual_results'], 1):
        print(f"\n问题 {i}: {result['question']}")
        print(f"  质量分数: {result['answer_quality']['quality_score']:.2f}")
        print(f"  关键词匹配: {result.get('keyword_match_score', 0):.2%}")
        print(f"  响应时间: {result['response_time']:.2f}秒")
        print(f"  置信度: {result['confidence']:.2f}")


def demo_error_handling():
    """演示错误处理"""
    print_separator("错误处理演示")
    
    # 测试空问题
    print("\n1. 空问题测试:")
    result1 = hr_qa("")
    print(f"答案: {result1['answer']}")
    
    # 测试无关问题
    print("\n2. 无关问题测试:")
    result2 = hr_qa("今天天气怎么样？")
    print(f"答案: {result2['answer']}")
    print(f"置信度: {result2.get('confidence', 0):.2f}")
    print(f"文档数量: {result2.get('document_count', 0)}")


def demo_performance_comparison():
    """演示性能对比"""
    print_separator("性能对比演示")
    
    question = "张克俭的职务是什么？"
    
    # 简单版本
    print("\n1. 简单版本 (hr_qa_simple):")
    start_time = time.time()
    simple_result = hr_qa_simple(question)
    simple_time = time.time() - start_time
    print(f"答案: {simple_result['answer'][:100]}...")
    print(f"处理时间: {simple_time:.2f}秒")
    
    # 完整版本
    print("\n2. 完整版本 (hr_qa):")
    start_time = time.time()
    full_result = hr_qa(question)
    full_time = time.time() - start_time
    print(f"答案: {full_result['answer'][:100]}...")
    print(f"处理时间: {full_time:.2f}秒")
    print(f"置信度: {full_result.get('confidence', 0):.2f}")
    print(f"来源数量: {len(full_result.get('sources', []))}")
    
    print(f"\n性能提升: {((simple_time - full_time) / simple_time * 100):.1f}%")


def interactive_demo():
    """交互式演示"""
    print_separator("交互式问答演示")
    
    print("\n欢迎使用RAG知识问答系统！")
    print("输入 'quit' 或 'exit' 退出")
    print("输入 'config' 查看当前配置")
    print("输入 'preset <name>' 应用预设配置 (fast/balanced/comprehensive)")
    
    while True:
        try:
            question = input("\n请输入您的问题: ").strip()
            
            if question.lower() in ['quit', 'exit', '退出']:
                print("感谢使用！")
                break
            
            if question.lower() == 'config':
                RAGConfig.print_config()
                continue
            
            if question.lower().startswith('preset '):
                preset_name = question.split(' ', 1)[1]
                try:
                    apply_preset(preset_name)
                    print(f"已应用 {preset_name} 预设配置")
                except ValueError as e:
                    print(f"错误: {e}")
                continue
            
            if not question:
                print("请输入有效问题")
                continue
            
            # 处理问题
            result = hr_qa(question)
            print_qa_result(result)
            
        except KeyboardInterrupt:
            print("\n\n感谢使用！")
            break
        except Exception as e:
            print(f"发生错误: {e}")


def main():
    """主函数"""
    print("RAG知识问答系统演示")
    print("=" * 60)
    
    # 显示当前配置
    print("\n当前系统配置:")
    RAGConfig.print_config()
    
    demos = {
        '1': ('基本问答功能', demo_basic_qa),
        '2': ('高级功能演示', demo_advanced_features),
        '3': ('配置预设演示', demo_config_presets),
        '4': ('系统评估演示', demo_evaluation),
        '5': ('错误处理演示', demo_error_handling),
        '6': ('性能对比演示', demo_performance_comparison),
        '7': ('交互式问答', interactive_demo),
        '0': ('运行所有演示', None)
    }
    
    print("\n请选择演示内容:")
    for key, (name, _) in demos.items():
        print(f"  {key}. {name}")
    
    choice = input("\n请输入选择 (1-7, 0为全部): ").strip()
    
    if choice == '0':
        # 运行所有演示（除了交互式）
        for key in ['1', '2', '3', '4', '5', '6']:
            if key in demos and demos[key][1]:
                demos[key][1]()
                time.sleep(1)  # 短暂暂停
    elif choice in demos and demos[choice][1]:
        demos[choice][1]()
    else:
        print("无效选择")


if __name__ == '__main__':
    main()