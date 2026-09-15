"""
Task Controller - Core Task Management Module
Provides silent, reliable Windows Task Scheduler and process monitoring.
All operations run without flashing console windows.
"""

import os
import sys
import json
import subprocess
import time
import psutil

# Cache task list to avoid redundant PowerShell calls (3 second TTL)
_TASK_CACHE = {
    "timestamp": 0,
    "data": []
}
CACHE_TTL = 3.0


def _get_silent_subprocess_kwargs():
    """Windows-specific creation flags to prevent any console window popup."""
    kwargs = {}
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        kwargs["startupinfo"] = startupinfo
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    return kwargs


def run_powershell_json(ps_script: str):
    """Execute a PowerShell command with hidden window and return parsed JSON."""
    kwargs = _get_silent_subprocess_kwargs()
    cmd = [
        "powershell.exe",
        "-NoProfile",
        "-NonInteractive",
        "-WindowStyle", "Hidden",
        "-ExecutionPolicy", "Bypass",
        "-Command",
        ps_script
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=12,
            **kwargs
        )
        out = proc.stdout.strip()
        if not out:
            return None
        return json.loads(out)
    except subprocess.TimeoutExpired:
        print("[TaskController] PowerShell execution timed out.")
        return None
    except Exception as e:
        print(f"[TaskController] PowerShell execution error: {e}")
        return None


def run_powershell_action(ps_script: str):
    """Execute a PowerShell command silently without parsing JSON."""
    kwargs = _get_silent_subprocess_kwargs()
    cmd = [
        "powershell.exe",
        "-NoProfile",
        "-NonInteractive",
        "-WindowStyle", "Hidden",
        "-ExecutionPolicy", "Bypass",
        "-Command",
        ps_script
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            **kwargs
        )
        return proc.returncode == 0, proc.stdout.strip(), proc.stderr.strip()
    except Exception as e:
        return False, "", str(e)


def extract_target_file(action_str: str) -> dict:
    """Analyze scheduled task action string to detect script target file."""
    if not action_str:
        return {"target_file": "", "file_type": "UNKNOWN", "file_exists": False, "file_dir": ""}

    tokens = action_str.split()
    target = ""
    if tokens:
        target = tokens[0].strip("\"'")
        if target.lower().endswith(("cmd.exe", "powershell.exe", "pwsh.exe", "python.exe", "pythonw.exe", "wscript.exe", "cscript.exe")):
            for tok in tokens[1:]:
                tok_clean = tok.strip("\"'")
                if any(tok_clean.lower().endswith(ext) for ext in [".bat", ".cmd", ".ps1", ".py", ".vbs"]):
                    target = tok_clean
                    break

    ext = os.path.splitext(target)[1].upper().replace(".", "") if target else "UNKNOWN"
    file_exists = os.path.exists(target) if target else False
    file_dir = os.path.dirname(target) if file_exists else ""

    return {
        "target_file": target,
        "file_type": ext if ext else "UNKNOWN",
        "file_exists": file_exists,
        "file_dir": file_dir
    }


