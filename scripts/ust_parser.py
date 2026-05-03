"""
UTAU .ust (INI-like text) 文件解析器。
支持 UST 1.2 / 1.19 / 1.20 / 2.0 版本，支持 Shift-JIS 和 UTF-8 编码。
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_parser import BaseParser
from .utils import detect_encoding, midi_note_name, parse_ini_style_text


class UstParser(BaseParser):
    """UTAU UST (INI-like text) 文件解析器。"""

    SUPPORTED_EXTENSIONS = [".ust"]
    FORMAT_NAME = "UTAU UST"

    def _parse_ust_file(self, file_path: Path) -> Dict[str, Any]:
        """
        解析 UST 文件内容。

        Returns:
            包含 version, setting, notes 的字典。
        """
        encoding = detect_encoding(file_path)
        text = file_path.read_text(encoding=encoding)

        result: Dict[str, Any] = {
            "version": "",
            "charset": "",
            "setting": {},
            "notes": [],
            "prev_note": {},
            "next_note": {},
        }

        current_section = ""
        current_data: Dict[str, str] = {}

        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue

            # Section header
            if line.startswith("[") and line.endswith("]"):
                # Save previous section
                self._save_section(result, current_section, current_data)
                current_section = line[1:-1]
                current_data = {}
                continue

            # Key-value pair
            if "=" in line:
                key, value = line.split("=", 1)
                current_data[key.strip()] = value.strip()
            else:
                # Line without '=' (e.g., 'UST Version2.0')
                # Store as empty key for version line
                current_data[""] = line

        # Save last section
        self._save_section(result, current_section, current_data)

        return result

    def _save_section(self, result: Dict[str, Any], section: str, data: Dict[str, str]) -> None:
        """保存解析到的 section 数据。"""
        if not section:
            return

        # Strip # prefix if present for section matching
        bare_section = section.lstrip("#")

        if bare_section == "VERSION":
            result["version"] = data.get("", "")
            for key, value in data.items():
                if key and key.lower() == "charset":
                    result["charset"] = value
        elif bare_section == "SETTING":
            result["setting"] = data
            # Extract version from setting if present (UST 1.19)
            if "UstVersion" in data:
                result["version"] = f"UST {data['UstVersion']}"
        elif bare_section == "PREV":
            result["prev_note"] = data
        elif bare_section == "NEXT":
            result["next_note"] = data
        elif bare_section == "TRACKEND":
            pass
        elif bare_section.isdigit():
            # Note section (#0000, #0001, etc.) - only numeric
            note_data = dict(data)
            note_data["_section"] = section
            result["notes"].append(note_data)

    def validate(self, file_path: Path) -> tuple[bool, List[str]]:
        """验证 UST 文件。"""
        errors: List[str] = []

        try:
            encoding = detect_encoding(file_path)
            text = file_path.read_text(encoding=encoding)
        except Exception as e:
            return False, [f"Cannot read file: {e}"]

        if "[#VERSION]" not in text and "[#SETTING]" not in text:
            errors.append("Missing [#VERSION] or [#SETTING] section")

        if "[#0000]" not in text:
            errors.append("No note sections found (missing [#0000])")

        # Check for valid version
        version_match = re.search(r"UST\s+Version\s*(\d+\.\d+)", text)
        if version_match:
            version = version_match.group(1)
            if version not in ["1.2", "1.19", "1.20", "2.0"]:
                errors.append(f"Unrecognized UST version: {version}")
        else:
            # Try UstVersion= format
            if "UstVersion=" not in text:
                errors.append("Cannot determine UST version")

        # Check for TRACKEND
        if "[#TRACKEND]" not in text:
            errors.append("Missing [#TRACKEND] marker")

        return len(errors) == 0, errors

    def info(self, file_path: Path) -> Dict[str, Any]:
        """提取 UST 文件信息。"""
        parsed = self._parse_ust_file(file_path)
        setting = parsed.get("setting", {})
        notes_data = parsed.get("notes", [])

        result: Dict[str, Any] = {
            "format": "UTAU UST",
            "file_name": file_path.name,
            "version": parsed.get("version", ""),
            "charset": parsed.get("charset", detect_encoding(file_path)),
            "tempo": 120.0,
            "project_name": setting.get("ProjectName", ""),
            "voice_dir": setting.get("VoiceDir", ""),
            "out_file": setting.get("OutFile", ""),
            "tracks": 1,
            "mode2": False,
        }

        # Parse tempo
        tempo_str = setting.get("Tempo", "")
        if tempo_str:
            try:
                # Handle comma as decimal separator
                tempo_str = tempo_str.replace(",", ".")
                result["tempo"] = float(tempo_str)
            except ValueError:
                pass

        # Parse tracks
        tracks_str = setting.get("Tracks", "")
        if tracks_str:
            try:
                result["tracks"] = int(tracks_str)
            except ValueError:
                pass

        # Parse Mode2
        mode2_str = setting.get("Mode2", "").lower()
        result["mode2"] = mode2_str == "true"

        # Parse flags
        result["flags"] = setting.get("Flags", "")

        # Parse time signature
        time_sig_str = setting.get("TimeSignatures", "")
        time_sigs: List[Dict[str, Any]] = []
        if time_sig_str:
            # Format: (4/4/0)
            match = re.search(r"\((\d+)/(\d+)/(\d+)\)", time_sig_str)
            if match:
                time_sigs.append({
                    "measure_position": int(match.group(3)),
                    "numerator": int(match.group(1)),
                    "denominator": int(match.group(2)),
                })
        if not time_sigs:
            time_sigs.append({"measure_position": 0, "numerator": 4, "denominator": 4})
        result["time_signatures"] = time_sigs

        # Tempos
        result["tempos"] = [{"tick_position": 0, "bpm": result["tempo"]}]

        # Parse notes
        notes: List[Dict[str, Any]] = []
        current_tick = 0

        for note_data in notes_data:
            try:
                length = int(note_data.get("Length", "480"))
            except ValueError:
                length = 480

            lyric = note_data.get("Lyric", "")
            try:
                pitch = int(note_data.get("NoteNum", "60"))
            except ValueError:
                pitch = 60

            try:
                intensity = float(note_data.get("Intensity", "100"))
            except ValueError:
                intensity = 100.0

            try:
                modulation = float(note_data.get("Modulation", "0"))
            except ValueError:
                modulation = 0.0

            # Mode2 pitch data
            mode2_data: Dict[str, Any] = {}
            pbs = note_data.get("PBS", "")
            pbw = note_data.get("PBW", "")
            pby = note_data.get("PBY", "")
            pbm = note_data.get("PBM", "")
            if pbs:
                mode2_data["pbs"] = pbs
            if pbw:
                mode2_data["pbw"] = pbw
            if pby:
                mode2_data["pby"] = pby
            if pbm:
                mode2_data["pbm"] = pbm

            # Vibrato
            vbr = note_data.get("VBR", "")
            vibrato_data: Optional[Dict[str, Any]] = None
            if vbr:
                parts = vbr.split(",")
                if len(parts) >= 7:
                    vibrato_data = {
                        "length": parts[0],
                        "cycle": parts[1],
                        "depth": parts[2],
                        "fade_in": parts[3],
                        "fade_out": parts[4],
                        "phase": parts[5],
                        "height": parts[6],
                    }

            # Envelope
            envelope = note_data.get("Envelope", "")

            # Note-level tempo
            note_tempo = None
            if "Tempo" in note_data:
                try:
                    note_tempo = float(note_data["Tempo"].replace(",", "."))
                except ValueError:
                    pass

            note_info: Dict[str, Any] = {
                "tick_on": current_tick,
                "tick_off": current_tick + length,
                "pitch": pitch,
                "lyric": lyric,
                "intensity": intensity,
                "modulation": modulation,
                "mode2": mode2_data if mode2_data else None,
                "vibrato": vibrato_data,
                "envelope": envelope,
                "flags": note_data.get("Flags", ""),
            }
            if note_tempo is not None:
                note_info["tempo"] = note_tempo

            notes.append(note_info)
            current_tick += length

        result["tracks"] = [{
            "index": 0,
            "name": result.get("project_name", "Track 1"),
            "notes": notes,
        }]
        result["total_notes"] = len(notes)

        return result
