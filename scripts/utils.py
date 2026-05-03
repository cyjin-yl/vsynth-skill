"""
通用工具函数，用于歌声合成工程文件解析。
"""

import io
import json
import struct
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


def detect_encoding(file_path: Path) -> str:
    """
    自动检测文件编码。

    检测策略:
    1. 先尝试 UTF-8 with BOM
    2. 再尝试纯 UTF-8
    3. 最后尝试 Shift-JIS

    Args:
        file_path: 文件路径。

    Returns:
        检测到的编码名称。
    """
    raw = file_path.read_bytes()

    # Check for UTF-8 BOM
    if raw.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"

    # Try UTF-8
    try:
        raw.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        pass

    # Try Shift-JIS
    try:
        raw.decode("shift_jis")
        return "shift_jis"
    except (UnicodeDecodeError, LookupError):
        pass

    # Default to utf-8 and let caller handle errors
    return "utf-8"


def read_text_with_encoding(file_path: Path, encoding: Optional[str] = None) -> str:
    """
    读取文本文件，自动检测编码（如果未指定）。

    Args:
        file_path: 文件路径。
        encoding: 可选的编码名称。如果为 None，自动检测。

    Returns:
        文件内容字符串。
    """
    if encoding is None:
        encoding = detect_encoding(file_path)
    return file_path.read_text(encoding=encoding)


def is_zip_file(file_path: Path) -> bool:
    """检查文件是否为有效的 ZIP 文件。"""
    try:
        with zipfile.ZipFile(file_path, "r"):
            return True
    except (zipfile.BadZipFile, OSError):
        return False


def extract_zip_file(
    file_path: Path, target_path: str, encoding: str = "utf-8"
) -> Optional[str]:
    """
    从 ZIP 文件中提取指定路径的文本内容。

    Args:
        file_path: ZIP 文件路径。
        target_path: ZIP 内部的目标文件路径。
        encoding: 文件编码。

    Returns:
        提取的文本内容，如果找不到则返回 None。
    """
    try:
        with zipfile.ZipFile(file_path, "r") as zf:
            # Normalize path separators
            normalized_target = target_path.replace("\\", "/")
            for name in zf.namelist():
                if name.replace("\\", "/") == normalized_target:
                    return zf.read(name).decode(encoding)
            return None
    except Exception:
        return None


def extract_zip_bytes(file_path: Path, target_path: str) -> Optional[bytes]:
    """
    从 ZIP 文件中提取指定路径的二进制内容。

    Args:
        file_path: ZIP 文件路径。
        target_path: ZIP 内部的目标文件路径。

    Returns:
        提取的二进制内容，如果找不到则返回 None。
    """
    try:
        with zipfile.ZipFile(file_path, "r") as zf:
            normalized_target = target_path.replace("\\", "/")
            for name in zf.namelist():
                if name.replace("\\", "/") == normalized_target:
                    return zf.read(name)
            return None
    except Exception:
        return None


def parse_json_safe(
    data: Union[str, bytes], fallback_encodings: List[str] = None
) -> Optional[Dict[str, Any]]:
    """
    安全地解析 JSON 数据。

    Args:
        data: JSON 字符串或字节。
        fallback_encodings: 如果字节解码失败，尝试的编码列表。

    Returns:
        解析后的 JSON 对象，失败则返回 None。
    """
    if fallback_encodings is None:
        fallback_encodings = ["utf-8", "utf-8-sig", "shift_jis"]

    if isinstance(data, bytes):
        for enc in fallback_encodings:
            try:
                text = data.decode(enc)
                # Remove BOM and NUL characters
                text = text.lstrip("\ufeff").replace("\x00", "")
                return json.loads(text)
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
        return None
    else:
        try:
            text = data.lstrip("\ufeff").replace("\x00", "")
            return json.loads(text)
        except json.JSONDecodeError:
            return None


