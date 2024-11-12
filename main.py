# -*- coding: utf-8 -*-

import sys
import customtkinter as ctk
from tkinter import messagebox
from itertools import product
import smtplib
from email.message import EmailMessage
from PIL import Image, ImageTk
import os

# Handle multiprocessing exception when frozen
if getattr(sys, 'frozen', False):
    import multiprocessing
    multiprocessing.freeze_support()

class InputBox:
    def __init__(self, master, title, optional=False):
        self.optional = optional  # Flag for optional fields
        self.title = title
        self.frame = ctk.CTkFrame(master, fg_color="#F0F0F0")
        
        self.label = ctk.CTkLabel(
            self.frame,
            text=title,
            font=('Microsoft YaHei', 14, 'bold'),
            text_color="#FF8C00"
        )
        self.label.pack(fill=ctk.X, pady=(0, 5))
        
        # Use CTkTextbox for multi-line input
        self.text = ctk.CTkTextbox(
            self.frame, height=80, corner_radius=8,
            fg_color="#FFFFFF", text_color="#FF8C00", border_color="#CCCCCC", border_width=2,
            font=('Microsoft YaHei', 12, 'bold')
        )
        self.text.pack(pady=5, fill=ctk.BOTH, expand=True)
        
        # Clear button with icon
        clear_icon = ctk.CTkImage(light_image=Image.open("icons/clear_icon.png"), size=(25, 25))
        self.clear_button = ctk.CTkButton(
            self.frame, text="", command=self.clear_items,
            image=clear_icon, fg_color="#E0E0E0", hover_color="#D0D0D0", text_color="#FF8C00",
            corner_radius=8, width=40, height=40
        )
        self.clear_button.pack(pady=5)
        
    def clear_items(self):
        self.text.delete("1.0", ctk.END)
        
    def has_items(self):
        content = self.text.get("1.0", ctk.END).strip()
        if not content and not self.optional:
            return False
        return True
        
    def get_items(self):
        content = self.text.get("1.0", ctk.END)
        lines = content.strip().split('\n')
        items = [line.strip() for line in lines if line.strip()]
        if not items:
            # Return [''] for optional fields, [] for required fields
            return [''] if self.optional else []
        else:
            return items

def delete_all():
    for box in input_boxes.values():
        box.clear_items()
    email_entry.delete(0, ctk.END)

def generate_combinations():
    if not all(box.has_items() for box in input_boxes.values()):
        messagebox.showwarning("警告", "请确保所有必填对话框都有输入内容！")
        return None
    # Get items from all input boxes
    all_items = [box.get_items() for box in input_boxes.values()]
    combinations = list(product(*all_items))
    return combinations

def show_combinations():
    combinations = generate_combinations()
    if combinations is None:
        return
    result_window = ctk.CTkToplevel(root)
    result_window.title("组合结果")
    result_window.geometry("500x400")
    result_text = ctk.CTkTextbox(
        result_window, width=480, height=380, corner_radius=10,
        fg_color="#FFFFFF", text_color="#FF8C00", border_color="#CCCCCC", border_width=2,
        font=('Microsoft YaHei', 12, 'bold')
    )
    result_text.pack(padx=10, pady=10, fill=ctk.BOTH, expand=True)
    separator = '_' if current_mode == '微信' else '-'
    for combo in combinations:
        # Handle placeholders for Douyin optional fields
        if current_mode == '抖音':
            combo = [item if item else ('$' if box.title == '搭建日期' else '&') for item, box in zip(combo, input_boxes.values())]
        result = separator.join(combo)
        result_text.insert(ctk.END, result + '\n')

def send_email():
    recipient_email = email_entry.get().strip()
    if not recipient_email:
        messagebox.showwarning("警告", "请输入您的邮箱地址！")
        return

    combinations = generate_combinations()
    if combinations is None:
        return

    # Prepare the email content with combinations
    email_content = "组合结果：\n\n"
    separator = '_' if current_mode == '微信' else '-'
    for combo in combinations:
        # Handle placeholders for Douyin optional fields
        if current_mode == '抖音':
            combo = [item if item else ('$' if box.title == '搭建日期' else '&') for item, box in zip(combo, input_boxes.values())]
        result = separator.join(combo)
        email_content += result + '\n'

    try:
        # Create the email message
        msg = EmailMessage()
        msg["Subject"] = "组合结果"
        msg["From"] = 'notapythonbot@163.com'  # Your email
        msg["To"] = recipient_email
        msg.set_content(email_content)

        # Send the email
        server = smtplib.SMTP_SSL('smtp.163.com', 465)  # SMTP server and port
        server.login(msg['From'], "YTNDTSKHEFFDSLFK")  # Your email and password (app-specific password)
        server.sendmail(msg['From'], recipient_email, msg.as_string())
        server.quit()
        messagebox.showinfo("成功", "邮件已发送！")
    except Exception as e:
        messagebox.showerror("错误", f"发送邮件失败：{e}")