def get_user_scheduled_tasks(force_refresh=False):
    """Query scheduled tasks on Windows Task Scheduler with 3s caching."""
    global _TASK_CACHE
    now = time.time()
    if not force_refresh and (now - _TASK_CACHE["timestamp"] < CACHE_TTL) and _TASK_CACHE["data"]:
        return _TASK_CACHE["data"]

    ps_code = """
    $tasks = Get-ScheduledTask | Select-Object TaskName, TaskPath, State, @{Name='Actions';Expression={($_.Actions | ForEach-Object { "$($_.Execute) $($_.Arguments)" }) -join ' ; '}}
    $taskInfo = Get-ScheduledTaskInfo -TaskName * -ErrorAction SilentlyContinue | Select-Object TaskName, TaskPath, LastRunTime, NextRunTime, LastTaskResult

    $infoHash = @{}
    foreach ($ti in $taskInfo) {
        $key = "$($ti.TaskPath)$($ti.TaskName)"
        $infoHash[$key] = $ti
    }

    $results = @()
    foreach ($t in $tasks) {
        $key = "$($t.TaskPath)$($t.TaskName)"
        $info = $infoHash[$key]

        $results += [PSCustomObject]@{
            name = $t.TaskName
            path = $t.TaskPath
            state = $t.State.ToString()
            action = $t.Actions
            lastRun = if ($info -and $info.LastRunTime) { $info.LastRunTime.ToString("yyyy-MM-dd HH:mm:ss") } else { "" }
            nextRun = if ($info -and $info.NextRunTime) { $info.NextRunTime.ToString("yyyy-MM-dd HH:mm:ss") } else { "" }
            lastResult = if ($info) { $info.LastTaskResult } else { 0 }
        }
    }
    $results | ConvertTo-Json -Depth 3 -Compress
    """

    data = run_powershell_json(ps_code)
    if not data:
        return _TASK_CACHE["data"] if _TASK_CACHE["data"] else []

    if isinstance(data, dict):
        data = [data]

    results = []
    current_user = os.environ.get("USERNAME", "").lower()
    user_profile = os.environ.get("USERPROFILE", "").lower()

    custom_keywords = ["desktop\\", "documents\\", "scripts\\", "automation\\", "tasks\\", "tunnel", "reminder", "alarm", "booking", "sync", "wsl", "whisper", "paper"]
    if current_user:
        custom_keywords.extend([f"users\\{current_user}", current_user])
    if user_profile:
        custom_keywords.append(user_profile)

    for item in data:
        name = item.get("name", "")
        path = item.get("path", "")
        state = item.get("state", "Ready")
        action = item.get("action", "") or ""
        last_run = item.get("lastRun", "")
        next_run = item.get("nextRun", "")
        last_result = item.get("lastResult", 0)

        file_meta = extract_target_file(action)
        is_batch = file_meta["file_type"] in ["BAT", "CMD"]

        act_lower = action.lower()
        name_lower = name.lower()
        is_vendor_updater = any(v in act_lower or v in name_lower for v in ["onedrive", "adobe", "firefox", "mozilla", "nvidia", "googleuserpeh", "zoomupdate"])

        is_custom = (
            not is_vendor_updater
            and (
                is_batch
                or any(ext in act_lower for ext in [".ps1", ".py", ".vbs", "pythonw", "python.exe", "powershell.exe"])
                or any(k in act_lower for k in custom_keywords)
            )
        )

        if last_result == 0:
            result_desc = "Success (0)"
        elif last_result == 267011:
            result_desc = "Ready (Pending)"
        elif last_result == 267009:
            result_desc = "Running"
        else:
            result_desc = f"Exit Code {last_result}"

        results.append({
            "name": name,
            "path": path,
            "state": state,
            "action": action,
            "target_file": file_meta["target_file"],
            "file_type": file_meta["file_type"],
            "file_exists": file_meta["file_exists"],
            "file_dir": file_meta["file_dir"],
            "is_batch": is_batch,
            "is_custom": is_custom,
            "last_run": last_run,
            "next_run": next_run,
            "last_result": last_result,
            "last_result_desc": result_desc
        })

    # Sort custom tasks first
    results.sort(key=lambda x: (not x["is_custom"], not x["is_batch"], x["name"].lower()))
    _TASK_CACHE["timestamp"] = now
    _TASK_CACHE["data"] = results
    return results


