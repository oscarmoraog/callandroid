import sys
import os

def write_vbs(target_path, exe_path):
    vbs = f'Set oWsh = CreateObject("WScript.Shell")\noWsh.Run "{exe_path}", 0, False\n'
    with open(target_path, "w") as f:
        f.write(vbs)

def write_shortcut_vbs(target_path, exe_path, work_dir, shortcut_path):
    vbs = (
        f'Set oWsh = CreateObject("WScript.Shell")\n'
        f'Set oLink = oWsh.CreateShortcut("{shortcut_path}")\n'
        f'oLink.TargetPath = "{exe_path}"\n'
        f'oLink.WorkingDirectory = "{work_dir}"\n'
        f'oLink.WindowStyle = 7\n'
        f'oLink.Description = "CallAndroid Server"\n'
        f'oLink.Save\n'
    )
    with open(target_path, "w") as f:
        f.write(vbs)

if __name__ == "__main__":
    action = sys.argv[1]
    if action == "run":
        write_vbs(sys.argv[2], sys.argv[3])
    elif action == "shortcut":
        write_shortcut_vbs(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
