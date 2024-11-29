# handlers.py

import gradio as gr
from api_model import APIModel
import threading
from models import MODEL_NAME_TO_CONFIG, ALL_MODEL_NAMES

# 全局变量
chat_history = []  # 存储对话历史
llm_clients = []    # 存储多个 APIModel 实例
status_message = ""  # 存储状态消息
stop_event = threading.Event()

def select_model(*selected_models):
    """
    处理模型选择：初始化所选模型的 APIModel 客户端。
    """
    global llm_clients, chat_history, status_message
    # 重置对话历史和客户端列表
    chat_history = []
    llm_clients = []

    # 展平所有选定的模型
    selected_models = [model for sublist in selected_models for model in sublist]

    if not selected_models:
        status_message = "请至少选择一个模型。"
        return gr.update(value=[]), status_message
    
    print(selected_models)
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

    # 添加用户消息
    chat_history.append({'role': 'user', 'content': user_input})

    # 记录当前 chat_history 的长度，以确定助手占位符的位置
    current_length = len(chat_history)

    # 为每个模型添加占位符消息
    for client_info in llm_clients:
        model_name = client_info['name']
        # 使用 HTML 标签加粗并变成蓝色
        styled_model_name = f"<span style='color:blue; font-weight:bold'>{model_name}:</span>"
        chat_history.append({'role': 'assistant', 'content': f'{styled_model_name} 正在生成回复...'})
    
    # 初始占位符输出
    yield chat_history

    # 获取每个模型的回复
    for idx, client_info in enumerate(llm_clients):
        model_name = client_info['name']
        llm_client = client_info['client']
        response = ''
        for chunk in llm_client.request_stream(user_input, multi_turns=False, stop_event=stop_event):
            if stop_event.is_set():
                break
            if chunk:
                response += chunk
                # 计算助手消息的位置
                chat_history_idx = current_length + idx  # 用户消息后的第 idx 条助手消息
                # 使用 HTML 标签加粗并变成蓝色
                styled_model_name = f"<span style='color:blue; font-weight:bold'>{model_name}:</span>"
                chat_history[chat_history_idx]['content'] = f'{styled_model_name} {response}'
                yield chat_history
        # 确保在生成结束后，助手的回复完整
        chat_history[chat_history_idx]['content'] = f'{styled_model_name} {response}'
        yield chat_history

def stop_generation():
    """
    处理停止生成：设置停止事件以中断生成。
    """
    stop_event.set()
    return "生成已停止。"

# def reset_chat():
#     """
#     处理重置对话：清空对话历史并重置所有模型的会话。
#     """
#     global chat_history, llm_clients
#     chat_history = []
#     for client_info in llm_clients:
#         client_info['client'].reset_conversation()
#     return gr.update(value=[]), "对话已重置。"

def reset_chat():
    global chat_history, llm_clients, status_message
    chat_history = []
    # llm_clients = []
    return gr.update(value=[]), status_message