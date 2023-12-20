// 定义一个变量来存储UI元素的引用。
let uiElements;

// 此函数负责加载并返回主要的UI组件。
function loadUIComponents() {
    return {
        prompt: getElement('#lei-txt-prompt'),  // 获取第一个提示输入框的元素。
        prompt2: getElement('#lei-img-prompt'), // 获取第二个提示输入框的元素。
        txt2img: getElement("#txt2img_prompt_container"), // 获取文本到图像提示容器的元素。
        img2img: getElement("#img2img_prompt_container"), // 获取图像到图像提示容器的元素。
    }
}

// 辅助函数，用于从gradio应用中获取指定的DOM元素。
function getElement(key) {
    // 使用querySelector选择器获取指定的DOM元素。
    return gradioApp().querySelector(key)
}

// 当UI加载完成后触发的事件。
onUiLoaded(() => {
    initData(); // 初始化数据。
});

// 初始化数据，配置UI元素。
function initData() {
    // 调用loadUIComponents函数，加载UI组件。
    uiElements = loadUIComponents();

    // 将prompt元素附加到文本到图像的容器中。
    uiElements.txt2img.appendChild(uiElements.prompt);

    // 将prompt2元素附加到图像到图像的容器中。
    uiElements.img2img.appendChild(uiElements.prompt2);
}
