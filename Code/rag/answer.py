from dashscope import Generation
from typing import List, Dict, Any

from rag.config import RAGConfig


def answer_question(question: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    基于检索到的文档回答问题
    
    Args:
        question: 用户问题
        documents: 检索到的文档列表
    
    Returns:
        包含答案、来源和置信度的字典
    """
    # 获取配置
    gen_config = RAGConfig.get_generation_config()
    
    if not documents:
        no_context_prompt = RAGConfig.get_prompt_template('no_context_prompt')
        return {
            'answer': no_context_prompt.format(question=question),
            'sources': [],
            'confidence': 0.0
        }
    
    # 构建多文档上下文
    max_docs = gen_config['max_documents_for_answer']
    context_parts = []
    sources = []
    
    for i, doc in enumerate(documents[:max_docs]):
        context_parts.append(f"文档{i+1}（来源：{doc['source']}，置信度：{doc['confidence']:.2f}）：\n{doc['content']}")
        sources.append({
            'source': doc['source'],
            'confidence': doc['confidence'],
            'rank': doc['rank']
        })
    
    context = "\n\n".join(context_parts)
    
    # 使用配置中的提示词模板
    prompt_template = RAGConfig.get_prompt_template('qa_prompt')
    prompt = prompt_template.format(context=context, question=question)

    try:
        # 使用配置中的生成参数
        rsp = Generation.call(
            model=gen_config['model_name'],
            prompt=prompt,
            max_tokens=gen_config['max_tokens'],
            temperature=gen_config['temperature']
        )
        answer = rsp.output.text
        
        # 计算整体置信度（基于文档置信度的加权平均）
        total_confidence = sum(doc['confidence'] for doc in documents) / len(documents)
        
        return {
            'answer': answer,
            'sources': sources,
            'confidence': total_confidence,
            'document_count': len(documents)
        }
    
    except Exception as e:
        return {
            'answer': f'生成答案时出现错误：{str(e)}',
            'sources': sources,
            'confidence': 0.0
        }


def answer_question_simple(question: str, context: str) -> str:
    """
    简单版本的问答函数，保持向后兼容性
    
    Args:
        question: 用户问题
        context: 上下文内容
    
    Returns:
        答案文本
    """
    prompt = f'''请基于```内的内容回答问题。
	```
	{context}
	```
	我的问题是：{question}。
    '''

    rsp = Generation.call(model='qwen-turbo', prompt=prompt)
    return rsp.output.text