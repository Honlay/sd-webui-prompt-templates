import contextlib

import gradio as gr
import modules.scripts as scripts
from modules.processing import process_images

def send_text_to_prompt(new_text, old_text):
    if old_text == "":  # if text on the textbox text2img or img2img is empty, return new text
        return new_text
    return old_text + " " + new_text  # else join them together and send it to the textbox
class ExtensionTemplateScript(scripts.Script):
    # Extension title in menu UI
    def title(self):
        return "Prompt Template"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    # Setup menu ui detail
    def ui(self, is_img2img):
        with gr.Accordion('提示词模板', open=False):
            with gr.Column():
                with gr.Row():
                    text_to_be_sent = gr.Textbox(label="模板描述")
                    dropdown_to_be_text = gr.Dropdown(
                        ["base", "cat", "dog", "bird"], label="选择模板", value="base"
                    )
                send_text_button = gr.Button(value='发送到提示词框', variant='primary')

        with contextlib.suppress(AttributeError):  # Ignore the error if the attribute is not present
            if is_img2img:
                send_text_button.click(fn=send_text_to_prompt, inputs=[text_to_be_sent, self.boxxIMG],
                                       outputs=[self.boxxIMG])
            else:
                send_text_button.click(fn=send_text_to_prompt, inputs=[text_to_be_sent, self.boxx], outputs=[self.boxx])

        return [text_to_be_sent, dropdown_to_be_text, send_text_button]

    def after_component(self, component, **kwargs):

        if kwargs.get("elem_id") == "txt2img_prompt":
            self.boxx = component
        if kwargs.get("elem_id") == "img2img_prompt":
            self.boxxIMG = component


