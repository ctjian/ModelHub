# main.py

import time
import gradio as gr
from handlers import select_model, submit_message, stop_generation, reset_chat
from models import COMPANY_MODEL_MAPPING

def create_model_selectors():
    """
    为每个公司创建一个 CheckboxGroup 模型选择器，并添加自定义CSS类。
    """
    selectors = []
    for company in COMPANY_MODEL_MAPPING:
        selectors.append(
            gr.CheckboxGroup(
                choices=[f"{company} - {model['name']}" for model in COMPANY_MODEL_MAPPING[company]],
                label=f"选择 {company} 的模型",
                elem_classes=["gr-checkboxgroup"],  # 添加自定义类
            )
        )
    return selectors


# 创建 Gradio 界面
with gr.Blocks() as demo:

    gr.Markdown("# 多模型对话界面")

    with gr.Column(elem_classes=["model-selector-container"]):
        with gr.Accordion("选择模型", open=True):
            # 动态创建每个公司的模型选择器
            company_selectors = create_model_selectors()
            select_button = gr.Button("选择模型")

    status_output = gr.Textbox(label="状态", interactive=False)

    # 定义 LaTeX 分隔符
    latex_delimiters = [
        {"left": "\\(", "right": "\\)", "display": False},  # 行内公式
        {"left": "\\[", "right": "\\]", "display": True},   # 行间公式
        {"left": "$$", "right": "$$", "display": True}      # 另一种行间公式
    ]

    # 创建 Chatbot 组件，指定 type='messages' 以符合数据格式要求

    chatbot = gr.Chatbot(label="对话", height=400, type='messages', latex_delimiters=latex_delimiters, elem_classes=["custom-chatbot"])

    user_input = gr.Textbox(label="请输入您的问题：")

    with gr.Row():
        submit_btn = gr.Button("提交")
        stop_btn = gr.Button("停止")
        reset_btn = gr.Button("重置")

    # 连接按钮到处理函数
    select_button.click(
        fn=select_model,
        inputs=company_selectors,
        outputs=[chatbot, status_output]
    )

    submit_btn.click(
        fn=submit_message,
        inputs=user_input,
        outputs=chatbot
    )

    reset_btn.click(
        fn=reset_chat,
        outputs=[chatbot, status_output]
    )

    stop_btn.click(
        fn=stop_generation,
        outputs=status_output
    )

demo.launch()