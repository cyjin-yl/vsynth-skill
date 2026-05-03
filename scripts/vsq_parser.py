"""
VOCALOID .vsq (SMF MIDI + INI) 文件解析器。
基于 Standard MIDI File Format 1，声乐数据以 INI 格式存储在 MIDI Text Meta Event 中。
"""

import struct
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .base_parser import BaseParser
from .utils import detect_encoding, midi_note_name, parse_ini_style_text


class VsqParser(BaseParser):
    """VOCALOID 2 VSQ (SMF + INI) 文件解析器。"""

    SUPPORTED_EXTENSIONS = [".vsq"]
    FORMAT_NAME = "VOCALOID VSQ"

    def _read_variable_length(self, f: BytesIO) -> int:
        """读取 MIDI 可变长度值。"""
        result = 0
        while True:
            byte = f.read(1)
            if not byte:
                raise ValueError("Unexpected end of file reading variable length value")
            value = byte[0]
            result = (result << 7) | (value & 0x7F)
            if not (value & 0x80):
                break
        return result

    def _parse_midi_meta_event(self, f: BytesIO) -> Tuple[int, bytes]:
        """
        解析 MIDI Meta Event。

        Returns:
            (meta_type, data)
        """
        meta_type_byte = f.read(1)
        if not meta_type_byte:
            raise ValueError("Unexpected end of file")
        meta_type = meta_type_byte[0]
        length = self._read_variable_length(f)
        data = f.read(length)
        return meta_type, data

    def _parse_vsq_ini(self, file_path: Path) -> str:
        """
        从 VSQ 文件的 MIDI Text Meta Events 中提取并拼接 INI 数据。

        VSQ 中的 INI 数据被分割成多个 Text Meta Event，每段有 DM:NNNN: 前缀。
        """
        data = file_path.read_bytes()
        f = BytesIO(data)

        # Skip MIDI header (MThd + 10 bytes)
        header = f.read(4)
        if header != b"MThd":
            raise ValueError("Not a valid MIDI file (missing MThd header)")
        f.read(10)  # length (4) + format (2) + tracks (2) + division (2)

        ini_parts: Dict[int, str] = {}

        # Read tracks
        track_idx = 0
        while f.tell() < len(data) and track_idx < 2:
            track_header = f.read(4)
            if len(track_header) < 4:
                break
            if track_header != b"MTrk":
                # Skip unknown chunk
                length = struct.unpack(">I", f.read(4))[0]
                f.seek(length, 1)
                continue

            track_length = struct.unpack(">I", f.read(4))[0]
            track_end = f.tell() + track_length

            while f.tell() < track_end:
                # Read delta time
                try:
                    delta_time = self._read_variable_length(f)
                except ValueError:
                    break

                status_byte = f.read(1)
                if not status_byte:
                    break
                status = status_byte[0]

                # Running status - not expected for meta events but handle anyway
                if status == 0xFF:
                    # Meta event
                    meta_type, meta_data = self._parse_midi_meta_event(f)
                    if meta_type == 0x01:
                        # Text Meta Event - may contain INI data
                        try:
                            text = meta_data.decode("shift_jis", errors="replace")
                            if text.startswith("DM:"):
                                # Extract part number
                                parts = text.split(":", 2)
                                if len(parts) >= 3:
                                    try:
                                        part_num = int(parts[1])
                                        ini_parts[part_num] = parts[2]
                                    except ValueError:
                                        pass
                        except Exception:
                            pass
                    elif meta_type == 0x2F:
                        # End of track
                        break
                    elif meta_type == 0x51:
                        # Set Tempo - skip 3 bytes
                        pass
                    elif meta_type == 0x58:
                        # Time Signature - skip 4 bytes
                        pass
                    elif meta_type == 0x03:
                        # Sequence/Track Name
                        pass
                elif status == 0x00:
                    # Not a valid status, try to recover
                    pass
                else:
                    # Other MIDI events - skip based on status
                    if 0x80 <= status <= 0x8F:
                        # Note Off - 2 bytes
                        f.read(2)
                    elif 0x90 <= status <= 0x9F:
                        # Note On - 2 bytes
                        f.read(2)
                    elif 0xA0 <= status <= 0xAF:
                        # Polyphonic Key Pressure - 2 bytes
                        f.read(2)
                    elif 0xB0 <= status <= 0xBF:
                        # Control Change - 2 bytes
                        f.read(2)
                    elif 0xC0 <= status <= 0xCF:
                        # Program Change - 1 byte
                        f.read(1)
                    elif 0xD0 <= status <= 0xDF:
                        # Channel Pressure - 1 byte
                        f.read(1)
                    elif 0xE0 <= status <= 0xEF:
                        # Pitch Bend - 2 bytes
                        f.read(2)
                    elif status == 0xF0 or status == 0xF7:
                        # SysEx - variable length
                        self._read_variable_length(f)

            track_idx += 1

        # Reassemble INI text
        if not ini_parts:
            return ""

        sorted_parts = [ini_parts[k] for k in sorted(ini_parts.keys())]
        # Join with newline to ensure section boundaries are preserved
        ini_text = "\n".join(p.rstrip("\n") for p in sorted_parts)
        return ini_text

    def _parse_midi_info(self, file_path: Path) -> Dict[str, Any]:
        """解析 MIDI 基本信息（曲速、拍号等）。"""
        data = file_path.read_bytes()
        f = BytesIO(data)

        header = f.read(4)
        if header != b"MThd":
            return {}

        header_length = struct.unpack(">I", f.read(4))[0]
        if header_length != 6:
            return {}

        format_type = struct.unpack(">H", f.read(2))[0]
        num_tracks = struct.unpack(">H", f.read(2))[0]
        division = struct.unpack(">H", f.read(2))[0]

        # Check if SMPTE timecode
        if division & 0x8000:
            # SMPTE format - not typical for VSQ
            ticks_per_quarter = 480
        else:
            ticks_per_quarter = division

        tempos: List[Dict[str, Any]] = []
        time_sigs: List[Dict[str, Any]] = []

        for _ in range(num_tracks):
            track_header = f.read(4)
            if len(track_header) < 4:
                break
            if track_header != b"MTrk":
                # Skip unknown chunk
                chunk_length = struct.unpack(">I", f.read(4))[0]
                f.seek(chunk_length, 1)
                continue

            track_length = struct.unpack(">I", f.read(4))[0]
            track_end = f.tell() + track_length
            tick_pos = 0

            while f.tell() < track_end:
                try:
                    delta = self._read_variable_length(f)
                except ValueError:
                    break
                tick_pos += delta

                status_byte = f.read(1)
                if not status_byte:
                    break
                status = status_byte[0]

                if status == 0xFF:
                    meta_type, meta_data = self._parse_midi_meta_event(f)
                    if meta_type == 0x51 and len(meta_data) == 3:
                        # Set Tempo
                        micros = struct.unpack(">I", b"\x00" + meta_data)[0]
                        bpm = 60000000.0 / micros
                        tempos.append({"tick_position": tick_pos, "bpm": round(bpm, 2)})
                    elif meta_type == 0x58 and len(meta_data) == 4:
                        # Time Signature
                        num = meta_data[0]
                        den = 2 ** meta_data[1]
                        time_sigs.append({
                            "tick_position": tick_pos,
                            "numerator": num,
                            "denominator": den,
                        })
                    elif meta_type == 0x2F:
                        break
                elif 0x80 <= status <= 0xEF:
                    # Skip regular MIDI events
                    if 0x80 <= status <= 0x8F:
                        f.read(2)
                    elif 0x90 <= status <= 0x9F:
                        f.read(2)
                    elif 0xA0 <= status <= 0xAF:
                        f.read(2)
                    elif 0xB0 <= status <= 0xBF:
                        f.read(2)
                    elif 0xC0 <= status <= 0xCF:
                        f.read(1)
                    elif 0xD0 <= status <= 0xDF:
                        f.read(1)
                    elif 0xE0 <= status <= 0xEF:
                        f.read(2)
                elif status == 0xF0 or status == 0xF7:
                    self._read_variable_length(f)

        return {
            "format_type": format_type,
            "num_tracks": num_tracks,
            "ticks_per_quarter": ticks_per_quarter,
            "tempos": tempos,
            "time_signatures": time_sigs,
        }

    def validate(self, file_path: Path) -> tuple[bool, List[str]]:
        """验证 VSQ 文件。"""
        errors: List[str] = []

        try:
            data = file_path.read_bytes()
        except Exception as e:
            return False, [f"Cannot read file: {e}"]

        # Check MIDI header
        if len(data) < 14 or data[:4] != b"MThd":
            errors.append("Not a valid MIDI file (missing MThd header)")
            return False, errors

        # Check format type (should be 1 for SMF Format 1)
        try:
            format_type = struct.unpack(">H", data[8:10])[0]
            if format_type != 1:
                errors.append(f"Unexpected MIDI format type {format_type} (expected 1)")
        except Exception:
            pass

        # Try to extract INI data
        try:
            ini_text = self._parse_vsq_ini(file_path)
            if not ini_text:
                errors.append("No INI data found in MIDI Text Meta Events")
            else:
                # Check for required sections
                if "[Common]" not in ini_text:
                    errors.append("Missing [Common] section in INI data")
                if "[EventList]" not in ini_text:
                    errors.append("Missing [EventList] section in INI data")
        except Exception as e:
            errors.append(f"Failed to parse INI data: {e}")

        return len(errors) == 0, errors

    def info(self, file_path: Path) -> Dict[str, Any]:
        """提取 VSQ 文件信息。"""
        midi_info = self._parse_midi_info(file_path)
        ini_text = self._parse_vsq_ini(file_path)
        ini_data = parse_ini_style_text(ini_text) if ini_text else {}

        result: Dict[str, Any] = {
            "format": "VOCALOID VSQ (SMF + INI)",
            "file_name": file_path.name,
            "midi_format_type": midi_info.get("format_type", 0),
            "midi_num_tracks": midi_info.get("num_tracks", 0),
            "ticks_per_quarter": midi_info.get("ticks_per_quarter", 480),
            "tempos": midi_info.get("tempos", []),
            "time_signatures": midi_info.get("time_signatures", []),
        }

        # Parse Common section
        common = ini_data.get("Common", {})
        result["version"] = common.get("Version", "")
        result["track_name"] = common.get("Name", "")
        result["color"] = common.get("Color", "")

        # Parse EventList to count events
        event_list = ini_data.get("EventList", {})
        notes: List[Dict[str, Any]] = []
        singers: List[Dict[str, Any]] = []

        for tick_str, event_id in event_list.items():
            try:
                tick = int(tick_str)
            except ValueError:
                continue

            if event_id.startswith("ID#"):
                event_data = ini_data.get(event_id, {})
                event_type = event_data.get("Type", "")

                if event_type == "Anote":
                    try:
                        length = int(event_data.get("Length", "0"))
                        note_num = int(event_data.get("Note#", "60"))
                        dynamics = int(event_data.get("Dynamics", "64"))
                        lyric_handle = event_data.get("LyricHandle", "")
                        lyric = ""
                        if lyric_handle.startswith("h#"):
                            lyric_data = ini_data.get(lyric_handle, {})
                            l0 = lyric_data.get("L0", "")
                            if l0:
                                parts = l0.split(",")
                                if parts:
                                    lyric = parts[0].strip('"')
                        notes.append({
                            "tick_on": tick,
                            "tick_off": tick + length,
                            "pitch": note_num,
                            "lyric": lyric,
                            "dynamics": dynamics,
                        })
                    except (ValueError, KeyError):
                        pass

                elif event_type == "Singer":
                    icon_handle = event_data.get("IconHandle", "")
                    if icon_handle.startswith("h#"):
                        icon_data = ini_data.get(icon_handle, {})
                        singer_name = icon_data.get("IDS", "")
                        icon_id = icon_data.get("IconID", "")
                        singers.append({
                            "tick_position": tick,
                            "name": singer_name,
                            "icon_id": icon_id,
                        })

        # Parse Master section for tempo override (if any)
        # (VSQ 的 tempo 主要在 Master Track 的 MIDI Meta Event 中)

        result["tracks"] = [{
            "index": 0,
            "name": result.get("track_name", "Track 1"),
            "notes": notes,
        }]
        result["total_notes"] = len(notes)
        result["singers"] = singers

        return result
