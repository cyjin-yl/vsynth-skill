"""
Synthesizer V .s5p (legacy JSON) 文件解析器。
旧版 Synthesizer V Editor (Build 017-018) 使用的格式。
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_parser import BaseParser
from .utils import blick_to_tick, midi_note_name


class S5pParser(BaseParser):
    """Synthesizer V Editor .s5p (legacy JSON) 文件解析器。"""

    SUPPORTED_EXTENSIONS = [".s5p"]
    FORMAT_NAME = "Synthesizer V S5P (Legacy)"

    DEFAULT_BLICKS_PER_BEAT = 1470000
    TICKS_PER_QUARTER = 480

    def _load_s5p(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """加载 S5P 文件。"""
        try:
            text = file_path.read_text(encoding="utf-8")
            text = text.lstrip("\ufeff").replace("\x00", "")
            return json.loads(text)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            # Try utf-16
            try:
                text = file_path.read_text(encoding="utf-16")
                text = text.lstrip("\ufeff").replace("\x00", "")
                return json.loads(text)
            except Exception:
                return None
        except Exception:
            return None

    def validate(self, file_path: Path) -> tuple[bool, List[str]]:
        """验证 S5P 文件。"""
        errors: List[str] = []

        try:
            project = self._load_s5p(file_path)
        except Exception as e:
            return False, [f"Cannot parse file: {e}"]

        if project is None:
            errors.append("No valid JSON found")
            return False, errors

        if "version" not in project:
            errors.append("Missing 'version' field")

        if "song" not in project:
            errors.append("Missing 'song' field (required for .s5p format)")

        return len(errors) == 0, errors

    def info(self, file_path: Path) -> Dict[str, Any]:
        """提取 S5P 文件信息。"""
        project = self._load_s5p(file_path)
        if project is None:
            raise ValueError("Cannot parse S5P file: no valid JSON found")

        version = project.get("version", 1)
        blick_rate = self.DEFAULT_BLICKS_PER_BEAT
        ticks_per_q = self.TICKS_PER_QUARTER

        result: Dict[str, Any] = {
            "format": f"Synthesizer V S5P (Legacy, version {version})",
            "file_name": file_path.name,
            "version": version,
            "blick_rate": blick_rate,
            "ticks_per_quarter": ticks_per_q,
        }

        song = project.get("song", {})

        # Tempos
        tempos: List[Dict[str, Any]] = []
        for tp in song.get("tempo", []):
            pos_blicks = tp.get("position", 0)
            bpm = tp.get("bpm", 120.0)
            tempos.append({
                "tick_position": int(blick_to_tick(pos_blicks, blick_rate, ticks_per_q)),
                "bpm": bpm,
            })
        result["tempos"] = tempos if tempos else [{"tick_position": 0, "bpm": 120.0}]

        # Time signatures
        time_sigs: List[Dict[str, Any]] = []
        for m in song.get("timeSignature", []):
            pos_blicks = m.get("position", 0)
            num = m.get("numerator", 4)
            den = m.get("denominator", 4)
            time_sigs.append({
                "tick_position": int(blick_to_tick(pos_blicks, blick_rate, ticks_per_q)),
                "numerator": num,
                "denominator": den,
            })
        result["time_signatures"] = time_sigs if time_sigs else [
            {"measure_position": 0, "numerator": 4, "denominator": 4}
        ]

        # Tracks - in .s5p, tracks directly contain notes
        tracks: List[Dict[str, Any]] = []
        total_notes = 0

        for track_idx, track in enumerate(song.get("tracks", [])):
            track_name = track.get("name", f"Track {track_idx + 1}")
            track_info: Dict[str, Any] = {
                "index": track_idx,
                "name": track_name,
                "notes": [],
            }

            # Default singer
            db_defaults = track.get("dbDefaults", {})
            if db_defaults:
                track_info["singer"] = db_defaults.get("name", "")
                track_info["language"] = db_defaults.get("language", "")

            # Notes directly in track
            for note in track.get("notes", []):
                onset = note.get("onset", 0)
                duration = note.get("duration", 0)
                pitch = note.get("pitch", 60)
                detune = note.get("detune", 0.0)
                lyrics = note.get("lyrics", "")
                phonemes = note.get("phonemes", "")

                tick_on = int(blick_to_tick(onset, blick_rate, ticks_per_q))
                tick_off = int(blick_to_tick(onset + duration, blick_rate, ticks_per_q))

                note_info: Dict[str, Any] = {
                    "tick_on": tick_on,
                    "tick_off": tick_off,
                    "pitch": pitch,
                    "detune": detune,
                    "lyric": lyrics,
                    "phoneme": phonemes,
                }

                # Attributes
                attributes = note.get("attributes", {})
                if attributes:
                    attrs: Dict[str, Any] = {}
                    for key in ["tF0Offset", "tF0Left", "tF0Right", "dF0Left", "dF0Right",
                                 "tF0VbrStart", "tF0VbrLeft", "tF0VbrRight", "dF0Vbr",
                                 "pF0Vbr", "fF0Vbr", "tNoteOffset", "dur", "alt"]:
                        if key in attributes:
                            attrs[key] = attributes[key]
                    if attrs:
                        note_info["attributes"] = attrs

                track_info["notes"].append(note_info)
                total_notes += 1

            # Parameters directly in track
            parameters = track.get("parameters", {})
            if parameters:
                params: Dict[str, Any] = {}
                for param_name, param_data in parameters.items():
                    if isinstance(param_data, dict) and "points" in param_data:
                        points = param_data["points"]
                        mode = param_data.get("mode", "linear")
                        params[param_name] = {
                            "mode": mode,
                            "point_count": len(points),
                        }
                    elif isinstance(param_data, list):
                        # Some .s5p files have flat point lists
                        params[param_name] = {
                            "type": "flat_list",
                            "point_count": len(param_data),
                        }
                if params:
                    track_info["parameters"] = params

            tracks.append(track_info)

        result["tracks"] = tracks
        result["track_count"] = len(tracks)
        result["total_notes"] = total_notes

        return result
