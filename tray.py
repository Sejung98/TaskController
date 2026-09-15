"""
Task Controller - System Tray Application
Runs quietly in the Windows notification area (bottom-right near clock).
Provides instant monitoring and control over automated tasks and scripts.
"""

import os
import sys
import threading
import time
import webbrowser
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item, Menu
import psutil

# Resolve base directory
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CORE_DIR = os.path.join(BASE_DIR, "core")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
sys.path.insert(0, CORE_DIR)

import task_manager
import server

WEB_URL = f"http://127.0.0.1:{server.DEFAULT_PORT}"
tray_icon_instance = None
cached_tasks = []


def ensure_single_instance():
    """Kill any previous tray instances to prevent duplicates."""
    my_pid = os.getpid()
    for p in psutil.process_iter(["pid", "cmdline"]):
        try:
            if p.info["pid"] == my_pid:
                continue
            cmd = " ".join(p.info["cmdline"] or [])
            if "tray.py" in cmd:
                p.kill()
        except Exception:
            pass


def create_tray_icon_image():
    """Load high quality controller icon for system tray."""
    possible_paths = [
        os.path.join(ASSETS_DIR, "tray_icon.png"),
        os.path.join(BASE_DIR, "tray_icon.png"),
        os.path.join(ASSETS_DIR, "icon.png"),
        os.path.join(BASE_DIR, "icon.png"),
    ]
    for p in possible_paths:
        if os.path.exists(p):
            try:
                im = Image.open(p).convert("RGBA")
                return im.resize((64, 64), Image.Resampling.LANCZOS)
            except Exception:
                pass

    # Fallback minimal icon
    size = (64, 64)
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((4, 4, 60, 60), radius=14, fill=(26, 32, 53, 255), outline=(99, 102, 241, 255), width=2)
    return image


def refresh_tasks():
    global cached_tasks
    try:
        cached_tasks = task_manager.get_user_scheduled_tasks(force_refresh=True)
    except Exception as e:
        print(f"[TaskController] Failed to refresh tasks: {e}")
        cached_tasks = []


def open_web_dashboard(icon=None, item=None):
    """Open the Task Controller web dashboard in default browser."""
    webbrowser.open(WEB_URL)


def quit_tray_app(icon=None, item=None):
    """Gracefully quit the tray application."""
    if tray_icon_instance:
        tray_icon_instance.stop()
    os._exit(0)


def build_menu():
    """Build dynamic English system tray context menu."""
    global cached_tasks
    refresh_tasks()

    items = []

    # 1. Header & Open Dashboard
    items.append(item("🎮 Open Web Dashboard", open_web_dashboard, default=True))
    items.append(Menu.SEPARATOR)

    # 2. Automation Tasks Submenus
    custom_tasks = [t for t in cached_tasks if t.get("is_custom")]

    if not custom_tasks:
        items.append(item("(No active custom tasks found)", None, enabled=False))
    else:
        task_submenus = []
        for t in custom_tasks[:20]:
            name = t.get("name", "Unknown")
            state = t.get("state", "Ready")
            is_enabled = state != "Disabled"
            target_file = t.get("target_file", "")

            state_icon = "🟢" if state == "Ready" else ("🔵" if state == "Running" else "⚪")
            label = f"{state_icon} {name}"

            def make_action(t_name, act_type, param=None):
                def action_func(icon, item):
                    if act_type == "run":
                        task_manager.run_scheduled_task(t_name)
                    elif act_type == "stop":
                        task_manager.stop_scheduled_task(t_name)
                    elif act_type == "toggle":
                        task_manager.toggle_scheduled_task(t_name, param)
                    elif act_type == "folder":
                        task_manager.open_file_folder(param)
                    elif act_type == "edit":
                        task_manager.edit_file_in_notepad(param)
                    elif act_type == "delete":
                        task_manager.delete_scheduled_task(t_name)
                    update_tray_menu()
                return action_func

            sub_items = [
                item(f"Status: {state} | Result: {t.get('last_result_desc', '')}", None, enabled=False),
                item(f"Next Run: {t.get('next_run') or 'None'}", None, enabled=False),
                Menu.SEPARATOR,
                item("▶ Run Task Now", make_action(name, "run")),
                item("⏹ Force Stop", make_action(name, "stop")),
                item("⚡ Disable Task" if is_enabled else "⚡ Enable Task", make_action(name, "toggle", not is_enabled)),
            ]
            if target_file:
                sub_items.append(Menu.SEPARATOR)
                sub_items.append(item("📂 Open Script Folder", make_action(name, "folder", target_file)))
                sub_items.append(item("📝 Edit Script in Notepad", make_action(name, "edit", target_file)))

            sub_items.append(Menu.SEPARATOR)
            sub_items.append(item("🗑️ Delete Scheduled Task", make_action(name, "delete")))

            task_submenus.append(item(label, Menu(*sub_items)))

        items.append(item("⚡ My Automation Tasks", Menu(*task_submenus)))

    # 3. Actions
    items.append(Menu.SEPARATOR)
    items.append(item("🔄 Refresh Task List", lambda icon, item: update_tray_menu()))
    items.append(item("❌ Exit Program", quit_tray_app))

    return Menu(*items)


def update_tray_menu():
    global tray_icon_instance
    if tray_icon_instance:
        tray_icon_instance.menu = build_menu()


def start_server_in_background():
    """Start local web server silently in background."""
    try:
        server.run_server(open_browser=False)
    except Exception as e:
        print(f"[TaskController] Web server error: {e}")


def main():
    global tray_icon_instance
    ensure_single_instance()

    # Start background web server
    server_thread = threading.Thread(target=start_server_in_background, daemon=True)
    server_thread.start()

    # Create and run system tray icon
    icon_image = create_tray_icon_image()
    tray_icon_instance = pystray.Icon(
        "TaskController",
        icon_image,
        "Task Controller - Windows Automation & Tasks",
        menu=build_menu()
    )

    print("==================================================")
    print("  Task Controller System Tray Started")
    print("  Right-click the controller icon near the clock.")
    print("==================================================")
    tray_icon_instance.run()


if __name__ == "__main__":
    main()
