from dashvector import Client
from typing import List, Dict, Any
import numpy as np

from rag.embedding import generate_embeddings
from rag.config import RAGConfig


def search_relevant_news(question: str, top_k: int = None, min_score: float = None) -> List[Dict[str, Any]]:
    """
    搜索相关新闻文档
    
    Args:
        question: 用户问题
        top_k: 返回的文档数量（None时使用配置默认值）
        min_score: 最小相似度阈值（None时使用配置默认值）
    
    Returns:
        包含文档内容、来源和置信度的列表
    """
    # 获取配置
    config = RAGConfig.get_retrieval_config()
    if top_k is None:
        top_k = config['default_top_k']
    if min_score is None:
        min_score = config['min_similarity_score']
    # 初始化 dashvector client
    client = Client(
        api_key='sk-2iNDSKIOX2K403qAxIJKcJfTtMp39D207AE75EDCA11EF8A1EBAC0B3B7047F',
        endpoint='vrs-cn-rp64520qc0008j.dashvector.cn-hangzhou.aliyuncs.com'
    )

    # 获取集合
    collection = client.get('news_embeddings')

    # 向量检索：支持多文档检索
    rsp = collection.query(
        generate_embeddings(question), 
        output_fields=['raw'], 
        topk=top_k
    )
    
    # 处理检索结果，添加置信度和来源信息
    results = []
    for i, doc in enumerate(rsp.output):
        # 计算置信度（相似度分数）
        confidence = float(doc.score) if hasattr(doc, 'score') else 0.8
        
        # 过滤低置信度文档
        if confidence >= min_score:
            results.append({
                'content': doc.fields['raw'],
                'source': f'文档ID: {doc.id}',
                'confidence': confidence,
                'rank': i + 1
            })
    
    return results


def rerank_documents(question: str, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    基于问题对文档进行重排序
    
    Args:
        question: 用户问题
        documents: 检索到的文档列表
    
    Returns:
        重排序后的文档列表
    """
    # 获取重排序配置
    config = RAGConfig.get_retrieval_config()
    similarity_weight = config['rerank_weight_similarity']
    keyword_weight = config['rerank_weight_keyword']
    
    # 基于关键词匹配度的重排序策略
    question_words = set(question.lower().split())
    
    for doc in documents:
        content_words = set(doc['content'].lower().split())
        keyword_overlap = len(question_words.intersection(content_words))
        # 结合原始置信度和关键词匹配度
        keyword_score = keyword_overlap / len(question_words) if question_words else 0
        doc['final_score'] = doc['confidence'] * similarity_weight + keyword_score * keyword_weight
    
    # 按最终分数排序
    return sorted(documents, key=lambda x: x['final_score'], reverse=True)