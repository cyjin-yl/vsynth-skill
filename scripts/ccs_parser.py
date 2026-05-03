"""
CeVIO .ccs (XML) 文件解析器。
CeVIO Creative Studio / CeVIO AI / VoiSona 项目文件。
时间单位为 Clock (1 Clock = 1/2 tick)。
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_parser import BaseParser
from .utils import clock_to_tick, midi_note_name


class CcsParser(BaseParser):
    """CeVIO CCS (XML) 文件解析器。"""

    SUPPORTED_EXTENSIONS = [".ccs", ".ccst"]
    FORMAT_NAME = "CeVIO CCS"

    CLOCK_PER_TICK = 2

    def _find_child_text(self, parent: ET.Element, tag: str, default: str = "") -> str:
        """查找子元素并返回文本内容。"""
        # Try with namespace wildcard
        child = parent.find(f".//{tag}")
        if child is None:
            # Try with any namespace
            for elem in parent:
                if elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag == tag:
                    child = elem
                    break
        return child.text if child is not None and child.text is not None else default

    def _find_child_int(self, parent: ET.Element, tag: str, default: int = 0) -> int:
        """查找子元素并返回整数。"""
        text = self._find_child_text(parent, tag, "")
        if text:
            try:
                return int(text)
            except ValueError:
                pass
        return default

    def _find_child_float(self, parent: ET.Element, tag: str, default: float = 0.0) -> float:
        """查找子元素并返回浮点数。"""
        text = self._find_child_text(parent, tag, "")
        if text:
            try:
                return float(text)
            except ValueError:
                pass
        return default

    def _get_local_name(self, element: ET.Element) -> str:
        """获取元素的本地名称（去掉命名空间）。"""
        tag = element.tag
        if "}" in tag:
            return tag.split("}")[1]
        return tag

    def validate(self, file_path: Path) -> tuple[bool, List[str]]:
        """验证 CCS 文件。"""
        errors: List[str] = []

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except ET.ParseError as e:
            return False, [f"Invalid XML: {e}"]
        except Exception as e:
            return False, [f"Cannot read file: {e}"]

        root_name = self._get_local_name(root)
        if root_name != "CeVIOCreativeStudioProject":
            errors.append(f"Unexpected root element '{root_name}' (expected CeVIOCreativeStudioProject)")

        # Check for Units with Category="SingerSong"
        has_song = False
        for unit in root.iter():
            if self._get_local_name(unit) == "Unit":
                category = unit.get("Category", "")
                if category == "SingerSong":
                    has_song = True
                    break

        if not has_song:
            errors.append("No singing units found (Category='SingerSong')")

        return len(errors) == 0, errors

    def info(self, file_path: Path) -> Dict[str, Any]:
        """提取 CCS 文件信息。"""
        tree = ET.parse(file_path)
        root = tree.getroot()

        result: Dict[str, Any] = {
            "format": "CeVIO CCS",
            "file_name": file_path.name,
            "version": "",
        }

        # Get version from root attributes
        version = root.get("Version", "")
        if version:
            result["version"] = version

        tracks: List[Dict[str, Any]] = []
        total_notes = 0
        singers: List[str] = []
        all_tempos: List[Dict[str, Any]] = []
        all_time_sigs: List[Dict[str, Any]] = []

        # Find all Units with Category="SingerSong"
        for unit in root.iter():
            if self._get_local_name(unit) != "Unit":
                continue
            category = unit.get("Category", "")
            if category != "SingerSong":
                continue

            track_name = unit.get("Name", "")
            group = unit.get("Group", "")

            track_info: Dict[str, Any] = {
                "name": track_name,
                "group": group,
                "notes": [],
            }

            # Find Song element
            for song in unit:
                if self._get_local_name(song) != "Song":
                    continue

                # Parse tempo
                for tempo in song.iter():
                    if self._get_local_name(tempo) == "Tempo":
                        for sound in tempo.iter():
                            if self._get_local_name(sound) == "Sound":
                                clock = self._find_child_int(sound, "Clock", 0)
                                bpm = self._find_child_float(sound, "Tempo", 120.0)
                                all_tempos.append({
                                    "tick_position": int(clock_to_tick(clock, self.CLOCK_PER_TICK)),
                                    "bpm": round(bpm, 2),
                                })

                # Parse beat/time signature
                for beat in song.iter():
                    if self._get_local_name(beat) == "Beat":
                        for time_elem in beat.iter():
                            if self._get_local_name(time_elem) == "Time":
                                clock = self._find_child_int(time_elem, "Clock", 0)
                                beats = self._find_child_int(time_elem, "Beats", 4)
                                beat_type = self._find_child_int(time_elem, "BeatType", 4)
                                all_time_sigs.append({
                                    "tick_position": int(clock_to_tick(clock, self.CLOCK_PER_TICK)),
                                    "numerator": beats,
                                    "denominator": beat_type,
                                })

                # Parse score/notes
                for score in song.iter():
                    if self._get_local_name(score) != "Score":
                        continue

                    for note in score.iter():
                        if self._get_local_name(note) != "Note":
                            continue

                        clock = self._find_child_int(note, "Clock", 0)
                        duration = self._find_child_int(note, "Duration", 0)
                        pitch_step = self._find_child_int(note, "PitchStep", 0)
                        pitch_octave = self._find_child_int(note, "PitchOctave", 4)
                        lyric = self._find_child_text(note, "Lyric", "")
                        phonetic = self._find_child_text(note, "Phonetic", "")

                        # PitchStep: 0=C, 1=C#, 2=D, ... 11=B
                        # PitchOctave: CeVIO uses 1-based octave (C4 = PitchStep 0, PitchOctave 4)
                        midi_pitch = pitch_step + (pitch_octave - 1) * 12

                        tick_on = int(clock_to_tick(clock, self.CLOCK_PER_TICK))
                        tick_off = int(clock_to_tick(clock + duration, self.CLOCK_PER_TICK))

                        track_info["notes"].append({
                            "tick_on": tick_on,
                            "tick_off": tick_off,
                            "pitch": midi_pitch,
                            "lyric": lyric,
                            "phoneme": phonetic,
                        })
                        total_notes += 1

                # Parse parameters
                for param in song.iter():
                    if self._get_local_name(param) == "Parameter":
                        param_name = param.get("Id", "")
                        if param_name:
                            track_info.setdefault("parameters", {})[param_name] = {
                                "id": param_name,
                            }

            tracks.append(track_info)

        # Get singer info from CastId in units
        for cast in root.iter():
            if self._get_local_name(cast) == "CastId":
                cast_id = cast.text or ""
                if cast_id:
                    singers.append(cast_id)

        result["tracks"] = tracks
        result["track_count"] = len(tracks)
        result["total_notes"] = total_notes
        result["singers"] = singers

        # Use collected tempos/time signatures (or defaults)
        result["tempos"] = all_tempos if all_tempos else [{"tick_position": 0, "bpm": 120.0}]
        result["time_signatures"] = all_time_sigs if all_time_sigs else [
            {"measure_position": 0, "numerator": 4, "denominator": 4}
        ]

        return result
