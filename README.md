# 🚀 LocalDrop Pro – Secure Local File Sharing

![Python Version](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-1F2937?style=for-the-badge)
![Interface](https://img.shields.io/badge/Interface-Desktop%20GUI-2C3E50?style=for-the-badge)
![Feature](https://img.shields.io/badge/Feature-Local%20File%20Sharing-8E44AD?style=for-the-badge)
![Security](https://img.shields.io/badge/Security-Token%20Protected-27AE60?style=for-the-badge)
![QR](https://img.shields.io/badge/Access-QR%20Code%20Enabled-16A085?style=for-the-badge)

**LocalDrop Pro** is a sleek, modern desktop application that allows you to **share files and folders over your local network** instantly using a browser — no external services, no uploads, no hassle.

Built with **Python + CustomTkinter**, it provides a clean UI, QR-based access, and token-based security for safe local transfers.

---

## ✨ Features

* 📁 **Share Files & Folders** over LAN instantly
* 🔗 **Auto-generated URL + QR Code** for quick access
* 🔐 **Secure Token-Based Access Control**
* 📱 **Device Detection** (Android, iPhone, Windows, etc.)
* 📊 **Live Network Activity Logs**
* 🌐 **Dynamic IP Selection**
* 🎨 **Dark/Light Mode Toggle**
* ⚡ **Multi-device Support (Threaded Server)**
* 🧠 **Smart File Icons (media, docs, archives, etc.)**

---

## 🛠️ Tech Stack

* **Python 3**
* **CustomTkinter** – Modern UI
* **http.server** – Lightweight HTTP server
* **socketserver** – Multi-threaded handling
* **qrcode** – QR code generation
* **Tkinter** – File dialogs & system integration

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/localdrop-pro.git
cd localdrop-pro
```

### 2. Install dependencies

```bash
pip install customtkinter qrcode[pil]
```

### 3. Run the application

```bash
python main.py
```

---

## 🚀 Usage

1. Launch the app
2. Select your **network IP**
3. Choose:

   * 📄 File
   * 📁 Folder
4. Click **🚀 Start Server**
5. Share via:

   * QR Code 📱
   * URL 🔗
6. Open the link on any device in the same network

---

## 🔐 Security

* Each session generates a **unique token**
* Unauthorized requests are:

  * ❌ Blocked
  * 🚨 Logged in activity panel
* Only users with the correct link (token) can access files

---

## 📡 How It Works

* Spins up a **local HTTP server** on your selected IP
* Serves files via browser interface
* Adds **token validation layer** for security
* Tracks connected devices via **User-Agent parsing**

---

## 📁 Project Structure

```
localdrop-pro/
│── main.py
│── README.md
```

---

## ⚠️ Limitations

* Works **only on the same local network (LAN/WiFi)**
* Large file transfers depend on network speed

---

## 💡 Future Improvements

* ⬆️ Upload support (receive files)
* 🔑 Password protection
* 📊 Transfer progress tracking
* 📦 Zip folder downloads
* 🌍 Cross-network tunneling (like ngrok)
* 🧾 Download history

---

## 👨‍💻 Author

**Utkarsh Gupta**

---
