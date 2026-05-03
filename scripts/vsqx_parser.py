"""
VOCALOID .vsqx (XML) 文件解析器。
支持 VOCALOID 3 (vsq3 命名空间) 和 VOCALOID 4 (vsq4 命名空间)。
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_parser import BaseParser
from .utils import safe_get


class VsqxParser(BaseParser):
    """VOCALOID 3/4 VSQX (XML) 文件解析器。"""

    SUPPORTED_EXTENSIONS = [".vsqx"]
    FORMAT_NAME = "VOCALOID VSQX"

    # 命名空间映射
    VSQ3_NS = "http://www.yamaha.co.jp/vocaloid/schema/vsq3/"
    VSQ4_NS = "http://www.yamaha.co.jp/vocaloid/schema/vsq4/"

    def _get_ns_prefix(self, namespace: str) -> str:
        """获取命名空间前缀。"""
        return f"{{{namespace}}}"

    def _detect_version(self, root: ET.Element) -> tuple[str, str]:
        """
        检测 VSQX 版本。

        Returns:
            (version_label, namespace) 例如 ("vsq4", "http://.../vsq4/")
        """
        tag = root.tag
        if tag.startswith("{"):
            # Has namespace
            ns = tag.split("}")[0].strip("{")
            if "vsq4" in ns:
                return ("vsq4", ns)
            elif "vsq3" in ns:
                return ("vsq3", ns)
        else:
            if tag == "vsq4":
                return ("vsq4", "")
            elif tag == "vsq3":
                return ("vsq3", "")
        return ("unknown", "")

    def _find_child_text(self, parent: ET.Element, tag: str, ns_prefix: str, default: str = "") -> str:
        """查找子元素并返回文本内容。"""
        child = parent.find(f"{ns_prefix}{tag}")
        return child.text if child is not None and child.text is not None else default

    def _find_child_int(self, parent: ET.Element, tag: str, ns_prefix: str, default: int = 0) -> int:
        """查找子元素并返回整数。"""
        text = self._find_child_text(parent, tag, ns_prefix, "")
        if text:
            try:
                return int(text)
            except ValueError:
                pass
        return default

    def validate(self, file_path: Path) -> tuple[bool, List[str]]:
        """
        验证 VSQX 文件。

        检查项目:
        1. 是否为有效的 XML
        2. 根元素是否为 vsq3 或 vsq4
        3. 是否包含必需的子元素
        """
        errors: List[str] = []

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except ET.ParseError as e:
            return False, [f"Invalid XML: {e}"]
        except Exception as e:
            return False, [f"Cannot read file: {e}"]

        version, ns = self._detect_version(root)
        if version == "unknown":
            errors.append("Root element is not vsq3 or vsq4")
            return False, errors

        ns_prefix = self._get_ns_prefix(ns) if ns else ""

        # Check for required elements
        vender = self._find_child_text(root, "vender", ns_prefix)
        if not vender:
            errors.append("Missing or empty <vender> element")

        version_elem = self._find_child_text(root, "version", ns_prefix)
        if not version_elem:
            errors.append("Missing or empty <version> element")

        master_track = root.find(f"{ns_prefix}masterTrack")
        if master_track is None:
            errors.append("Missing <masterTrack> element")

        vs_tracks = root.findall(f"{ns_prefix}vsTrack")
        if not vs_tracks:
            errors.append("No <vsTrack> elements found (no vocal tracks)")

        return len(errors) == 0, errors

    def info(self, file_path: Path) -> Dict[str, Any]:
        """
        提取 VSQX 文件信息。

        返回信息包括:
        - format: 格式名称和版本
        - vendor: 厂商
        - version: 文件格式版本
        - resolution: 时间分辨率 (tick/四分音符)
        - pre_measure: 前置小节数
        - time_signatures: 拍号列表
        - tempos: 曲速列表
        - tracks: 轨道列表（包含音符信息）
        - total_notes: 总音符数
        - singers: 歌手列表
        """
        tree = ET.parse(file_path)
        root = tree.getroot()

        version, ns = self._detect_version(root)
        ns_prefix = self._get_ns_prefix(ns) if ns else ""
        is_vsq4 = version == "vsq4"

        result: Dict[str, Any] = {
            "format": f"VOCALOID VSQX ({version.upper()})",
            "file_name": file_path.name,
            "version": self._find_child_text(root, "version", ns_prefix),
            "vendor": self._find_child_text(root, "vender", ns_prefix),
        }

        # Parse masterTrack
        master_track = root.find(f"{ns_prefix}masterTrack")
        if master_track is not None:
            resolution = self._find_child_int(master_track, "resolution", ns_prefix, 480)
            pre_measure = self._find_child_int(master_track, "preMeasure", ns_prefix, 1)
            result["resolution"] = resolution
            result["pre_measure"] = pre_measure

            # Time signatures
            time_sigs: List[Dict[str, Any]] = []
            ts_tag = "timeSig"
            pos_tag = "posMes" if not is_vsq4 else "m"
            num_tag = "nume" if not is_vsq4 else "nu"
            den_tag = "denomi" if not is_vsq4 else "de"

            for ts in master_track.findall(f"{ns_prefix}{ts_tag}"):
                time_sigs.append({
                    "measure_position": self._find_child_int(ts, pos_tag, ns_prefix),
                    "numerator": self._find_child_int(ts, num_tag, ns_prefix),
                    "denominator": self._find_child_int(ts, den_tag, ns_prefix),
                })
            result["time_signatures"] = time_sigs

            # Tempos
            tempos: List[Dict[str, Any]] = []
            tempo_tag = "tempo"
            t_tag = "t"
            v_tag = "v" if is_vsq4 else "bpm"

            for tp in master_track.findall(f"{ns_prefix}{tempo_tag}"):
                pos = self._find_child_int(tp, t_tag, ns_prefix)
                val_text = self._find_child_text(tp, v_tag, ns_prefix, "0")
                if is_vsq4:
                    bpm = int(val_text) / 100.0 if val_text else 120.0
                else:
                    try:
                        bpm = float(val_text)
                    except ValueError:
                        bpm = 120.0
                tempos.append({"tick_position": pos, "bpm": bpm})
            result["tempos"] = tempos

        # Parse tracks
        tracks: List[Dict[str, Any]] = []
        total_notes = 0
        singers: List[str] = []

        track_tag = "vsTrack"
        name_tag = "trackName" if not is_vsq4 else "name"
        part_tag = "musicalPart" if not is_vsq4 else "vsPart"
        part_pos_tag = "pos" if not is_vsq4 else "t"
        note_tag = "note"
        note_pos_tag = "t"
        dur_tag = "dur" if is_vsq4 else "duration"
        pitch_tag = "n" if is_vsq4 else "noteNum"
        lyric_tag = "y" if is_vsq4 else "lyric"
        phoneme_tag = "p" if is_vsq4 else "phnms"
        velocity_tag = "v" if is_vsq4 else "velocity"

        for track_idx, track in enumerate(root.findall(f"{ns_prefix}{track_tag}")):
            track_name = self._find_child_text(track, name_tag, ns_prefix, f"Track {track_idx + 1}")
            track_info: Dict[str, Any] = {
                "index": track_idx,
                "name": track_name,
                "notes": [],
            }

            for part in track.findall(f"{ns_prefix}{part_tag}"):
                part_pos = self._find_child_int(part, part_pos_tag, ns_prefix, 0)

                for note in part.findall(f"{ns_prefix}{note_tag}"):
                    note_pos = self._find_child_int(note, note_pos_tag, ns_prefix, 0)
                    duration = self._find_child_int(note, dur_tag, ns_prefix, 0)
                    pitch = self._find_child_int(note, pitch_tag, ns_prefix, 60)
                    lyric = self._find_child_text(note, lyric_tag, ns_prefix, "")
                    phoneme = self._find_child_text(note, phoneme_tag, ns_prefix, "")
                    velocity = self._find_child_int(note, velocity_tag, ns_prefix, 64)

                    track_info["notes"].append({
                        "tick_on": part_pos + note_pos,
                        "tick_off": part_pos + note_pos + duration,
                        "pitch": pitch,
                        "lyric": lyric,
                        "phoneme": phoneme,
                        "velocity": velocity,
                    })
                    total_notes += 1

            tracks.append(track_info)

        # Parse singers from vVoiceTable
        voice_table = root.find(f"{ns_prefix}vVoiceTable")
        if voice_table is not None:
            for voice in voice_table.findall(f"{ns_prefix}vVoice"):
                voice_name = self._find_child_text(voice, "vVoiceName", ns_prefix, "")
                if voice_name:
                    singers.append(voice_name)

        result["tracks"] = tracks
        result["track_count"] = len(tracks)
        result["total_notes"] = total_notes
        result["singers"] = singers

        return result
