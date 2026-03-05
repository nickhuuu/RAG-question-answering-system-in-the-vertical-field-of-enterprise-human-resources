import dashscope
import logging
import time
from typing import Dict, Any

from rag.search import search_relevant_news, rerank_documents
from rag.answer import answer_question
from rag.config import RAGConfig
from util.api_keys import dashscope_apikey

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def hr_qa(question: str, top_k: int = None, enable_rerank: bool = None) -> Dict[str, Any]:
    """
    人力资源问答系统主函数
    
    Args:
        question: 用户问题
        top_k: 检索文档数量（None时使用配置默认值）
        enable_rerank: 是否启用重排序（None时使用配置默认值）
    
    Returns:
        包含问题、答案、来源和置信度的字典
    """
    start_time = time.time()
    logger.info(f"开始处理问题: {question[:100]}...")
    
    # 获取配置
    retrieval_config = RAGConfig.get_retrieval_config()
    if top_k is None:
        top_k = retrieval_config['default_top_k']
    if enable_rerank is None:
        enable_rerank = retrieval_config['enable_rerank']
    dashscope.api_key = dashscope_apikey
    
    try:
        # 1. 检索相关文档
        retrieval_start = time.time()
        documents = search_relevant_news(question, top_k=top_k)
        retrieval_time = time.time() - retrieval_start
        
        logger.info(f"检索到 {len(documents)} 个相关文档，耗时 {retrieval_time:.2f}秒")
        
        if not documents:
            logger.warning(f"未找到相关文档: {question}")
            return {
                "question": question,
                "answer": "抱歉，没有找到相关信息来回答您的问题。",
                "sources": [],
                "confidence": 0.0,
                "document_count": 0,
                "processing_time": time.time() - start_time
            }
        
        # 2. 可选的文档重排序
        if enable_rerank and len(documents) > 1:
            rerank_start = time.time()
            documents = rerank_documents(question, documents)
            rerank_time = time.time() - rerank_start
            logger.info(f"文档重排序完成，耗时 {rerank_time:.2f}秒")
        
        # 3. 生成答案
        generation_start = time.time()
        result = answer_question(question, documents)
        generation_time = time.time() - generation_start
        
        logger.info(f"答案生成完成，耗时 {generation_time:.2f}秒")
        
        # 4. 构建完整响应
        total_time = time.time() - start_time
        response = {
            "question": question,
            "answer": result['answer'],
            "sources": result['sources'],
            "confidence": result['confidence'],
            "document_count": result.get('document_count', len(documents)),
            "processing_time": total_time,
            "performance_metrics": {
                "retrieval_time": retrieval_time,
                "generation_time": generation_time,
                "rerank_time": rerank_time if enable_rerank and len(documents) > 1 else 0,
                "total_time": total_time
            },
            "retrieval_info": {
                "total_retrieved": len(documents),
                "rerank_enabled": enable_rerank,
                "top_k": top_k
            }
        }
        
        logger.info(f"问题处理完成，总耗时 {total_time:.2f}秒，置信度 {result['confidence']:.2f}")
        return response
        
    except Exception as e:
        error_time = time.time() - start_time
        logger.error(f"处理问题时出现错误: {str(e)}, 耗时 {error_time:.2f}秒")
        return {
            "question": question,
            "answer": f"系统处理问题时出现错误：{str(e)}",
            "sources": [],
            "confidence": 0.0,
            "document_count": 0,
            "processing_time": error_time,
            "error": str(e)
        }


def hr_qa_simple(question: str) -> Dict[str, str]:
    """
    简化版问答函数，保持向后兼容性
    
    Args:
        question: 用户问题
    
    Returns:
        包含问题和答案的字典
    """
    result = hr_qa(question)
    return {
        "question": result["question"],
        "answer": result["answer"]
    }

if __name__ == '__main__':
    question = input('Enter question: ')
    answer = hr_qa(question)
    print(answer)



