import os
import socket
import threading
import http.server
import socketserver
import qrcode
import html
import io
import secrets
import urllib.parse
from urllib.parse import quote, unquote
import customtkinter as ctk
from tkinter import filedialog, messagebox

PORT = 8000
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class LocalDropPro:
    def __init__(self, root):
        self.root = root
        self.root.title("LocalDrop Pro - Command Center")
        self.root.state('zoomed') 
        
        self.target_path = None
        self.is_file = False
        self.server_thread = None
        self.httpd = None
        self.is_running = False
        self.connected_ips = set() 
        self.current_token = None

        self.setup_ui()

    def get_dynamic_ips(self):
        hostname = socket.gethostname()
        _, _, ips = socket.gethostbyname_ex(hostname)
        return [ip for ip in ips if ip != "127.0.0.1"]

    def setup_ui(self):
        self.main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        self.left_panel = ctk.CTkFrame(self.main_container, width=450)
        self.left_panel.pack(side="left", fill="y", padx=(0, 10))
        self.left_panel.pack_propagate(False) 

        self.right_panel = ctk.CTkFrame(self.main_container)
        self.right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.lbl_title = ctk.CTkLabel(self.left_panel, text="LocalDrop Hub", font=ctk.CTkFont(size=32, weight="bold"))
        self.lbl_title.pack(pady=(20, 5))

        self.ip_combo = ctk.CTkComboBox(self.left_panel, values=self.get_dynamic_ips(), width=300)
        self.ip_combo.pack(pady=10)

        self.button_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.button_frame.pack(pady=10)

        self.btn_file = ctk.CTkButton(self.button_frame, text="📄 Select File", width=140, command=self.select_file)
        self.btn_file.pack(side="left", padx=5)

        self.btn_folder = ctk.CTkButton(self.button_frame, text="📁 Select Folder", width=140, fg_color="#8e44ad", hover_color="#9b59b6", command=self.select_folder)
        self.btn_folder.pack(side="left", padx=5)

        self.lbl_target = ctk.CTkLabel(self.left_panel, text="No target selected", text_color="gray", wraplength=400)
        self.lbl_target.pack(pady=(0, 15))

        self.btn_toggle = ctk.CTkButton(self.left_panel, text="🚀 Start Server", fg_color="#2ecc71", hover_color="#27ae60", font=ctk.CTkFont(weight="bold", size=16), height=40, width=300, command=self.toggle_server)
        self.btn_toggle.pack(pady=10)

        self.qr_frame = ctk.CTkFrame(self.left_panel, width=220, height=220, fg_color="transparent")
        self.qr_frame.pack(pady=15)
        self.lbl_qr = ctk.CTkLabel(self.qr_frame, text="[ QR Code ]", text_color="gray", font=ctk.CTkFont(size=14))
        self.lbl_qr.pack()

        self.url_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.url_frame.pack(pady=5)

        self.entry_url = ctk.CTkEntry(self.url_frame, width=230, justify="center", font=ctk.CTkFont(weight="bold"), state="disabled")
        self.entry_url.pack(side="left", padx=(0, 5))

        self.btn_copy = ctk.CTkButton(self.url_frame, text="📋 Copy", width=60, command=self.copy_url)
        self.btn_copy.pack(side="left")

        ctk.CTkLabel(self.left_panel, text="📱 Connected Devices", font=ctk.CTkFont(weight="bold", size=16)).pack(pady=(20, 5))
        self.device_box = ctk.CTkTextbox(self.left_panel, width=380, height=150, font=ctk.CTkFont(family="Consolas", size=13))
        self.device_box.pack(pady=5, fill="both", expand=True, padx=20)
        self.device_box.configure(state="disabled")

        self.top_right_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.top_right_frame.pack(fill="x", padx=20, pady=10)
        
        self.switch_theme = ctk.CTkSwitch(self.top_right_frame, text="Dark Mode", command=self.toggle_theme)
        self.switch_theme.select()
        self.switch_theme.pack(side="right")

        ctk.CTkLabel(self.right_panel, text="⚡ Live Network Activity Log", font=ctk.CTkFont(weight="bold", size=20)).pack(anchor="w", padx=20, pady=(0, 10))

        self.log_box = ctk.CTkTextbox(self.right_panel, font=ctk.CTkFont(family="Consolas", size=14))
        self.log_box.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.log_box.configure(state="disabled")

    def toggle_theme(self):
        if self.switch_theme.get() == 1: ctk.set_appearance_mode("dark")
        else: ctk.set_appearance_mode("light")

    def copy_url(self):
        url = self.entry_url.get()
        if url:
            self.root.clipboard_clear()
            self.root.clipboard_append(url)
            self.btn_copy.configure(text="✅ Copied!", fg_color="#2ecc71")
            self.root.after(2000, lambda: self.btn_copy.configure(text="📋 Copy", fg_color=["#3a7ebf", "#1f538d"]))

    def extract_device_model(self, user_agent):
        ua = user_agent.lower()
        if "android" in ua: return "Android Device"
        if "iphone" in ua: return "Apple iPhone"
        if "ipad" in ua: return "Apple iPad"
        if "macintosh" in ua or "mac os" in ua: return "Apple MacBook"
        if "windows" in ua: return "Windows PC"
        if "linux" in ua: return "Linux Machine"
        return "Unknown Device"

    def register_device(self, ip, user_agent):
        device_name = self.extract_device_model(user_agent)
        device_id = f"{device_name} ({ip})"

        if device_id not in self.connected_ips:
            self.connected_ips.add(device_id)
            self.device_box.configure(state="normal")
            self.device_box.insert("end", f"✓ {device_name}\n  IP: {ip}\n\n")
            self.device_box.see("end")
            self.device_box.configure(state="disabled")
            self.log_activity(f"📱 New Device Linked: {device_name} ({ip})")
            
    def log_activity(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def select_file(self):
        path = filedialog.askopenfilename(title="Select a File to Share")
        if path:
            self.target_path = path
            self.is_file = True
            filename = os.path.basename(path)
            self.lbl_target.configure(text=f"Target: {filename}", text_color=("#333333", "white"))

    def select_folder(self):
        path = filedialog.askdirectory(title="Select a Folder to Share")
        if path:
            self.target_path = path
            self.is_file = False
            foldername = os.path.basename(path)
            self.lbl_target.configure(text=f"Target: .../{foldername}/", text_color=("#333333", "white"))

    def toggle_server(self):
        if not self.is_running: self.start_server()
        else: self.stop_server()

    def start_server(self):
        if not self.target_path:
            return messagebox.showwarning("Wait!", "Please select a file or folder first.")
        
        selected_ip = self.ip_combo.get()
        if not selected_ip:
            return messagebox.showerror("Network Error", "No network found.")

        self.current_token = secrets.token_hex(4)

        if self.is_file:
            directory = os.path.dirname(self.target_path)
            filename = os.path.basename(self.target_path)
            os.chdir(directory)
            url = f"http://{selected_ip}:{PORT}/{quote(filename)}?token={self.current_token}"
        else:
            os.chdir(self.target_path)
            url = f"http://{selected_ip}:{PORT}/?token={self.current_token}"

        self.generate_and_display_qr(url)

        self.entry_url.configure(state="normal")
        self.entry_url.delete(0, "end")
        self.entry_url.insert(0, url)
        self.entry_url.configure(state="readonly")

        self.is_running = True
        self.btn_toggle.configure(text="🛑 Stop Server", fg_color="#e74c3c", hover_color="#c0392b")
        self.btn_file.configure(state="disabled")
        self.btn_folder.configure(state="disabled")
        
        self.log_activity("==================================================")
        self.log_activity(f"📡 SERVER ONLINE: Broadcasting on {selected_ip}")
        self.log_activity(f"🔐 Security Token Active: {self.current_token}")
        self.log_activity("==================================================")

        self.server_thread = threading.Thread(target=self.run_http_server, args=(selected_ip, PORT), daemon=True)
        self.server_thread.start()

    def run_http_server(self, ip, port):
        app_instance = self 

        class CleanLoggerHandler(http.server.SimpleHTTPRequestHandler):
            def log_message(self, format, *args):
                pass 

            def list_directory(self, path):
                try:
                    list_dir = os.listdir(path)
                except OSError:
                    self.send_error(404, "No permission to list directory")
                    return None
                
                list_dir.sort(key=lambda a: a.lower())
                
                r = []
                r.append('<!DOCTYPE html>\n<html>\n<head>\n<meta charset="utf-8">\n')
                r.append('<meta name="viewport" content="width=device-width, initial-scale=1">\n')
                r.append('<title>LocalDrop Secure Hub</title>\n')
                
                r.append('<style>\n')
                r.append('body { font-family: -apple-system, sans-serif; background-color: #f4f5f7; margin: 0; padding: 15px; }\n')
                r.append('.container { max-width: 800px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); overflow: hidden; }\n')
                r.append('.header { background: #2ecc71; color: white; padding: 20px; text-align: center; font-size: 22px; font-weight: bold; }\n')
                r.append('.file-list { list-style: none; padding: 0; margin: 0; }\n')
                r.append('.file-list li { border-bottom: 1px solid #eee; }\n')
                r.append('.file-list li:last-child { border-bottom: none; }\n')
                r.append('.file-list a { display: flex; align-items: center; padding: 15px 20px; text-decoration: none; color: #333; font-size: 16px; }\n')
                r.append('.file-list a:hover { background: #f8f9fa; }\n')
                r.append('.icon { font-size: 24px; margin-right: 15px; }\n')
                r.append('</style>\n</head>\n<body>\n')
                
                r.append('<div class="container">\n')
                r.append('<div class="header">🔒 LocalDrop Secure Hub</div>\n')
                r.append('<ul class="file-list">\n')
                
                for name in list_dir:
                    if name.startswith('.'): continue
                        
                    fullname = os.path.join(path, name)
                    displayname = linkname = name
                    
                    icon = "📄" 
                    if os.path.isdir(fullname):
                        displayname = name + "/"
                        linkname = name + "/"
                        icon = "📁"
                    elif name.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
                        icon = "🎬"
                    elif name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        icon = "🖼️"
                    elif name.lower().endswith(('.pdf', '.txt', '.doc', '.docx', '.csv')):
                        icon = "📝"
                    elif name.lower().endswith(('.zip', '.rar', '.7z')):
                        icon = "📦"
                        
                    enc_link = quote(linkname, errors='surrogatepass')
                    enc_link += f"?token={app_instance.current_token}"

                    r.append(f'<li><a href="{enc_link}"><span class="icon">{icon}</span> {html.escape(displayname)}</a></li>\n')
                    
                r.append('</ul>\n</div>\n</body>\n</html>\n')
                
                encoded = '\n'.join(r).encode('utf-8', 'surrogateescape')
                f = io.BytesIO()
                f.write(encoded)
                f.seek(0)
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                return f

            def do_GET(self):
                parsed_path = urllib.parse.urlparse(self.path)
                
                if parsed_path.path == '/favicon.ico':
                    super().do_GET()
                    return

                query = urllib.parse.parse_qs(parsed_path.query)
                client_token = query.get('token', [''])[0]

                if client_token != app_instance.current_token:
                    self.send_error(403, "Unauthorized: Invalid or missing security token.")
                    app_instance.root.after(0, app_instance.log_activity, f"[BLOCKED] 🚨 Unauthorized access attempt from {self.client_address[0]}")
                    return

                self.path = parsed_path.path

                user_agent = self.headers.get('User-Agent', 'Unknown')
                client_ip = self.client_address[0]
                path = unquote(self.path)

                app_instance.root.after(0, app_instance.register_device, client_ip, user_agent)

                if path != '/' and path != '/favicon.ico':
                    filename = os.path.basename(path)
                    app_instance.root.after(0, app_instance.log_activity, f"[{client_ip}] 👁️ Accessed: {filename}")
                elif path == '/':
                    app_instance.root.after(0, app_instance.log_activity, f"[{client_ip}] 👀 Browsing directory...")

                super().do_GET()

        self.httpd = socketserver.ThreadingTCPServer((ip, port), CleanLoggerHandler)
        try:
            self.httpd.serve_forever()
        except Exception:
            pass

    def stop_server(self):
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
        
        self.is_running = False
        self.btn_toggle.configure(text="🚀 Start Server", fg_color="#2ecc71", hover_color="#27ae60")
        self.btn_file.configure(state="normal")
        self.btn_folder.configure(state="normal")
        
        self.lbl_qr.configure(image=None, text="[ QR Code ]")
        
        self.entry_url.configure(state="normal")
        self.entry_url.delete(0, "end")
        self.entry_url.configure(state="disabled")
        
        self.connected_ips.clear()
        self.current_token = None
        self.log_activity("🛑 SERVER OFFLINE.")
        self.log_activity("==================================================\n")

    def generate_and_display_qr(self, url):
        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        
        raw_pil_img = qr.make_image(fill_color="black", back_color="white").get_image()
        ctk_img = ctk.CTkImage(light_image=raw_pil_img, dark_image=raw_pil_img, size=(220, 220))
        
        self.lbl_qr.configure(image=ctk_img, text="")
        self.lbl_qr.image = ctk_img 

if __name__ == "__main__":
    root = ctk.CTk()
    app = LocalDropPro(root)
    root.mainloop()