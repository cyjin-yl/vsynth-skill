"""
VOCALOID .vpr (ZIP + JSON) 文件解析器。
VOCALOID 5/6 使用的 ZIP 容器格式，内部包含 Project/sequence.json。
"""

import json
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_parser import BaseParser
from .utils import extract_zip_bytes, extract_zip_file, is_zip_file, safe_get


class VprParser(BaseParser):
    """VOCALOID 5/6 VPR (ZIP + JSON) 文件解析器。"""

    SUPPORTED_EXTENSIONS = [".vpr"]
    FORMAT_NAME = "VOCALOID VPR"

    SEQUENCE_JSON_PATH = "Project/sequence.json"

    def _extract_sequence_json(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """从 VPR ZIP 容器中提取 sequence.json 内容。"""
        text = extract_zip_file(file_path, self.SEQUENCE_JSON_PATH, encoding="utf-8")
        if text is None:
            # Try with backslash separator
            text = extract_zip_file(file_path, "Project\\sequence.json", encoding="utf-8")
        if text is None:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    def validate(self, file_path: Path) -> tuple[bool, List[str]]:
        """验证 VPR 文件。"""
        errors: List[str] = []

        if not is_zip_file(file_path):
            errors.append("Not a valid ZIP file")
            return False, errors

        # Check for sequence.json
        found = False
        try:
            with zipfile.ZipFile(file_path, "r") as zf:
                for name in zf.namelist():
                    if name.replace("\\", "/") == self.SEQUENCE_JSON_PATH:
                        found = True
                        break
        except Exception as e:
            errors.append(f"Cannot read ZIP contents: {e}")
            return False, errors

        if not found:
            errors.append(f"Missing {self.SEQUENCE_JSON_PATH} in ZIP container")
            return False, errors

        # Validate JSON structure
        seq_json = self._extract_sequence_json(file_path)
        if seq_json is None:
            errors.append("Cannot parse sequence.json as valid JSON")
            return False, errors

        if "version" not in seq_json:
            errors.append("Missing 'version' field in sequence.json")
        if "masterTrack" not in seq_json:
            errors.append("Missing 'masterTrack' field in sequence.json")
        if "tracks" not in seq_json:
            errors.append("Missing 'tracks' field in sequence.json")

        return len(errors) == 0, errors

    def info(self, file_path: Path) -> Dict[str, Any]:
        """提取 VPR 文件信息。"""
        seq_json = self._extract_sequence_json(file_path)
        if seq_json is None:
            raise ValueError("Cannot parse VPR file: sequence.json not found or invalid")

        result: Dict[str, Any] = {
            "format": "VOCALOID VPR",
            "file_name": file_path.name,
            "version": seq_json.get("version", ""),
            "vendor": seq_json.get("vendor", ""),
            "title": seq_json.get("title", ""),
        }

        # Parse masterTrack
        master_track = seq_json.get("masterTrack", {})

        # Time signatures
        time_sigs: List[Dict[str, Any]] = []
        for ts in master_track.get("timeSignature", []):
            time_sigs.append({
                "measure_position": ts.get("bar", 0),
                "numerator": ts.get("numer", 4),
                "denominator": ts.get("denom", 4),
            })
        result["time_signatures"] = time_sigs

        # Tempos
        tempos: List[Dict[str, Any]] = []
        for tp in master_track.get("tempo", []):
            pos = tp.get("pos", 0)
            val = tp.get("value", 12000)
            bpm = val / 100.0
            tempos.append({"tick_position": pos, "bpm": round(bpm, 2)})
        result["tempos"] = tempos

        result["sampling_rate"] = master_track.get("samplingRate", 44100)
        result["loop"] = master_track.get("loop", False)

        # Parse tracks
        tracks: List[Dict[str, Any]] = []
        total_notes = 0
        singers: List[str] = []

        for track_idx, track in enumerate(seq_json.get("tracks", [])):
            track_type = track.get("type", "vocaloid")
            track_name = track.get("name", f"Track {track_idx + 1}")
            track_info: Dict[str, Any] = {
                "index": track_idx,
                "name": track_name,
                "type": track_type,
                "notes": [],
            }

            for part in track.get("parts", []):
                part_type = part.get("type", "")
                part_start = part.get("start", 0)

                if part_type == "musical" or "notes" in part:
                    for note in part.get("notes", []):
                        pos = note.get("pos", 0)
                        duration = note.get("duration", 0)
                        pitch = note.get("pitch", 60)
                        if "number" in note:
                            pitch = note["number"]
                        lyric = note.get("lyric", "")
                        phoneme = note.get("phoneme", "")
                        velocity = note.get("velocity", 64)
                        dynamics = note.get("dynamics", 64)

                        track_info["notes"].append({
                            "tick_on": part_start + pos,
                            "tick_off": part_start + pos + duration,
                            "pitch": pitch,
                            "lyric": lyric,
                            "phoneme": phoneme,
                            "velocity": velocity,
                            "dynamics": dynamics,
                        })
                        total_notes += 1

            tracks.append(track_info)

        # Parse voices
        for voice in seq_json.get("voices", []):
            comp_id = voice.get("compID", "")
            if comp_id:
                singers.append(comp_id)

        result["tracks"] = tracks
        result["track_count"] = len(tracks)
        result["total_notes"] = total_notes
        result["singers"] = singers

        return result
