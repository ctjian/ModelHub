import gradio as gr
from api_model import APIModel
import threading
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
    ],
    'Alibaba': [
        {
            'name': 'Qwen2.5-7B-Instruct',
            'model': 'Qwen/Qwen2.5-7B-Instruct',
            'api_key': Sili_APIKEY,
            'host_url': Sili_BASE_URL
        },
        {
            'name': 'Qwen2.5-72B-Instruct',
            'model': 'Vendor-A/Qwen/Qwen2.5-72B-Instruct',
            'api_key': Sili_APIKEY,
            'host_url': Sili_BASE_URL
        },
    ],
}

# 创建模型全名到配置的映射
MODEL_NAME_TO_CONFIG = {}

def get_all_model_names():
    all_models = []
    for company, models in COMPANY_MODEL_MAPPING.items():
        for model in models:
            model_full_name = f"{company} - {model['name']}"
            all_models.append(model_full_name)
            MODEL_NAME_TO_CONFIG[model_full_name] = model
    return all_models

# 初始化模型名称列表
ALL_MODEL_NAMES = get_all_model_names()

# 全局变量
chat_history = []  # 确保 chat_history 是一个列表
llm_clients = []
stop_event = threading.Event()

def select_model(*selected_models):
    """
    接收来自各个公司选择框的选定模型，初始化相应的 APIModel 客户端。
    """
    global llm_clients, chat_history
    # 重置对话历史
    chat_history = []
    llm_clients = []

    # 收集所有选定的模型
    selected_models = [model for sublist in selected_models for model in sublist]

    if not selected_models:
        status_message = "请至少选择一个模型。"
        return gr.update(value=[]), status_message

    for model_name in selected_models:
        model_config = MODEL_NAME_TO_CONFIG.get(model_name)
        if model_config:
            llm_client = APIModel(
                api_key=model_config['api_key'],
                host_url=model_config['host_url'],
                model=model_config['model']
            )
            llm_clients.append({'name': model_name, 'client': llm_client})
        else:
            status_message = f"模型 {model_name} 不存在"
            return gr.update(value=[]), status_message

    status_message = f"已选择模型：{', '.join(selected_models)}"
    return gr.update(value=[]), status_message

def submit_message(user_input):
    global chat_history, llm_clients, stop_event
    stop_event.clear()
    if not llm_clients:
        # 在模型未选择的情况下，提示用户选择模型
        chat_history.append({'role': 'assistant', 'content': '请先选择模型。'})
        yield chat_history
        return

    chat_history.append({'role': 'user', 'content': user_input})

    # 为每个模型添加占位符消息
    for client_info in llm_clients:
        model_name = client_info['name']
        chat_history.append({'role': 'assistant', 'content': f'{model_name}: 正在生成回复...'})

    yield chat_history

    # 获取每个模型的回复
    for idx, client_info in enumerate(llm_clients):
        model_name = client_info['name']
        llm_client = client_info['client']
        response = ''
        for chunk in llm_client.request_stream(user_input, multi_turns=True):
            if stop_event.is_set():
                break
            if chunk:
                response += chunk
                # 更新助手的消息内容
                chat_history_idx = 1 + idx  # 用户消息后的第 idx 条助手消息
                chat_history[chat_history_idx]['content'] = f'{model_name}: {response}'
                yield chat_history
        # 确保在生成结束后，助手的回复完整
        chat_history[chat_history_idx]['content'] = f'{model_name}: {response}'
        yield chat_history

def stop_generation():
    stop_event.set()
    return "生成已停止。"

def reset_chat():
    global chat_history, llm_clients
    chat_history = []
    for client_info in llm_clients:
        client_info['client'].reset_conversation()
    return gr.update(value=[]), "对话已重置。"

# 创建 Gradio 界面
with gr.Blocks() as demo:
    gr.Markdown("# 多模型对话界面")

    with gr.Column():
        with gr.Accordion("选择模型", open=True):
            # 为每个公司创建一个 CheckboxGroup
            company_selectors = {}
            for company in COMPANY_MODEL_MAPPING:
                with gr.Group():
                    gr.Markdown(f"### {company}")
                    checkbox = gr.CheckboxGroup(
                        choices=[f"{company} - {model['name']}" for model in COMPANY_MODEL_MAPPING[company]],
                        label=f"选择 {company} 的模型"
                    )
                    company_selectors[company] = checkbox
            select_button = gr.Button("选择模型")

    status_output = gr.Textbox(label="状态", interactive=False)

    # 指定 type='messages'，并确保数据格式正确
    chatbot = gr.Chatbot(label="对话", height=400, type='messages')

    user_input = gr.Textbox(label="请输入您的问题：")

    with gr.Row():
        submit_btn = gr.Button("提交")
        stop_btn = gr.Button("停止")
        reset_btn = gr.Button("重置")

    # 点击选择模型按钮时，初始化模型，并清空聊天记录
    select_button.click(
        fn=select_model,
        inputs=[company_selectors[company] for company in COMPANY_MODEL_MAPPING],
        outputs=[chatbot, status_output]
    )

    # 提交用户输入
    submit_btn.click(
        fn=submit_message,
        inputs=user_input,
        outputs=chatbot
    )

    # 重置对话
    reset_btn.click(
        fn=reset_chat,
        outputs=[chatbot, status_output]
    )

    # 停止生成
    stop_btn.click(
        fn=stop_generation,
        outputs=status_output
    )

demo.launch()
