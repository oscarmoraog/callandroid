import shutil
import subprocess
from pathlib import Path


def find_adb() -> str:
    adb_path = shutil.which("adb")
    if adb_path:
        return adb_path

    common = [
        r"C:\platform-tools\adb.exe",
        r"C:\Android\platform-tools\adb.exe",
        r"C:\Users\{USER}\AppData\Local\Android\Sdk\platform-tools\adb.exe",
    ]
    for p in common:
        path = Path(p.replace("{USER}", Path.home().name))
        if path.exists():
            return str(path)

    raise FileNotFoundError(
        "ADB não encontrado.\n\n"
        "Instale o Android SDK Platform Tools e\n"
        "adicione o ADB ao PATH do Windows."
    )


def list_devices(adb_path: str) -> list[dict]:
    result = subprocess.run(
        [adb_path, "devices"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Erro ao executar adb devices: {result.stderr.strip()}")

    devices = []
    for line in result.stdout.strip().splitlines()[1:]:
        parts = line.split()
        if len(parts) == 2:
            serial, status = parts
            devices.append({"serial": serial, "status": status})
    return devices


def get_available_device(adb_path: str) -> str:
    devices = list_devices(adb_path)

    if not devices:
        raise ConnectionError(
            "Nenhum dispositivo Android conectado.\n\n"
            "Conecte o Android via USB,\n"
            "ative a depuração USB e autorize este computador."
        )

    for d in devices:
        if d["status"] == "device":
            return d["serial"]

    statuses = {d["status"] for d in devices}

    if "unauthorized" in statuses:
        raise PermissionError(
            "O Android ainda não autorizou este computador.\n\n"
            "Verifique a tela do celular e aceite\n"
            "a autorização da depuração USB."
        )

    if "offline" in statuses:
        raise ConnectionError(
            "O dispositivo Android está offline.\n\n"
            "Reconecte o cabo USB e tente novamente."
        )

    raise ConnectionError(
        "Nenhum dispositivo Android conectado.\n\n"
        "Conecte o Android via USB,\n"
        "ative a depuração USB e autorize este computador."
    )


def dial(adb_path: str, phone: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            adb_path,
            "shell",
            "am",
            "start",
            "-a",
            "android.intent.action.CALL",
            "-d",
            f"tel:{phone}",
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )


def hangup(adb_path: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [adb_path, "shell", "input", "keyevent", "KEYCODE_ENDCALL"],
        capture_output=True,
        text=True,
        timeout=10,
    )


def is_call_active(adb_path: str) -> bool:
    try:
        result = subprocess.run(
            [adb_path, "shell", "dumpsys", "telephony.registry"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return "mCallState=2" in result.stdout
    except Exception:
        return False
