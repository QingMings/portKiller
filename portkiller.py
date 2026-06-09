import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import re


class PortKillerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("端口查找结束工具")
        self.root.geometry("800x500")
        self.root.minsize(700, 400)

        # 输入区域
        input_frame = ttk.Frame(root, padding="10")
        input_frame.pack(fill="x")

        # 左侧：端口号输入
        left_frame = ttk.Frame(input_frame)
        left_frame.pack(side="left")

        ttk.Label(left_frame, text="端口号:").pack(side="left")
        self.port_entry = ttk.Entry(left_frame, width=15)
        self.port_entry.pack(side="left", padx=5)
        self.port_entry.bind("<Return>", lambda e: self.search_port())

        self.search_btn = ttk.Button(left_frame, text="查找", command=self.search_port, width=8)
        self.search_btn.pack(side="left")

        # 提示文字
        ttk.Label(input_frame, text="输入端口号后按回车或点击查找", foreground="#888").pack(side="left", padx=20)

        # 右侧：关于按钮
        ttk.Button(input_frame, text="关于", command=self.show_about, width=6).pack(side="right")

        # 结果表格区域
        result_frame = ttk.Frame(root, padding="10")
        result_frame.pack(fill="both", expand=True)

        columns = ("protocol", "address", "state", "pid", "proc_name")
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings")

        self.tree.heading("protocol", text="协议")
        self.tree.heading("address", text="地址")
        self.tree.heading("state", text="状态")
        self.tree.heading("pid", text="PID")
        self.tree.heading("proc_name", text="进程")

        self.tree.column("protocol", width=80, anchor="center")
        self.tree.column("address", width=200, anchor="w")
        self.tree.column("state", width=100, anchor="center")
        self.tree.column("pid", width=80, anchor="center")
        self.tree.column("proc_name", width=200, anchor="w")

        # 交替行背景
        self.tree.tag_configure("odd", background="#f5f5f5")
        self.tree.tag_configure("even", background="#ffffff")

        tree_scroll = ttk.Scrollbar(result_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

        # 右键菜单
        self.popup = tk.Menu(root, tearoff=0)
        self.popup.add_command(label="结束选中进程", command=self.kill_selected)
        self.popup.add_command(label="刷新", command=self.search_port)
        self.tree.bind("<Button-3>", self.show_popup)
        self.tree.bind("<Double-1>", lambda e: self.kill_selected())

        # 按钮栏
        btn_frame = ttk.Frame(root, padding="5")
        btn_frame.pack(fill="x")

        ttk.Button(btn_frame, text="结束选中进程", command=self.kill_selected).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="刷新", command=self.search_port).pack(side="left", padx=5)

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(root, textvariable=self.status_var, padding="5", relief="sunken", anchor="w")
        status_bar.pack(fill="x")

    def show_about(self):
        about_text = (
            "端口查找结束工具\n"
            "====================\n\n"
            "使用说明：\n"
            " 1. 在顶部输入框中输入端口号（如 8080）\n"
            " 2. 按回车键或点击「查找」按钮\n"
            " 3. 下方表格显示占用该端口的进程\n"
            " 4. 选中一行或多行后：\n"
            "    - 点击「结束选中进程」可关闭进程\n"
            "    - 双击行可快速结束该进程\n"
            "    - 右键行可弹出菜单操作\n"
            " 5. 点击「刷新」可重新查询\n\n"
            "注意：\n"
            "  - 仅显示 LISTENING 或 ESTABLISHED 状态的进程\n"
            "  - 已自动按 PID 去重，过滤掉 PID 0\n"
            "  - 结束系统进程需管理员权限"
        )
        messagebox.showinfo("关于", about_text)

    def show_popup(self, event):
        try:
            self.popup.tk_popup(event.x_root, event.y_root)
        finally:
            self.popup.grab_release()

    def clear_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def search_port(self):
        port = self.port_entry.get().strip()

        if not port:
            messagebox.showwarning("提示", "请输入端口号")
            return

        if not re.match(r"^\d+$", port):
            messagebox.showerror("错误", "端口号必须是数字")
            return

        self.clear_tree()
        self.status_var.set(f"正在查找端口 {port}...")
        self.root.update_idletasks()

        try:
            result = subprocess.run(
                'netstat -ano',
                shell=True,
                capture_output=True,
                text=True,
                encoding='gbk',
                errors='replace'
            )

            lines = result.stdout.strip().split("\n")
            seen_pids = {}
            row_index = 0

            for line in lines:
                if not line.strip():
                    continue

                parts = line.split()
                if len(parts) < 5:
                    continue

                local_addr = parts[1]
                state = parts[-2] if len(parts) > 4 else ""
                pid = parts[-1]

                # 精确端口匹配
                if not (local_addr.endswith(f":{port}") or re.search(rf":{port}(\s|$)", local_addr)):
                    continue

                # 状态过滤
                if state and state not in ("LISTENING", "ESTABLISHED"):
                    continue

                # 过滤 PID 0
                if not pid.isdigit() or int(pid) == 0:
                    continue

                # 去重
                if pid in seen_pids:
                    continue
                seen_pids[pid] = True

                protocol = parts[0]

                proc_result = subprocess.run(
                    f'tasklist /FI "PID eq {pid}" /FO CSV /NH',
                    shell=True,
                    capture_output=True,
                    text=True,
                    encoding='gbk',
                    errors='replace'
                )

                proc_name = "未知"
                proc_lines = proc_result.stdout.strip().split("\n")
                for pline in proc_lines:
                    if pid in pline:
                        proc_name = pline.split(",")[0].strip('"') if "," in pline else proc_name
                        break

                tag = "odd" if row_index % 2 else "even"
                self.tree.insert("", "end", values=(protocol, local_addr, state, pid, proc_name), tags=(tag,))
                row_index += 1

            if not seen_pids:
                self.status_var.set(f"未找到占用端口 {port} 的进程")
                messagebox.showinfo("结果", f"未找到占用端口 {port} 的进程")
            else:
                self.status_var.set(f"找到 {len(seen_pids)} 个占用端口 {port} 的进程")

        except Exception as e:
            self.status_var.set("查询失败")
            messagebox.showerror("错误", str(e))

    def kill_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先在表格中选择一行")
            return

        items = [self.tree.item(s)["values"] for s in selected]
        pids = [(str(item[3]), str(item[4])) for item in items if item and len(item) > 3]

        if not pids:
            return

        msg = "\n".join([f"PID {pid} ({name})" for pid, name in pids])
        if messagebox.askyesno("确认", f"确定要结束以下进程吗？\n\n{msg}"):
            for pid, name in pids:
                try:
                    subprocess.run(f"taskkill /F /PID {pid}", shell=True)
                except Exception as e:
                    messagebox.showerror("错误", f"结束 PID {pid} 失败: {e}")
            self.search_port()

    def kill_all(self):
        items = [self.tree.item(s)["values"] for s in self.tree.get_children()]
        if not items:
            messagebox.showinfo("提示", "当前没有可结束的进程")
            return

        pids = [(str(item[3]), str(item[4])) for item in items if item and len(item) > 3]
        if not pids:
            return

        msg = "\n".join([f"PID {pid} ({name})" for pid, name in pids])
        if messagebox.askyesno("确认", f"确定要结束以下所有进程吗？\n\n{msg}"):
            for pid, name in pids:
                try:
                    subprocess.run(f"taskkill /F /PID {pid}", shell=True)
                except Exception as e:
                    messagebox.showerror("错误", f"结束 PID {pid} 失败: {e}")
            self.search_port()


def _set_app_icon(root):
    """设置应用图标：优先使用 app.ico"""
    import os
    import sys
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # 兼容 PyInstaller 打包后的临时目录
    if getattr(sys, "frozen", False):
        base_dir = sys._MEIPASS
    ico_path = os.path.join(base_dir, "app.ico")
    if os.path.exists(ico_path):
        try:
            root.iconbitmap(default=ico_path)
        except Exception:
            pass


if __name__ == "__main__":
    root = tk.Tk()
    _set_app_icon(root)
    app = PortKillerApp(root)
    root.mainloop()
