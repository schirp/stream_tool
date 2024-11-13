import streamlit as st
from itertools import product

def local_css():
    st.markdown("""
        <style>
        /* 导入字体 */
        @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@500&display=swap');
        /* 全局字体和背景 */
        html, body, [class*="css"]  {
            font-family: 'Noto Serif SC', serif;
            background-color: #f5f5f5;
        }
        /* 标题样式 */
        .title {
            text-align: center;
            color: #FF8C00;  /* 标题颜色为橙色 */
            font-weight: bold;
            font-size: 36px;
            margin-bottom: 10px;
        }
        /* 输入框标签样式 */
        label {
            font-weight: 600;
            font-size: 18px;
            color: #A9A9A9;  /* 修改为深灰色 */
        }
        /* 按钮样式 */
        .stButton > button {
            background-color: #556B2F;
            color: #ffffff;
            border-radius: 10px;
            font-size: 18px;
            height: 50px;
            width: 100%;
            border: none;
            transition: background-color 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #6B8E23;
        }
        /* 侧边栏样式 */
        .sidebar .sidebar-content {
            background-image: linear-gradient(#A9A9A9,#708090);
            color: white;
        }
        .sidebar .sidebar-content h2 {
            color: white;
            font-size: 24px;
        }
        .sidebar .sidebar-content .option {
            font-size: 18px;
            font-weight: 500;
        }
        /* 调整标题位置 */
        .css-18e3th9 {
            padding-top: 0;
        }
        /* 表单布局 */
        .stForm {
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
        }
        /* 调整提示信息样式 */
        .stSuccess, .stError, .stWarning {
            font-size: 16px;
        }
        </style>
        """, unsafe_allow_html=True)


def main():
    local_css()

    # 创建标题容器并将标题放置在左上角
    title_container = st.container()
    with title_container:
        st.markdown('<div class="title"><h1>数据输入工具</h1></div>', unsafe_allow_html=True)

    # 模式选择
    st.sidebar.header("选择模式")
    mode = st.sidebar.selectbox("", ["抖音", "微信"])
    
    if mode == "微信":
        wechat_type = st.sidebar.radio("选择微信类型", ["广告", "创意"])
        if wechat_type == "广告":
            input_fields = ["BN", "项目名称", "点位", "人群", "出价方式", "日期", "备注"]
        else:
            input_fields = ["BN", "项目名称", "点位", "素材", "人群", "出价方式", "日期", "备注"]
        separator = "_"
    else:
        input_fields = ["上线日期", "目的", "人群", "素材", "设备（无用$占位）", "定向城市（无用$占位）", "搭建日期（无用$占位）"]
        separator = "-"

    st.subheader("请输入以下信息")
    st.info("""
                每一栏通过回车键分割, e.g \n
               ##### 素材
                ```
               素材A 
               素材B 
               素材C
               ```
               """, icon="ℹ️")

    # 使用表单组织输入组件
    with st.form("input_form"):
        inputs = {}
        # 根据字段数量确定列数
        num_fields = len(input_fields)
        num_cols = 2 if num_fields > 6 else 1
        cols = st.columns(num_cols)
        for idx, field in enumerate(input_fields):
            col = cols[idx % num_cols]
            with col:
                inputs[field] = st.text_area(field, height=80)
        
        st.write(" ")

        # 提交按钮
        submitted = st.form_submit_button("生成组合")

    if submitted:
        combinations = generate_combinations(inputs, mode, separator)
        if combinations:
            st.success("生成成功！", icon="🔥")

            # 使用 expander 展示组合结果
            with st.expander("点击展开组合结果"):
                for combo in combinations:
                    st.write(combo)
        else:
            st.error("请确保所有必填字段都已填写！")

def generate_combinations(inputs, mode, separator):
    # 将输入的每一项按行分割
    items_list = []
    for key, value in inputs.items():
        lines = value.strip().split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        
        if not lines:
            if mode == "抖音":
                # 对于“抖音”模式的可选字段，设置占位符
                if "设备" in key or "定向城市" in key:
                    lines = ["$"]
                elif "搭建日期" in key:
                    lines = ["$"]
                else:
                    st.warning(f"请填写 {key} 字段！")
                    return []
            else:
                st.warning(f"请填写 {key} 字段！")
                return []
        items_list.append(lines)
    
    # 生成组合
    combinations = list(product(*items_list))
    result = [separator.join(combo) for combo in combinations]
    result = [separator.join(combo).replace('$', '\$') for combo in combinations]
    return result


if __name__ == "__main__":
    main()