def read_midi_header(data: bytes) -> Optional[Tuple[int, int, int]]:
    """
    读取 MIDI 文件头部信息。

    Args:
        data: MIDI 文件的前几个字节。

    Returns:
        (format_type, num_tracks, time_division) 或 None。
    """
    if len(data) < 14:
        return None
    if data[:4] != b"MThd":
        return None
    # Skip 4 bytes (MThd) + 4 bytes (length, should be 6)
    if struct.unpack(">I", data[4:8])[0] != 6:
        return None
    format_type = struct.unpack(">H", data[8:10])[0]
    num_tracks = struct.unpack(">H", data[10:12])[0]
    time_division = struct.unpack(">H", data[12:14])[0]
    return (format_type, num_tracks, time_division)


def midi_ticks_to_seconds(ticks: int, bpm: float, ticks_per_quarter: int = 480) -> float:
    """
    将 MIDI tick 转换为秒。

    Args:
        ticks: Tick 数量。
        bpm: 每分钟节拍数。
        ticks_per_quarter: 每四分音符的 tick 数。

    Returns:
        对应的时间（秒）。
    """
    quarter_notes = ticks / ticks_per_quarter
    seconds_per_quarter = 60.0 / bpm
    return quarter_notes * seconds_per_quarter


def seconds_to_midi_ticks(seconds: float, bpm: float, ticks_per_quarter: int = 480) -> int:
    """
    将秒转换为 MIDI tick。

    Args:
        seconds: 时间（秒）。
        bpm: 每分钟节拍数。
        ticks_per_quarter: 每四分音符的 tick 数。

    Returns:
        对应的 tick 数量。
    """
    quarters = seconds / (60.0 / bpm)
    return int(quarters * ticks_per_quarter)


def blick_to_tick(blicks: int, blicks_per_beat: int = 1470000, ticks_per_quarter: int = 480) -> float:
    """
    将 Synthesizer V 的 blick 时间单位转换为 MIDI tick。

    1 blick = 1/blicks_per_beat beat
    1 beat = ticks_per_quarter tick (假设 4/4 拍)

    Args:
        blicks: Blick 数量。
        blicks_per_beat: 每拍的 blick 数（默认 1,470,000）。
        ticks_per_quarter: 每四分音符的 tick 数。

    Returns:
        对应的 tick 数量（浮点数）。
    """
    beats = blicks / blicks_per_beat
    return beats * ticks_per_quarter


def tick_to_blick(ticks: float, blicks_per_beat: int = 1470000, ticks_per_quarter: int = 480) -> int:
    """
    将 MIDI tick 转换为 blick。

    Args:
        ticks: Tick 数量。
        blicks_per_beat: 每拍的 blick 数。
        ticks_per_quarter: 每四分音符的 tick 数。

    Returns:
        对应的 blick 数量（整数）。
    """
    beats = ticks / ticks_per_quarter
    return int(beats * blicks_per_beat)


def clock_to_tick(clock: int, clock_per_tick: int = 2) -> float:
    """
    将 CeVIO Clock 单位转换为 MIDI tick。

    1 Clock = 1/2 tick (即 1 tick = 2 Clock)

    Args:
        clock: Clock 数量。
        clock_per_tick: 每 tick 的 clock 数。

    Returns:
        对应的 tick 数量。
    """
    return clock / clock_per_tick


def tick_to_clock(tick: float, clock_per_tick: int = 2) -> int:
    """
    将 MIDI tick 转换为 CeVIO Clock。

    Args:
        tick: Tick 数量。
        clock_per_tick: 每 tick 的 clock 数。

    Returns:
        对应的 clock 数量。
    """
    return int(tick * clock_per_tick)


