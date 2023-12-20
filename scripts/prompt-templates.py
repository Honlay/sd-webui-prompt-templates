import contextlib
import os
import json
import gradio as gr
import modules.scripts as scripts
from googletrans import Translator
import random

# 获取当前脚本的路径信息
current_script = os.path.realpath(__file__)
current_folder = os.path.dirname(current_script)
work_basedir = os.path.dirname(current_folder)  # 本插件的根目录
data_path = work_basedir + r"/data/styles/"
random_path = work_basedir + r"/data/random/random.json"
# 初始化全局变量
prompt_is_chinese = False
negative_prompt_chinese = False
original_prompt = ""
original_negative_prompt = ""


def send_text_to_prompt(old_text):
    return original_prompt.replace("{prompt}", old_text)


def send_text_to_negative_prompt():
    return original_negative_prompt


# 获取指定目录下的所有 JSON 文件的文件名
def get_json_filenames(directory):
    return [f.rstrip('.json') for f in os.listdir(directory) if f.endswith('.json')]


# 获取 JSON 文件名列表
json_filenames = get_json_filenames(data_path)


def load_template_data(path):
    """从 JSON 文件加载模板数据"""
    json_file_path = f'{data_path}/{path}.json'
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    return []


def load_random_data():
    """从json文件加载随机数据"""
    if os.path.exists(random_path):
        with open(random_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    return []


def prompt_translate_chinese(text):
    """翻译正向提示词"""
    global prompt_is_chinese
    prompt_is_chinese = not prompt_is_chinese
    if prompt_is_chinese:
        translator = Translator()
        result = translator.translate(text, src='en', dest='zh-cn')
        return result.text.strip()
    else:
        return original_prompt


def negative_prompt_translate_chinese(text):
    """翻译反向提示词"""
    global negative_prompt_chinese
    negative_prompt_chinese = not negative_prompt_chinese
    if negative_prompt_chinese:
        translator = Translator()
        result = translator.translate(text, src='en', dest='zh-cn')
        return result.text.strip()
    else:
        return original_negative_prompt


def clear_prompt():
    return ""


class TemplateScript(scripts.Script):
    """自定义脚本类，用于提供 Gradio 界面功能"""

    def title(self):
        """返回插件标题"""
        return "Prompt Template"

    def __init__(self):
        """初始化函数，加载模板数据"""
        self.txtprompt = None
        self.neg_prompt_boxIMG = None
        self.neg_prompt_boxTXT = None
        self.boxxIMG = None
        self.boxx = None
        self.template_data = load_template_data(json_filenames[0])
        self.random_data = load_random_data()

    def show(self, is_img2img):
        """确定是否显示此扩展插件"""
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        if is_img2img:
            eid = 'lei-img-prompt'
        else:
            eid = 'lei-txt-prompt'
        """构建 UI 组件"""
        with gr.Row(elem_id=eid):
            with gr.Accordion('提示词模板 V1.1.0', open=False):
                gr.HTML('<a href="https://github.com/Honlay/sd-webui-prompt-templates">[使用说明]')
                with gr.Row():
                    with gr.Column(scale=3, elem_classes="block gradio-accordion svelte-90oupt padded"):
                        radio = gr.Radio(json_filenames, label="选择模板类型", value=json_filenames[0])

                        with gr.Row():
                            dropdown_to_text = gr.Dropdown(
                                [item["name"] for item in self.template_data],
                                label="选择模板"
                            )
                            random_button = gr.Button(value="🎲️",
                                                      elem_classes="lg secondary gradio-button tool svelte-cmf5ev",
                                                      elem_id="txt2img_random_seed")
                        with gr.Row():
                            prompt_sent = gr.Textbox(label="正向提示词")
                            prompt_tr_button = gr.Button(value="🌐", size="sm",
                                                         elem_classes="lg secondary gradio-button tool svelte-cmf5ev")
                            prompt_clear_button = gr.Button(value="🗑️", size="sm",
                                                            elem_classes="lg secondary gradio-button tool svelte-cmf5ev")
                        with gr.Row():
                            negative_prompt_send = gr.Textbox(label="反向提示词")
                            negative_prompt_tr_button = gr.Button(value="🌐", size="sm",
                                                                  elem_classes="lg secondary gradio-button tool "
                                                                               "svelte-cmf5ev")
                            negative_prompt_clear_button = gr.Button(value="🗑️", size="sm",
                                                                     elem_classes="lg secondary gradio-button tool "
                                                                                  "svelte-cmf5ev")

                        send_text_button = gr.Button(value='发送到提示词框', variant='primary')
                        dropdown_to_text.change(fn=self.update_prompt, inputs=[dropdown_to_text], outputs=[prompt_sent])
                        dropdown_to_text.change(fn=self.update_negative_prompt, inputs=[dropdown_to_text],
                                                outputs=[negative_prompt_send])

                        prompt_tr_button.click(fn=prompt_translate_chinese, inputs=[prompt_sent],
                                               outputs=[prompt_sent])
                        negative_prompt_tr_button.click(fn=negative_prompt_translate_chinese,
                                                        inputs=[negative_prompt_send], outputs=[negative_prompt_send])
                        radio.change(fn=self.load_and_update_dropdown, inputs=[radio], outputs=[dropdown_to_text])

                        random_button.click(fn=self.select_random_prompt, outputs=[prompt_sent])

                        prompt_clear_button.click(fn=clear_prompt, outputs=[prompt_sent])
                        negative_prompt_clear_button.click(fn=clear_prompt, outputs=[negative_prompt_send])
                    with gr.Column(scale=2,elem_classes="block gradio-accordion svelte-90oupt padded"):
                        gr.Markdown("""
                                        ### 提示词写作技巧
                                        #### 符号解析
                                        - ()小括号: 加权 每套一层括号增加1.1倍，red=1 (red)=1.1 (((red)))=1.331
                                        - {}大括号: 加权 每套一层括号增加1.05倍，red=1 {red}=1.05 {{{red}}}=1.15
                                        - []中括号: 降权 每套一层括号增加0.9倍，red=1 [red]=0.9 [[[red]]]=0.729
                                        - _下划线：起到连接的作用，如要生成咖啡蛋糕，则写为:coffee_cake
                                        - 通常使用小括号和数字直接设置权重(red:1.5),范围建议设置在0.3-1.5之间
                                        #### 进阶语法
                                        - [提示词:0-1数值]表示整体画面采样达到数值之后才计算其采样
                                        - [提示词::0-1数值]表示整体画面采样达到数值之后不再计算其采样
                                        - [提示词1:提示词2:0-1数值]表示整体画面达到数值之后提示词1不再采样,提示词2开始采样
                                        - [提示词1|提示词2]交替采样
                                        #### 推荐格式:画质、画风词+画面主体描述+环境、场景、灯光、构图+Lora
                                        """,
                                    )
        # 处理文本框和按钮交互
        with contextlib.suppress(AttributeError):
            if is_img2img:
                send_text_button.click(fn=send_text_to_prompt, inputs=[self.boxxIMG], outputs=[self.boxxIMG])
                send_text_button.click(fn=send_text_to_negative_prompt, outputs=[self.neg_prompt_boxIMG])
            else:
                send_text_button.click(fn=send_text_to_prompt, inputs=[self.boxx], outputs=[self.boxx])
                send_text_button.click(fn=send_text_to_negative_prompt, outputs=[self.neg_prompt_boxTXT])

        return [prompt_sent, dropdown_to_text, send_text_button]

    def after_component(self, component, **kwargs):
        """处理组件事件后的回调函数"""
        if component.elem_id == "txt2img_prompt" or component.elem_id == "img2img_prompt":
            self.txtprompt = component

        if kwargs.get("elem_id") == "txt2img_prompt":
            self.boxx = component
        if kwargs.get("elem_id") == "img2img_prompt":
            self.boxxIMG = component
        if kwargs.get("elem_id") == "txt2img_neg_prompt":
            self.neg_prompt_boxTXT = component
        if kwargs.get("elem_id") == "img2img_neg_prompt":
            self.neg_prompt_boxIMG = component

    def select_random_prompt(self):
        if self.random_data:
            random_entry = random.choice(self.random_data)
            global original_prompt
            original_prompt = random_entry["prompt"]
            return random_entry['translation']
        return ""

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

    def update_negative_prompt(self, selected_name):
        """根据下拉菜单的选择更新文本框"""
        for item in self.template_data:
            if item["name"] == selected_name:
                global original_negative_prompt
                original_negative_prompt = item["negative_prompt"]
                return item["negative_prompt"]
        return ""

    def load_and_update_dropdown(self, selected_json):
        """根据选定的 JSON 文件名加载数据并更新下拉菜单选项"""
        self.template_data = load_template_data(selected_json)
        new_options = [item["name"] for item in self.template_data]
        return gr.Dropdown.update(choices=new_options)
