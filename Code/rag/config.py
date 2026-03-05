from typing import Dict, Any
import os


class RAGConfig:
    """
    RAG系统配置类
    """
    
    # 检索配置
    RETRIEVAL_CONFIG = {
        'default_top_k': 3,
        'min_similarity_score': 0.7,
        'max_context_length': 4000,
        'enable_rerank': True,
        'rerank_weight_similarity': 0.7,
        'rerank_weight_keyword': 0.3
    }
    
    # 答案生成配置
    GENERATION_CONFIG = {
        'model_name': 'qwen-turbo',
        'max_tokens': 1000,
        'temperature': 0.1,
        'max_documents_for_answer': 3
    }
    
    # 向量数据库配置
    VECTOR_DB_CONFIG = {
        'collection_name': 'news_embeddings',
        'embedding_dimension': 1536,
        'index_type': 'HNSW'
    }
    
    # 评估配置
    EVALUATION_CONFIG = {
        'min_answer_length': 10,
        'quality_score_weights': {
            'has_answer': 0.2,
            'has_sources': 0.2,
            'high_confidence': 0.2,
            'is_informative': 0.2,
            'no_error': 0.2
        }
    }
    
    # 提示词模板
    PROMPT_TEMPLATES = {
        'qa_prompt': """
你是一个专业的问答助手。请基于以下提供的文档内容回答用户问题。

要求：
1. 仅基于提供的文档内容回答，不要添加文档中没有的信息
2. 如果文档中没有足够信息回答问题，请明确说明
3. 回答要准确、简洁、有条理
4. 如果多个文档有相关信息，请综合考虑

文档内容：
{context}

用户问题：{question}

请提供准确的回答：
        """.strip(),
        
        'no_context_prompt': """
抱歉，没有找到相关信息来回答您的问题：{question}

建议：
1. 请尝试使用不同的关键词重新提问
2. 确认问题是否在知识库覆盖范围内
3. 可以尝试更具体或更简洁的问题表述
        """.strip()
    }
    
    # 日志配置
    LOGGING_CONFIG = {
        'log_level': 'INFO',
        'log_file': 'rag_system.log',
        'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'enable_file_logging': True,
        'enable_console_logging': True
    }
    
    @classmethod
    def get_retrieval_config(cls) -> Dict[str, Any]:
        """获取检索配置"""
        return cls.RETRIEVAL_CONFIG.copy()
    
    @classmethod
    def get_generation_config(cls) -> Dict[str, Any]:
        """获取生成配置"""
        return cls.GENERATION_CONFIG.copy()
    
    @classmethod
    def get_vector_db_config(cls) -> Dict[str, Any]:
        """获取向量数据库配置"""
        return cls.VECTOR_DB_CONFIG.copy()
    
    @classmethod
    def get_evaluation_config(cls) -> Dict[str, Any]:
        """获取评估配置"""
        return cls.EVALUATION_CONFIG.copy()
    
    @classmethod
    def get_prompt_template(cls, template_name: str) -> str:
        """获取提示词模板"""
        return cls.PROMPT_TEMPLATES.get(template_name, "")
    
    @classmethod
    def get_logging_config(cls) -> Dict[str, Any]:
        """获取日志配置"""
        return cls.LOGGING_CONFIG.copy()
    
    @classmethod
    def update_config(cls, config_type: str, updates: Dict[str, Any]):
        """
        更新配置
        
        Args:
            config_type: 配置类型 ('retrieval', 'generation', 'vector_db', 'evaluation')
            updates: 要更新的配置项
        """
        config_map = {
            'retrieval': cls.RETRIEVAL_CONFIG,
            'generation': cls.GENERATION_CONFIG,
            'vector_db': cls.VECTOR_DB_CONFIG,
            'evaluation': cls.EVALUATION_CONFIG,
            'logging': cls.LOGGING_CONFIG
        }
        
        if config_type in config_map:
            config_map[config_type].update(updates)
        else:
            raise ValueError(f"Unknown config type: {config_type}")
    
    @classmethod
    def load_from_env(cls):
        """
        从环境变量加载配置
        """
        # 检索配置
        if os.getenv('RAG_TOP_K'):
            cls.RETRIEVAL_CONFIG['default_top_k'] = int(os.getenv('RAG_TOP_K'))
        
        if os.getenv('RAG_MIN_SCORE'):
            cls.RETRIEVAL_CONFIG['min_similarity_score'] = float(os.getenv('RAG_MIN_SCORE'))
        
        # 生成配置
        if os.getenv('RAG_MODEL_NAME'):
            cls.GENERATION_CONFIG['model_name'] = os.getenv('RAG_MODEL_NAME')
        
        if os.getenv('RAG_MAX_TOKENS'):
            cls.GENERATION_CONFIG['max_tokens'] = int(os.getenv('RAG_MAX_TOKENS'))
        
        if os.getenv('RAG_TEMPERATURE'):
            cls.GENERATION_CONFIG['temperature'] = float(os.getenv('RAG_TEMPERATURE'))
        
        # 向量数据库配置
        if os.getenv('RAG_COLLECTION_NAME'):
            cls.VECTOR_DB_CONFIG['collection_name'] = os.getenv('RAG_COLLECTION_NAME')
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """
        验证配置的有效性
        
        Returns:
            验证结果字典
        """
        issues = []
        
        # 验证检索配置
        if cls.RETRIEVAL_CONFIG['default_top_k'] <= 0:
            issues.append("default_top_k must be positive")
        
        if not 0 <= cls.RETRIEVAL_CONFIG['min_similarity_score'] <= 1:
            issues.append("min_similarity_score must be between 0 and 1")
        
        # 验证生成配置
        if cls.GENERATION_CONFIG['max_tokens'] <= 0:
            issues.append("max_tokens must be positive")
        
        if not 0 <= cls.GENERATION_CONFIG['temperature'] <= 2:
            issues.append("temperature must be between 0 and 2")
        
        # 验证评估配置
        weights = cls.EVALUATION_CONFIG['quality_score_weights']
        if abs(sum(weights.values()) - 1.0) > 0.01:
            issues.append("quality_score_weights must sum to 1.0")
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues
        }
    
    @classmethod
    def print_config(cls):
        """
        打印当前配置
        """
        print("=== RAG系统配置 ===")
        print("\n检索配置:")
        for key, value in cls.RETRIEVAL_CONFIG.items():
            print(f"  {key}: {value}")
        
        print("\n生成配置:")
        for key, value in cls.GENERATION_CONFIG.items():
            print(f"  {key}: {value}")
        
        print("\n向量数据库配置:")
        for key, value in cls.VECTOR_DB_CONFIG.items():
            print(f"  {key}: {value}")
        
        print("\n评估配置:")
        for key, value in cls.EVALUATION_CONFIG.items():
            print(f"  {key}: {value}")