def midi_note_name(note_number: int) -> str:
    """
    将 MIDI 音符编号转换为音符名称。

    Args:
        note_number: MIDI 音符编号（C4=60）。

    Returns:
        音符名称如 "C4", "F#5" 等。
    """
    notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    octave = (note_number // 12) - 1
    note = notes[note_number % 12]
    return f"{note}{octave}"


def detect_format(file_path: Path) -> Optional[str]:
    """
    根据文件内容和扩展名自动检测文件格式。

    Args:
        file_path: 文件路径。

    Returns:
        检测到的格式名称，如 "vsqx", "svp", "ust" 等，无法检测则返回 None。
    """
    ext = file_path.suffix.lower()
    name = file_path.name.lower()

    # Extension-based detection
    ext_map = {
        ".vsqx": "vsqx",
        ".vsq": "vsq",
        ".vpr": "vpr",
        ".ust": "ust",
        ".ustx": "ustx",
        ".svp": "svp",
        ".s5p": "s5p",
        ".ccs": "ccs",
        ".ccst": "ccs",
        ".acep": "acep",
        ".mid": "midi",
        ".midi": "midi",
    }

    if ext in ext_map:
        return ext_map[ext]

    # Content-based fallback
    try:
        data = file_path.read_bytes()
    except Exception:
        return None

    # Check for XML
    if data.startswith(b"<?xml") or data.startswith(b"<"):
        text = data[:4096].decode("utf-8", errors="ignore")
        if "vsq3" in text or "vsq4" in text:
            return "vsqx"
        if "CeVIO" in text or "Sequence" in text:
            return "ccs"

    # Check for JSON
    if data.strip().startswith(b"{") or data.strip().startswith(b"["):
        try:
            obj = json.loads(data[:8192].decode("utf-8", errors="ignore"))
            if isinstance(obj, dict):
                if "timeAxis" in obj or "library" in obj:
                    return "svp"
                if "song" in obj and "tracks" in obj:
                    return "s5p"
                if "masterTrack" in obj and "tracks" in obj:
                    return "vpr"
        except json.JSONDecodeError:
            pass

    # Check for ZIP
    if is_zip_file(file_path):
        return "vpr"

    # Check for MIDI
    if data[:4] == b"MThd":
        return "midi"

    # Check for UST (INI-like)
    try:
        text = data[:1024].decode("utf-8", errors="ignore")
        if "[#VERSION]" in text or "[#SETTING]" in text:
            return "ust"
    except Exception:
        pass
    try:
        text = data[:1024].decode("shift_jis", errors="ignore")
        if "[#VERSION]" in text or "[#SETTING]" in text:
            return "ust"
    except Exception:
        pass

    return None


def parse_ini_style_text(text: str) -> Dict[str, Dict[str, str]]:
    """
    解析 INI 风格的文本（如 VSQ 的 INI 部分）。

    Args:
        text: INI 风格文本。

    Returns:
        解析后的字典：{section: {key: value}}。
    """
    result: Dict[str, Dict[str, str]] = {}
    current_section = ""

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1]
            if current_section not in result:
                result[current_section] = {}
        elif "=" in line and current_section:
            key, value = line.split("=", 1)
            result[current_section][key.strip()] = value.strip()

    return result


def try_read_json(file_path: Path, encoding: str = "utf-8") -> Optional[Dict[str, Any]]:
    """
    尝试读取文件并解析为 JSON。

    Args:
        file_path: 文件路径。
        encoding: 文件编码。

    Returns:
        解析后的 JSON 对象，失败则返回 None。
    """
    try:
        text = file_path.read_text(encoding=encoding)
        text = text.lstrip("\ufeff").replace("\x00", "")
        return json.loads(text)
    except Exception:
        return None


def safe_get(
    data: Dict[str, Any], key: str, default: Any = None, expected_type: type = None
) -> Any:
    """
    安全地从字典获取值，并可选地进行类型检查。

    Args:
        data: 字典。
        key: 键名。
        default: 默认值。
        expected_type: 期望的类型。

    Returns:
        值或默认值。
    """
    if key not in data or data[key] is None:
        return default
    value = data[key]
    if expected_type is not None and not isinstance(value, expected_type):
        try:
            if expected_type == int:
                return int(value)
            elif expected_type == float:
                return float(value)
            elif expected_type == str:
                return str(value)
            elif expected_type == bool:
                return bool(value)
            elif expected_type == list:
                return list(value)
            elif expected_type == dict:
                return dict(value)
        except (ValueError, TypeError):
            return default
    return value