def button_click(choice):
    global current_box, selected_button
    # Hide current input box
    if current_box is not None:
        current_box.frame.pack_forget()
    # Show new input box
    current_box = input_boxes[choice]
    current_box.frame.pack(padx=10, pady=10, fill=ctk.BOTH, expand=True)
    # Update button appearances
    for btn in buttons.values():
        btn.configure(fg_color="#E0E0E0", text_color="#FF8C00")
    # Highlight selected button
    selected_button = buttons[choice]
    selected_button.configure(fg_color="#FF8C00", text_color="#FFFFFF")

def update_mode(value):
    global current_mode, input_boxes, buttons, selected_button, current_box
    current_mode = value
    # Clear previous widgets
    for widget in main_frame.winfo_children():
        widget.destroy()
    # Re-initialize variables
    input_boxes = {}
    buttons = {}
    selected_button = None
    current_box = None
    if current_mode == '微信':
        # Sub-selection for '广告' and '创意'
        def wechat_option_selected(choice):
            update_wechat_inputs(choice)

        option_var = ctk.StringVar(value='广告')
        option_frame = ctk.CTkFrame(main_frame, fg_color="#F0F0F0")
        option_frame.pack(pady=10)

        ad_button = ctk.CTkButton(
            option_frame, text="广告", command=lambda: wechat_option_selected('广告'),
            fg_color="#E0E0E0", hover_color="#D0D0D0", text_color="#FF8C00",
            corner_radius=8, width=80, height=40,
            font=('Microsoft YaHei', 12, 'bold')
        )
        ad_button.pack(side=ctk.LEFT, padx=5)

        creative_button = ctk.CTkButton(
            option_frame, text="创意", command=lambda: wechat_option_selected('创意'),
            fg_color="#E0E0E0", hover_color="#D0D0D0", text_color="#FF8C00",
            corner_radius=8, width=80, height=40,
            font=('Microsoft YaHei', 12, 'bold')
        )
        creative_button.pack(side=ctk.LEFT, padx=5)

        def update_wechat_inputs(choice):
            global input_boxes, buttons, selected_button, current_box
            # Clear previous widgets
            for widget in main_frame.winfo_children():
                if widget != option_frame:
                    widget.destroy()
            input_boxes = {}
            buttons = {}
            selected_button = None
            current_box = None
            if choice == '广告':
                input_configs = [
                    {"title": "BN", "optional": False},
                    {"title": "项目名称", "optional": False},
                    {"title": "点位", "optional": False},
                    {"title": "人群", "optional": False},
                    {"title": "出价方式", "optional": False},
                    {"title": "日期", "optional": False},
                    {"title": "备注", "optional": False},
                ]
            else:
                input_configs = [
                    {"title": "BN", "optional": False},
                    {"title": "项目名称", "optional": False},
                    {"title": "点位", "optional": False},
                    {"title": "素材", "optional": False},
                    {"title": "人群", "optional": False},
                    {"title": "出价方式", "optional": False},
                    {"title": "日期", "optional": False},
                    {"title": "备注", "optional": False},
                ]
            create_input_boxes(input_configs)
        # Initialize with '广告' inputs
        update_wechat_inputs('广告')
    else:
        input_configs = [
            {"title": "上线日期", "optional": False},
            {"title": "目的", "optional": False},
            {"title": "人群", "optional": False},
            {"title": "素材", "optional": False},
            {"title": "设备", "optional": True},
            {"title": "定向城市", "optional": True},
            {"title": "搭建日期", "optional": True},
        ]
        create_input_boxes(input_configs)

