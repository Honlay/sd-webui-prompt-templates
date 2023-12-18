import contextlib
import os
import json
import gradio as gr
import modules.scripts as scripts
from modules.processing import process_images
from googletrans import Translator

# 获取当前脚本的路径信息
current_script = os.path.realpath(__file__)
current_folder = os.path.dirname(current_script)
work_basedir = os.path.dirname(current_folder)  # 本插件的根目录
temp_path = work_basedir + r"/json"  # JSON 文件的路径
# 初始化全局变量
prompt_is_chinese = False
negative_prompt_chinese = False
original_prompt = ""
original_negative_prompt = ""


def send_text_to_prompt(old_text):
    # return new_text.format(old_text)
    return original_prompt.replace("{prompt}", old_text)


def send_text_to_negative_prompt(new_text):
    return original_negative_prompt


class TemplateScript(scripts.Script):
    """自定义脚本类，用于提供 Gradio 界面功能"""
    def title(self):
        """返回插件标题"""
        return "Prompt Template"

    def __init__(self):
        """初始化函数，加载模板数据"""
        self.neg_prompt_boxIMG = None
        self.neg_prompt_boxTXT = None
        self.boxxIMG = None
        self.boxx = None
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

    def update_prompt(self, selected_name):
        """根据下拉菜单的选择更新文本框"""
        global prompt_is_chinese
        prompt_is_chinese = False
        global negative_prompt_chinese
        negative_prompt_chinese = False
        for item in self.template_data:
            if item["name"] == selected_name:
                global original_prompt
                original_prompt = item["prompt"]
                return item["prompt"]
        return ""

    def prompt_translate_chinese(self, text):
        """翻译正向提示词"""
        global prompt_is_chinese
        prompt_is_chinese = not prompt_is_chinese
        if prompt_is_chinese:
            translator = Translator()
            result = translator.translate(text, src='en', dest='zh-cn')
            return result.text.strip()
        else:
            return original_prompt

    def update_negative_prompt(self, selected_name):
        """根据下拉菜单的选择更新文本框"""
        for item in self.template_data:
            if item["name"] == selected_name:
                global original_negative_prompt
                original_negative_prompt = item["negative_prompt"]
                return item["negative_prompt"]
        return ""

    def negative_prompt_translate_chinese(self, text):
        """翻译反向提示词"""
        global negative_prompt_chinese
        negative_prompt_chinese = not negative_prompt_chinese
        if negative_prompt_chinese:
            translator = Translator()
            result = translator.translate(text, src='en', dest='zh-cn')
            return result.text.strip()
        else:
            return original_negative_prompt

    def show(self, is_img2img):
        """确定是否显示此扩展插件"""
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        """构建 UI 组件"""
        with gr.Accordion('提示词模板', open=False):
            with gr.Column():
                dropdown_to_text = gr.Dropdown(
                    [item["name"] for item in self.template_data],
                    label="选择模板",
                    value=self.template_data[0]["name"] if self.template_data else "无选项"
                )
                with gr.Row():
                    prompt_sent = gr.Textbox(label="正向提示词")
                    prompt_tr_button = gr.Button(value="译", size="sm",
                                                 elem_classes="lg secondary gradio-button tool svelte-cmf5ev")
                with gr.Row():
                    negative_prompt_send = gr.Textbox(label="反向提示词")
                    negative_prompt_tr_button = gr.Button(value="译", size="sm",
                                                          elem_classes="lg secondary gradio-button tool svelte-cmf5ev")

                send_text_button = gr.Button(value='发送到提示词框', variant='primary')
                dropdown_to_text.change(fn=self.update_prompt, inputs=[dropdown_to_text], outputs=[prompt_sent])
                dropdown_to_text.change(fn=self.update_negative_prompt, inputs=[dropdown_to_text],
                                        outputs=[negative_prompt_send])

                prompt_tr_button.click(fn=self.prompt_translate_chinese, inputs=[prompt_sent], outputs=[prompt_sent])
                negative_prompt_tr_button.click(fn=self.negative_prompt_translate_chinese, inputs=[negative_prompt_send], outputs=[negative_prompt_send])

        # 处理文本框和按钮交互
        with contextlib.suppress(AttributeError):
            if is_img2img:
                send_text_button.click(fn=send_text_to_prompt, inputs=[self.boxxIMG],
                                       outputs=[self.boxxIMG])
                send_text_button.click(fn=send_text_to_negative_prompt,
                                       inputs=[negative_prompt_send],
                                       outputs=[self.neg_prompt_boxIMG])
            else:
                send_text_button.click(fn=send_text_to_prompt, inputs=[self.boxx], outputs=[self.boxx])
                send_text_button.click(fn=send_text_to_negative_prompt,
                                       inputs=[negative_prompt_send],
                                       outputs=[self.neg_prompt_boxTXT])

        return [prompt_sent, dropdown_to_text, send_text_button]

    def after_component(self, component, **kwargs):
        """处理组件事件后的回调函数"""
        if kwargs.get("elem_id") == "txt2img_prompt":
            self.boxx = component
        if kwargs.get("elem_id") == "img2img_prompt":
            self.boxxIMG = component
        if kwargs.get("elem_id") == "txt2img_neg_prompt":
            self.neg_prompt_boxTXT = component
        if kwargs.get("elem_id") == "img2img_neg_prompt":
            self.neg_prompt_boxIMG = component