def get_running_batch_processes():
    """Find currently active cmd.exe or batch processes."""
    procs = []
    for p in psutil.process_iter(["pid", "name", "cmdline", "create_time"]):
        try:
            name = (p.info["name"] or "").lower()
            if name in ["cmd.exe", "conhost.exe"]:
                cmdline = " ".join(p.info["cmdline"] or [])
                cmd_lower = cmdline.lower()
                if any(ext in cmd_lower for ext in [".bat", ".cmd", "serve", "tunnel", "run", "start"]):
                    procs.append({
                        "pid": p.info["pid"],
                        "name": p.info["name"],
                        "cmdline": cmdline,
                        "started": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(p.info["create_time"])),
                        "memory_mb": round(p.memory_info().rss / (1024 * 1024), 1)
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return procs


def toggle_scheduled_task(task_name: str, enable: bool):
    """Enable or Disable a scheduled task."""
    cmd_name = "Enable-ScheduledTask" if enable else "Disable-ScheduledTask"
    safe_name = task_name.replace("'", "''")
    ps = f"{cmd_name} -TaskName '{safe_name}' -ErrorAction Stop"
    success, out, err = run_powershell_action(ps)

    get_user_scheduled_tasks(force_refresh=True)

    if success:
        return {
            "success": True,
            "message": f"Task '{task_name}' successfully {'enabled' if enable else 'disabled'}."
        }
    else:
        return {
            "success": False,
            "message": f"Failed to {'enable' if enable else 'disable'} task. May require Administrator privileges.",
            "error": err
        }


def run_scheduled_task(task_name: str):
    """Manually start a scheduled task immediately."""
    safe_name = task_name.replace("'", "''")
    ps = f"Start-ScheduledTask -TaskName '{safe_name}' -ErrorAction Stop"
    success, out, err = run_powershell_action(ps)

    get_user_scheduled_tasks(force_refresh=True)

    if success:
        return {"success": True, "message": f"Started task '{task_name}' successfully."}
    else:
        return {"success": False, "message": f"Failed to start task.", "error": err}


def stop_scheduled_task(task_name: str):
    """Force stop a currently running scheduled task."""
    safe_name = task_name.replace("'", "''")
    ps = f"Stop-ScheduledTask -TaskName '{safe_name}' -ErrorAction Stop"
    success, out, err = run_powershell_action(ps)

    get_user_scheduled_tasks(force_refresh=True)

    if success:
        return {"success": True, "message": f"Stopped task '{task_name}' successfully."}
    else:
        return {"success": False, "message": f"Failed to stop task.", "error": err}


def kill_batch_process(pid: int):
    """Terminate a background batch process by PID."""
    try:
        p = psutil.Process(pid)
        p.kill()
        return {"success": True, "message": f"Terminated process PID {pid}."}
    except psutil.NoSuchProcess:
        return {"success": True, "message": f"Process PID {pid} was already terminated."}
    except Exception as e:
        return {"success": False, "message": f"Failed to terminate PID {pid}.", "error": str(e)}


def open_file_folder(file_path: str):
    """Open File Explorer highlighting the script file."""
    if not file_path or not os.path.exists(file_path):
        return {"success": False, "message": "File does not exist or invalid path."}

    norm_path = os.path.normpath(file_path)
    kwargs = _get_silent_subprocess_kwargs()
    try:
        subprocess.Popen(f'explorer.exe /select,"{norm_path}"', **kwargs)
        return {"success": True, "message": f"Opened Explorer: {norm_path}"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def edit_file_in_notepad(file_path: str):
    """Open script file in Notepad."""
    if not file_path or not os.path.exists(file_path):
        return {"success": False, "message": "File does not exist or invalid path."}

    norm_path = os.path.normpath(file_path)
    kwargs = _get_silent_subprocess_kwargs()
    try:
        subprocess.Popen(["notepad.exe", norm_path], **kwargs)
        return {"success": True, "message": f"Opened Notepad: {norm_path}"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def delete_scheduled_task(task_name: str, delete_script_file: bool = False, file_path: str = ""):
    """Permanently delete (unregister) a task from Windows Task Scheduler."""
    safe_name = task_name.replace("'", "''")
    ps = f"Unregister-ScheduledTask -TaskName '{safe_name}' -Confirm:$false -ErrorAction Stop"
    success, out, err = run_powershell_action(ps)

    file_deleted = False
    file_err = ""
    if success and delete_script_file and file_path:
        norm_path = os.path.normpath(file_path)
        if os.path.exists(norm_path):
            try:
                os.remove(norm_path)
                file_deleted = True
            except Exception as fe:
                file_err = str(fe)

    get_user_scheduled_tasks(force_refresh=True)

    if success:
        msg = f"Task '{task_name}' successfully removed from Windows Task Scheduler."
        if delete_script_file:
            if file_deleted:
                msg += f" Script file '{file_path}' was also deleted."
            else:
                msg += f" (Script file deletion failed: {file_err})"
        return {"success": True, "message": msg, "file_deleted": file_deleted}
    else:
        return {
            "success": False,
            "message": f"Failed to delete task. May require Administrator privileges.",
            "error": err
        }