def create_input_boxes(input_configs):
    global input_boxes, buttons, selected_button, current_box
    # Create input boxes and store them in a dictionary
    for config in input_configs:
        box = InputBox(main_frame, config["title"], config["optional"])
        input_boxes[config["title"]] = box

    # Selection buttons to select input box
    options = [config["title"] for config in input_configs]
    selected_button = None  # Keep track of selected button

    button_frame = ctk.CTkFrame(main_frame, fg_color="#F0F0F0")
    button_frame.pack(pady=10)

    for option in options:
        btn = ctk.CTkButton(
            button_frame, text=option, command=lambda opt=option: button_click(opt),
            fg_color="#E0E0E0", hover_color="#D0D0D0", text_color="#FF8C00",
            corner_radius=20, width=80, height=40,
            font=('Microsoft YaHei', 12, 'bold')
        )
        btn.pack(side=ctk.LEFT, padx=5)
        buttons[option] = btn

    # Initially display the first input box
    current_box = input_boxes[options[0]]
    current_box.frame.pack(padx=10, pady=10, fill=ctk.BOTH, expand=True)
    # Highlight the first button
    selected_button = buttons[options[0]]
    selected_button.configure(fg_color="#FF8C00", text_color="#FFFFFF")

# Set appearance and theme
ctk.set_appearance_mode("light")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

root = ctk.CTk()
root.title("tools")
root.geometry("1000x600")  # Adjusted size

# Initialize variables
input_boxes = {}
current_box = None
current_mode = '抖音'  # Default mode

# Create a frame for the mode switch
mode_frame = ctk.CTkFrame(root, fg_color="#F0F0F0")
mode_frame.pack(pady=30)

mode_var = ctk.StringVar(value='抖音')
mode_switch = ctk.CTkSegmentedButton(
    mode_frame,
    values=['抖音', '微信'],
    command=update_mode,
    variable=mode_var,
    fg_color="#E0E0E0",
    selected_color="#FF8C00",
    unselected_color="#E0E0E0",
    text_color="#FF8C00",
    font=('Microsoft YaHei', 16, 'bold')
)
mode_switch.pack()

# Create a frame for the main content
main_frame = ctk.CTkFrame(root, fg_color="#F0F0F0")
main_frame.pack(pady=20, fill=ctk.BOTH, expand=True)

# Initialize with default mode inputs
update_mode(mode_var.get())

# Control frame for buttons and email entry (fixed position at the bottom)
control_frame = ctk.CTkFrame(root, fg_color="#F0F0F0")
control_frame.pack(side=ctk.BOTTOM, pady=10, fill=ctk.X)

# Load icons
delete_icon = ctk.CTkImage(light_image=Image.open("icons/delete_icon.png"), size=(20, 20))
show_icon = ctk.CTkImage(light_image=Image.open("icons/show_icon.png"), size=(20, 20))
send_icon = ctk.CTkImage(light_image=Image.open("icons/send_icon.png"), size=(20, 20))

delete_all_button = ctk.CTkButton(
    control_frame, text="", command=delete_all, image=delete_icon,
    fg_color="#E0E0E0", hover_color="#D0D0D0", text_color="#FF8C00",
    corner_radius=8, width=40, height=40
)
delete_all_button.pack(side=ctk.LEFT, padx=5)

generate_button = ctk.CTkButton(
    control_frame, text="", command=show_combinations, image=show_icon,
    fg_color="#E0E0E0", hover_color="#D0D0D0", text_color="#FF8C00",
    corner_radius=8, width=40, height=40
)
generate_button.pack(side=ctk.LEFT, padx=5)

# Email entry field
email_label = ctk.CTkLabel(control_frame, text="邮箱：", text_color="#FF8C00", font=('Microsoft YaHei', 12, 'bold'))
email_label.pack(side=ctk.LEFT, padx=5)

email_entry = ctk.CTkEntry(
    control_frame, width=200, corner_radius=8,
    fg_color="#FFFFFF", text_color="#FF8C00", border_color="#CCCCCC", border_width=2,
    font=('Microsoft YaHei', 12, 'bold')
)
email_entry.pack(side=ctk.LEFT, padx=5)

send_button = ctk.CTkButton(
    control_frame, text="", command=send_email, image=send_icon,
    fg_color="#E0E0E0", hover_color="#D0D0D0", text_color="#FF8C00",
    corner_radius=8, width=40, height=40
)
send_button.pack(side=ctk.LEFT, padx=5)

# Add version information
version_label = ctk.CTkLabel(root, text="v0.1.3", font=('Microsoft YaHei', 10, 'bold'), text_color="#FF8C00")
version_label.pack(side=ctk.BOTTOM, pady=5)

root.mainloop()
