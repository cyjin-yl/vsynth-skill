"""
Synthesizer V .svp (JSON) 文件解析器。
使用 blick 时间单位 (1 blick = 1/1470000 beat)。
支持版本 1 (SVS1) 和版本 2 (SVS2)。
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_parser import BaseParser
from .utils import blick_to_tick, midi_note_name, safe_get


class SvpParser(BaseParser):
    """Synthesizer V SVP (JSON) 文件解析器。"""

    SUPPORTED_EXTENSIONS = [".svp"]
    FORMAT_NAME = "Synthesizer V SVP"

    # 1 blick = 1/1470000 beat (UtaFormatix uses this)
    # 1 blick = 1/705600000 beat (Dreamtonics docs)
    # We'll support both but default to 1470000 for compatibility
    DEFAULT_BLICKS_PER_BEAT = 1470000
    TICKS_PER_QUARTER = 480

    def _load_svp(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        加载 SVP 文件。

        SVP 文件可能包含多个以 NUL 字符分隔的 JSON 对象（自动保存历史）。
        我们取 version 号最大的那个。
        """
        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = file_path.read_text(encoding="utf-16")

        # Split on NUL characters
        parts = text.split("\x00")
        projects = []

        for part in parts:
            part = part.strip()
            if not part:
                continue
            try:
                obj = json.loads(part)
                if isinstance(obj, dict):
                    projects.append(obj)
            except json.JSONDecodeError:
                continue

        if not projects:
            return None

        # Take the project with highest version number
        return max(projects, key=lambda p: p.get("version", 0))

    def validate(self, file_path: Path) -> tuple[bool, List[str]]:
        """验证 SVP 文件。"""
        errors: List[str] = []

        try:
            project = self._load_svp(file_path)
        except Exception as e:
            return False, [f"Cannot parse file: {e}"]

        if project is None:
            errors.append("No valid JSON project found")
            return False, errors

        if "version" not in project:
            errors.append("Missing 'version' field")
        if "timeAxis" not in project:
            errors.append("Missing 'timeAxis' field")
        if "tracks" not in project:
            errors.append("Missing 'tracks' field")

        # Check library exists for v2
        version = project.get("version", 1)
        if version >= 2 and "library" not in project:
            errors.append("Missing 'library' field (required for version 2+)")

        return len(errors) == 0, errors

    def info(self, file_path: Path) -> Dict[str, Any]:
        """提取 SVP 文件信息。"""
        project = self._load_svp(file_path)
        if project is None:
            raise ValueError("Cannot parse SVP file: no valid JSON project found")

        version = project.get("version", 1)
        blick_rate = self.DEFAULT_BLICKS_PER_BEAT
        ticks_per_q = self.TICKS_PER_QUARTER

        result: Dict[str, Any] = {
            "format": f"Synthesizer V SVP (version {version})",
            "file_name": file_path.name,
            "version": version,
            "blick_rate": blick_rate,
            "ticks_per_quarter": ticks_per_q,
        }

        # Parse timeAxis
        time_axis = project.get("timeAxis", {})

        # Tempos
        tempos: List[Dict[str, Any]] = []
        for tp in time_axis.get("tempo", []):
            pos_blicks = tp.get("position", 0)
            bpm = tp.get("beatPerMinute", 120.0)
            tempos.append({
                "tick_position": int(blick_to_tick(pos_blicks, blick_rate, ticks_per_q)),
                "bpm": bpm,
            })
        result["tempos"] = tempos if tempos else [{"tick_position": 0, "bpm": 120.0}]

        # Time signatures
        time_sigs: List[Dict[str, Any]] = []
        for m in time_axis.get("measure", []):
            pos_blicks = m.get("position", 0)
            num = m.get("numerator", 4)
            den = m.get("denominator", 4)
            time_sigs.append({
                "tick_position": int(blick_to_tick(pos_blicks, blick_rate, ticks_per_q)),
                "measure_position": None,  # SVP doesn't use measure positions directly
                "numerator": num,
                "denominator": den,
            })
        result["time_signatures"] = time_sigs if time_sigs else [
            {"measure_position": 0, "numerator": 4, "denominator": 4}
        ]

        # Parse library (NoteGroups) for v2
        library = {g.get("uuid", ""): g for g in project.get("library", [])}

        # Parse tracks
        tracks: List[Dict[str, Any]] = []
        total_notes = 0

        for track_idx, track in enumerate(project.get("tracks", [])):
            track_name = track.get("name", f"Track {track_idx + 1}")
            track_info: Dict[str, Any] = {
                "index": track_idx,
                "name": track_name,
                "display_order": track.get("displayOrder", track_idx),
                "color": track.get("color", ""),
                "notes": [],
            }

            # Default singer
            db_defaults = track.get("dbDefaults", {})
            if db_defaults:
                track_info["singer"] = db_defaults.get("name", "")
                track_info["language"] = db_defaults.get("language", "")
                track_info["phoneset"] = db_defaults.get("phoneset", "")

            # Mixer
            mixer = track.get("mixer", {})
            if mixer:
                track_info["mixer"] = {
                    "gain": mixer.get("gain", 0),
                    "pan": mixer.get("pan", 0),
                    "mute": mixer.get("mute", False),
                    "solo": mixer.get("solo", False),
                }

            # Parse notes from groups
            for group_ref in track.get("groups", []):
                group_id = group_ref.get("groupID", "")
                time_offset = group_ref.get("timeOffset", 0)
                pitch_offset = group_ref.get("pitchOffset", 0)

                # Find the group in library
                group = library.get(group_id)
                if group is None:
                    continue

                for note in group.get("notes", []):
                    onset = note.get("onset", 0)
                    duration = note.get("duration", 0)
                    pitch = note.get("pitch", 60)
                    detune = note.get("detune", 0.0)
                    lyrics = note.get("lyrics", "")
                    phonemes = note.get("phonemes", "")

                    tick_on = int(blick_to_tick(onset + time_offset, blick_rate, ticks_per_q))
                    tick_off = int(blick_to_tick(onset + time_offset + duration, blick_rate, ticks_per_q))

                    note_info: Dict[str, Any] = {
                        "tick_on": tick_on,
                        "tick_off": tick_off,
                        "pitch": pitch + pitch_offset,
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
                                     "pF0Vbr", "fF0Vbr", "tNoteOffset", "dF0VbrMod",
                                     "expValueX", "expValueY", "muted", "evenSyllableDuration",
                                     "musicalType", "rTone", "rIntonation"]:
                            if key in attributes:
                                attrs[key] = attributes[key]
                        if attrs:
                            note_info["attributes"] = attrs

                    track_info["notes"].append(note_info)
                    total_notes += 1

                # Parameters from group
                parameters = group.get("parameters", {})
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
                    if params:
                        track_info["parameters"] = params

                # Pitch controls
                pitch_controls = group.get("pitchControls", [])
                if pitch_controls:
                    track_info["pitch_control_count"] = len(pitch_controls)

            tracks.append(track_info)

        result["tracks"] = tracks
        result["track_count"] = len(tracks)
        result["total_notes"] = total_notes

        # Render config
        render_config = project.get("renderConfig", {})
        if render_config:
            result["render_config"] = {
                "destination": render_config.get("destination", ""),
                "file_name": render_config.get("fileName", ""),
            }

        return result
