import streamlit as st
from itertools import product
import smtplib
from email.message import EmailMessage

# 应用自定义 CSS
def local_css():
    st.markdown("""
        <style>
        /* 全局字体和背景 */
        @import url('https://fonts.googleapis.com/css2?family=Microsoft+YaHei&display=swap');
        html, body, [class*="css"]  {
            font-family: 'Microsoft YaHei', sans-serif;
            background-color: #f0f2f6;
        }
        /* 标题样式 */
        h1 {
            color: #FF8C00;
            font-weight: bold;
        }
        /* 输入框标签样式 */
        label {
            font-weight: bold;
            font-size: 16px;
            color: #333333;
        }
        /* 按钮样式 */
        .stButton > button {
            background-color: #FF8C00;
            color: #ffffff;
            border-radius: 8px;
            font-size: 16px;
            height: 50px;
            width: 100%;
        }
        .stButton > button:hover {
            background-color: #e07c00;
        }
        /* 侧边栏样式 */
        .css-1d391kg {
            background-color: #ffffff;
        }
        </style>
        """, unsafe_allow_html=True)

def main():
    local_css()
    st.title("数据输入工具")

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
        input_fields = ["上线日期", "目的", "人群", "素材", "设备（无用&占位）", "定向城市（无&占位）", "搭建日期（无用$占位）"]
        separator = "-"

    st.write("---")  # 分割线

    st.header("请输入以下信息：")

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
                inputs[field] = st.text_area(field, height=100)

        # 邮箱输入
        email = st.text_input("请输入您的邮箱地址（可选）")
        st.write(" ")

        # 提交按钮
        submitted = st.form_submit_button("生成组合")

    if submitted:
        combinations = generate_combinations(inputs, mode, separator)
        if combinations:
            st.success("生成成功！")
            # 使用 expander 展示组合结果
            with st.expander("点击展开组合结果"):
                for combo in combinations:
                    st.write(combo)
            # 发送邮件
            if email:
                send_email(email, combinations)
        else:
            st.error("请确保所有必填字段都已填写！")
        
def generate_combinations(inputs, mode, separator):
    # 将输入的每一项按行分割
    items_list = []
    for key, value in inputs.items():
        lines = value.strip().split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        if not lines:
            if mode == "抖音" and ("设备" in key or "定向城市" in key):
                lines = ["&"]
            elif mode == "抖音" and "搭建日期" in key:
                lines = ["$"]
            else:
                st.warning(f"请填写 {key} 字段！")
                return []
        items_list.append(lines)
    
    # 生成组合
    combinations = list(product(*items_list))
    result = [separator.join(combo) for combo in combinations]
    return result

def send_email(recipient_email, combinations):
    # 组合结果作为邮件内容
    email_content = "组合结果：\n\n" + "\n".join(combinations)
    try:
        # 创建邮件消息
        msg = EmailMessage()
        msg["Subject"] = "组合结果"
        msg["From"] = 'your_email@example.com'  # 替换为您的邮箱
        msg["To"] = recipient_email
        msg.set_content(email_content)

        # 发送邮件
        server = smtplib.SMTP_SSL('smtp.example.com', 465)  # 替换为您的SMTP服务器和端口
        server.login(msg['From'], "your_email_password")  # 替换为您的邮箱和密码
        server.sendmail(msg['From'], recipient_email, msg.as_string())
        server.quit()
        st.info("邮件已发送！")
    except Exception as e:
        st.error(f"发送邮件失败：{e}")

if __name__ == "__main__":
    main()