# 预设配置方案
CONFIG_PRESETS = {
    'fast': {
        'retrieval': {
            'default_top_k': 1,
            'min_similarity_score': 0.6,
            'enable_rerank': False
        },
        'generation': {
            'max_tokens': 500,
            'temperature': 0.0
        }
    },
    
    'balanced': {
        'retrieval': {
            'default_top_k': 3,
            'min_similarity_score': 0.7,
            'enable_rerank': True
        },
        'generation': {
            'max_tokens': 1000,
            'temperature': 0.1
        }
    },
    
    'comprehensive': {
        'retrieval': {
            'default_top_k': 5,
            'min_similarity_score': 0.6,
            'enable_rerank': True
        },
        'generation': {
            'max_tokens': 1500,
            'temperature': 0.2
        }
    }
}


def apply_preset(preset_name: str):
    """
    应用预设配置
    
    Args:
        preset_name: 预设名称 ('fast', 'balanced', 'comprehensive')
    """
    if preset_name not in CONFIG_PRESETS:
        raise ValueError(f"Unknown preset: {preset_name}")
    
    preset = CONFIG_PRESETS[preset_name]
    
    for config_type, config_updates in preset.items():
        RAGConfig.update_config(config_type, config_updates)
    
    print(f"已应用预设配置: {preset_name}")


if __name__ == '__main__':
    # 加载环境变量配置
    RAGConfig.load_from_env()
    
    # 验证配置
    validation = RAGConfig.validate_config()
    if not validation['is_valid']:
        print("配置验证失败:")
        for issue in validation['issues']:
            print(f"  - {issue}")
    else:
        print("配置验证通过")
    
    # 打印配置
    RAGConfig.print_config()