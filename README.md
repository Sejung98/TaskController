# 🎮 Task Controller

> **"Built with Google Gemini because managing numerous AI-driven background tasks, batch automations, and scheduled jobs on Windows was becoming difficult to keep track of."**
>
> A lightweight, modern Windows Scheduled Task and Automation Controller.  
> Provides a silent background system tray app and a high-performance web dashboard with Dark/Light modes.

---

## 🌟 Key Features

- **🎮 System Tray & Web Dashboard**: Monitor, start, stop, and manage background scripts directly from the Windows taskbar or a sleek browser interface.
- **⚡ 100% Silent Execution**: Background queries and triggers run with zero PowerShell console window popups or flashing.
- **🌓 Dark & Light Modes**: Elegant, responsive UI with smooth one-click theme switching.
- **🔄 Task Lifecycle Control**:
  - **Toggle (ON/OFF)**: Enable or disable scheduled tasks safely.
  - **Run & Stop**: Immediately trigger or terminate tasks on-demand.
  - **Delete Task**: Permanently unregister tasks from Windows Task Scheduler (with optional script file cleanup).
- **📂 One-Click Code Access**: Instantly open script folder in File Explorer or edit directly in Notepad.
- **🏃 Process Inspector**: Real-time monitoring and termination of background `cmd.exe` and batch processes.
- **🔒 Privacy & Security**:
  - Zero hardcoded personal paths or credentials.
  - Localhost-only binding (`127.0.0.1`) prevents unauthorized external access.

---

## 📂 Project Architecture

```text
TaskController/
│
├── core/                  # Core Python modules & business logic
│   ├── __init__.py
│   ├── task_manager.py    # Windows Task Scheduler query, control & cache
│   └── server.py          # Local HTTP API & Web dashboard server
│
├── assets/                # Visual assets and icons
│   ├── icon.ico           # Windows multi-size application icon
│   ├── icon.png           # High-resolution transparent master icon
│   ├── tray_icon.png      # High-contrast tray icon
│   └── generate_icons.py  # Icon generation script
│
├── web/                   # Web dashboard frontend
│   ├── index.html         # Clean dashboard UI
│   ├── styles.css         # Minimal styling with Dark/Light themes
│   ├── app.js             # Client logic & theme controller
│   └── favicon.png        # Web favicon
│
├── launchers/             # Dedicated launcher batch scripts
│   ├── run_tray.bat       # Launch System Tray in background
│   ├── run_dashboard.bat  # Launch Web Dashboard in browser
│   ├── stop_all.bat       # Gracefully terminate running background processes
│   ├── install.bat        # Installs required Python dependencies
│   └── build_exe.bat      # Compiles standalone executable (PyInstaller)
│
├── tray.py                # Main system tray entry point
├── requirements.txt       # Python dependencies (pystray, Pillow, psutil)
├── .gitignore             # Standard Git ignore rules
├── LICENSE                # MIT License (Copyright 2026 Sejung)
└── README.md              # Project documentation
```

---

## 🚀 Quick Start Guide

### Option 1: Running with Python (For Developers)

If Python 3.8+ is installed on your computer:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Sejung98/TaskController.git
   cd TaskController
   ```

2. **Install dependencies**:
   - Double-click `launchers\install.bat` (or run `pip install -r requirements.txt`).

3. **Start the application**:
   - **System Tray Mode**: Double-click `launchers\run_tray.bat` (controller icon appears near the clock).
   - **Web Dashboard Mode**: Double-click `launchers\run_dashboard.bat` (opens `http://127.0.0.1:18500` in browser).
   - **Stop Application**: Double-click `launchers\stop_all.bat`.

---

### Option 2: Standalone `.exe` (For General Windows Users)

General Windows users without Python installed cannot run `.bat` files directly. You can build a single executable `.exe`:

1. Double-click `launchers\build_exe.bat`.
2. PyInstaller will compile everything into `dist\TaskController.exe`.
3. Distribute `TaskController.exe` (e.g. upload to **GitHub Releases**). Users can simply download and run it with no dependencies!

---

## 👥 Contributors & Credits

- **[Sejung](https://github.com/Sejung98)** — Creator & Project Lead
- **Google Gemini** — AI Pair Programmer & Code Contributor

---

## 🛡️ Security & Privacy Notice

- **No Personal Information**: All script target paths and user directories are dynamically resolved via system environment variables (`%USERNAME%`, `%USERPROFILE%`).
- **Network Isolation**: The API server strictly binds to `127.0.0.1` (loopback only) and is never accessible across external networks.
- **Safe Deletion**: Deleting a scheduled task only unregisters it from Windows Task Scheduler; deleting the underlying file requires explicit user confirmation.

---

## 📜 License & Copyright

Copyright &copy; 2026 **Sejung**. All rights reserved.  
Licensed under the [MIT License](LICENSE).

