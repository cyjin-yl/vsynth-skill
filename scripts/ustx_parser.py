"""
OpenUtau .ustx (YAML) 文件解析器。
使用 ruamel.yaml 支持 YAML 1.2。
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_parser import BaseParser

# Try to import ruamel.yaml, fallback to standard yaml
try:
    from ruamel.yaml import YAML
    HAS_RUAMEL = True
except ImportError:
    HAS_RUAMEL = False
    try:
        import yaml  # type: ignore
    except ImportError:
        yaml = None  # type: ignore


class UstxParser(BaseParser):
    """OpenUtau USTX (YAML) 文件解析器。"""

    SUPPORTED_EXTENSIONS = [".ustx"]
    FORMAT_NAME = "OpenUtau USTX"

    def _load_yaml(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        加载 YAML 文件。

        优先使用 ruamel.yaml，如果不存在则尝试 pyyaml。
        """
        if HAS_RUAMEL:
            yaml_loader = YAML()
            yaml_loader.preserve_quotes = True
            try:
                with open(file_path, "r", encoding="utf-8-sig") as f:
                    data = yaml_loader.load(f)
                    if isinstance(data, dict):
                        return dict(data)
                    return None
            except Exception:
                return None
        elif yaml is not None:
            try:
                with open(file_path, "r", encoding="utf-8-sig") as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, dict):
                        return data
                    return None
            except Exception:
                return None
        else:
            raise ImportError(
                "No YAML library available. Install ruamel.yaml or pyyaml."
            )

    def validate(self, file_path: Path) -> tuple[bool, List[str]]:
        """验证 USTX 文件。"""
        errors: List[str] = []

        try:
            data = self._load_yaml(file_path)
        except Exception as e:
            return False, [f"Cannot parse YAML: {e}"]

        if data is None:
            errors.append("YAML parsed to None (empty or invalid)")
            return False, errors

        # Check required fields
        if "ustx_version" not in data and "bpm" not in data:
            errors.append("Missing 'ustx_version' or 'bpm' field")

        if "tracks" not in data:
            errors.append("Missing 'tracks' field")

        if "voice_parts" not in data and "parts" not in data:
            errors.append("Missing 'voice_parts' field")

        return len(errors) == 0, errors

    def info(self, file_path: Path) -> Dict[str, Any]:
        """提取 USTX 文件信息。"""
        data = self._load_yaml(file_path)
        if data is None:
            raise ValueError("Cannot parse USTX file: invalid YAML")

        result: Dict[str, Any] = {
            "format": "OpenUtau USTX",
            "file_name": file_path.name,
            "name": data.get("name", ""),
            "ustx_version": data.get("ustx_version", ""),
            "resolution": data.get("resolution", 480),
            "key": data.get("key", 0),
        }

        # Parse time signatures
        time_sigs: List[Dict[str, Any]] = []
        for ts in data.get("time_signatures", []):
            time_sigs.append({
                "measure_position": ts.get("bar_position", 0),
                "numerator": ts.get("beat_per_bar", 4),
                "denominator": ts.get("beat_unit", 4),
            })
        # Fallback to old format
        if not time_sigs and "beat_per_bar" in data:
            time_sigs.append({
                "measure_position": 0,
                "numerator": data.get("beat_per_bar", 4),
                "denominator": data.get("beat_unit", 4),
            })
        result["time_signatures"] = time_sigs if time_sigs else [
            {"measure_position": 0, "numerator": 4, "denominator": 4}
        ]

        # Parse tempos
        tempos: List[Dict[str, Any]] = []
        for tp in data.get("tempos", []):
            tempos.append({
                "tick_position": tp.get("position", 0),
                "bpm": tp.get("bpm", 120.0),
            })
        # Fallback to old format
        if not tempos and "bpm" in data:
            tempos.append({"tick_position": 0, "bpm": data.get("bpm", 120.0)})
        result["tempos"] = tempos if tempos else [{"tick_position": 0, "bpm": 120.0}]

        # Parse tracks
        tracks: List[Dict[str, Any]] = []
        for track_idx, track in enumerate(data.get("tracks", [])):
            tracks.append({
                "index": track_idx,
                "name": track.get("track_name", f"Track {track_idx + 1}"),
                "singer": track.get("singer", ""),
                "phonemizer": track.get("phonemizer", ""),
                "color": track.get("track_color", ""),
                "mute": track.get("mute", False),
                "solo": track.get("solo", False),
                "volume": track.get("volume", 0.0),
                "pan": track.get("pan", 0.0),
            })
        result["tracks_meta"] = tracks
        result["track_count"] = len(tracks)

        # Parse voice parts
        voice_parts = data.get("voice_parts", data.get("parts", []))
        parts: List[Dict[str, Any]] = []
        total_notes = 0

        for part in voice_parts:
            part_info: Dict[str, Any] = {
                "name": part.get("name", ""),
                "track_no": part.get("track_no", 0),
                "position": part.get("position", 0),
                "duration": part.get("duration", 0),
                "notes": [],
            }

            for note in part.get("notes", []):
                note_pos = note.get("position", 0)
                duration = note.get("duration", 480)
                tone = note.get("tone", 60)
                lyric = note.get("lyric", "")

                note_info: Dict[str, Any] = {
                    "tick_on": part_info["position"] + note_pos,
                    "tick_off": part_info["position"] + note_pos + duration,
                    "pitch": tone,
                    "lyric": lyric,
                }

                # Pitch data
                pitch = note.get("pitch")
                if pitch and "data" in pitch:
                    note_info["pitch_points"] = [
                        {"x": p.get("x", 0), "y": p.get("y", 0), "shape": p.get("shape", "io")}
                        for p in pitch["data"]
                    ]

                # Vibrato
                vibrato = note.get("vibrato")
                if vibrato:
                    note_info["vibrato"] = {
                        "length": vibrato.get("length", 0),
                        "period": vibrato.get("period", 175),
                        "depth": vibrato.get("depth", 25),
                    }

                # Phoneme overrides
                phoneme_overrides = note.get("phoneme_overrides", [])
                if phoneme_overrides:
                    note_info["phoneme_overrides"] = phoneme_overrides

                part_info["notes"].append(note_info)
                total_notes += 1

            # Curves
            curves = part.get("curves", [])
            part_info["curves"] = [
                {"xs": c.get("xs", []), "ys": c.get("ys", []), "abbr": c.get("abbr", "")}
                for c in curves
            ]

            parts.append(part_info)

        result["voice_parts"] = parts
        result["total_notes"] = total_notes

        # Expressions
        expressions = data.get("expressions", {})
        result["expressions"] = {
            k: {
                "name": v.get("name", ""),
                "abbr": v.get("abbr", ""),
                "type": v.get("type", ""),
                "min": v.get("min", 0),
                "max": v.get("max", 0),
            }
            for k, v in expressions.items()
        }

        # Wave parts (audio)
        wave_parts = data.get("wave_parts", [])
        result["audio_parts"] = [
            {
                "name": wp.get("name", ""),
                "track_no": wp.get("track_no", 0),
                "position": wp.get("position", 0),
                "path": wp.get("relative_path", ""),
            }
            for wp in wave_parts
        ]

        return result
