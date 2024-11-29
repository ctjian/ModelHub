# models.py

from config.api_keys import *

# 模型配置，包含公司和对应的模型列表
COMPANY_MODEL_MAPPING = {
    'OpenAI': [
        {
            'name': 'GPT-4o-mini',
            'model': 'gpt-4o-mini',
            'api_key': Wlai_APIKEY,
            'host_url': Wlai_BASE_URL
        },
        {
            'name': 'GPT-4',
            'model': 'gpt-4',
            'api_key': Wlai_APIKEY,
            'host_url': Wlai_BASE_URL
        },
        # o1-mini
        {
            'name': 'o1-mini',
            'model': 'o1-mini',
            'api_key': Wlai_APIKEY,
            'host_url': Wlai_BASE_URL
        },
        # o1-preview
        {
            'name': 'o1-preview',
            'model': 'o1-preview',
            'api_key': Wlai_APIKEY,
            'host_url': Wlai_BASE_URL
        },
    ],
    '通义千问': [
        {
            'name': 'Qwen2.5-7B-Instruct',
            'model': 'Qwen/Qwen2.5-7B-Instruct',
            'api_key': Sili_APIKEY,
            'host_url': Sili_BASE_URL
        },
        {
            'name': 'Qwen2.5-14B-Instruct',
            'model': 'Vendor-A/Qwen/Qwen2.5-14B-Instruct',
            'api_key': Sili_APIKEY,
            'host_url': Sili_BASE_URL
        },
        {
            'name': 'Qwen2.5-32B-Instruct',
            'model': 'Vendor-A/Qwen/Qwen2.5-32B-Instruct',
            'api_key': Sili_APIKEY,
            'host_url': Sili_BASE_URL
        },
        {
            'name': 'Qwen2.5-72B-Instruct',
            'model': 'Vendor-A/Qwen/Qwen2.5-72B-Instruct',
            'api_key': Sili_APIKEY,
            'host_url': Sili_BASE_URL
        },
        # marco-o1
        {
            'name': 'Marco-o1',
            'model': 'marco-o1',
            'api_key': 'EMPTY',
            'host_url': 'http://192.168.30.69:8000/v1'
        },
        # Qwen/QwQ-32B-Preview
        {
            'name': 'Qwen/QwQ-32B-Preview',
            'model': 'Qwen/QwQ-32B-Preview',
            'api_key': Sili_APIKEY,
            'host_url': Sili_BASE_URL,
            'system_prompt': 'You are a helpful and harmless assistant. You are Qwen developed by Alibaba. You should think step-by-step.'
        },
    ],
    '零一万物':[
        {
            'name': 'Yi-1.5-9B-Chat-16K',
            'model': '01-ai/Yi-1.5-9B-Chat-16K',
            'api_key': Sili_APIKEY,
            'host_url': Sili_BASE_URL
        },
        {
            'name': 'Yi-1.5-6B-Chat',
            'model': '01-ai/Yi-1.5-6B-Chat',
            'api_key': Sili_APIKEY,
            'host_url': Sili_BASE_URL
        },
        {
            'name': 'Yi-34b-Chat-0205',
            'model': 'yi-34b-chat-0205',
            'api_key': Wlai_APIKEY,
            'host_url': Wlai_BASE_URL
        },
        {
            'name': 'Yi-34b-Chat-200K',
            'model': 'yi-34b-chat-200K',
            'api_key': Wlai_APIKEY,
            'host_url': Wlai_BASE_URL
        },

    ]
}

# 创建模型全名到配置的映射
MODEL_NAME_TO_CONFIG = {}

def get_all_model_names():
    all_models = []
    for company, models in COMPANY_MODEL_MAPPING.items():
        for model in models:
            model_full_name = f"{model['name']}"
            all_models.append(model_full_name)
            MODEL_NAME_TO_CONFIG[model_full_name] = model
    return all_models

# 初始化模型名称列表
ALL_MODEL_NAMES = get_all_model_names()

print(ALL_MODEL_NAMES)

