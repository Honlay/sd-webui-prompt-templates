import contextlib
import os
import json
import gradio as gr
import modules.scripts as scripts
from modules.processing import process_images

# 获取当前脚本的路径信息
current_script = os.path.realpath(__file__)
current_folder = os.path.dirname(current_script)
work_basedir = os.path.dirname(current_folder)  # 本插件的根目录
temp_path = work_basedir + r"/json"  # JSON 文件的路径


def send_text_to_prompt(new_text, old_text):
    return new_text.format(old_text)
    # """将新文本添加到旧文本中，用于更新文本框内容"""
    # if old_text == "":
    #     return new_text
    # return old_text + " " + new_text


class TemplateScript(scripts.Script):
    """自定义脚本类，用于提供 Gradio 界面功能"""

    def title(self):
        """返回插件标题"""
        return "Prompt Template"

    def __init__(self):
        """初始化函数，加载模板数据"""
        self.template_data = self.load_template_data()

    def load_template_data(self):
        """从 JSON 文件加载模板数据"""
        json_file_path = f'{temp_path}/Template.json'
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                print("Loaded data:", data)  # 打印加载的数据
                return data
        return []

    def update_textbox(self, selected_name):
        """根据下拉菜单的选择更新文本框"""
        for item in self.template_data:
            if item["name"] == selected_name:
                return item["prompt"]
        return ""

    def show(self, is_img2img):
        """确定是否显示此扩展插件"""
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        """构建 UI 组件"""
        with gr.Accordion('提示词模板', open=False):
            with gr.Column():
                with gr.Row():
                    text_to_be_sent = gr.Textbox(label="模板描述")
                    dropdown_to_text = gr.Dropdown(
                        [item["name"] for item in self.template_data],
                        label="选择模板",
                        value=self.template_data[0]["name"] if self.template_data else "无选项"
                    )
                send_text_button = gr.Button(value='发送到提示词框', variant='primary')
                dropdown_to_text.change(fn=self.update_textbox, inputs=[dropdown_to_text], outputs=[text_to_be_sent])

        # 处理文本框和按钮交互
        with contextlib.suppress(AttributeError):
            if is_img2img:
                send_text_button.click(fn=send_text_to_prompt, inputs=[text_to_be_sent, self.boxxIMG],
                                       outputs=[self.boxxIMG])
            else:
                send_text_button.click(fn=send_text_to_prompt, inputs=[text_to_be_sent, self.boxx], outputs=[self.boxx])

        return [text_to_be_sent, dropdown_to_text, send_text_button]

    def after_component(self, component, **kwargs):
        """处理组件事件后的回调函数"""
        if kwargs.get("elem_id") == "txt2img_prompt":
            self.boxx = component
        if kwargs.get("elem_id") == "img2img_prompt":
            self.boxxIMG = component
