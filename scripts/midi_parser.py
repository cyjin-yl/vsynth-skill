"""
标准 MIDI 文件 (.mid) 解析器。
解析 SMF Format 0/1，提取曲速、拍号、音符。
"""

import struct
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .base_parser import BaseParser
from .utils import midi_note_name


class MidiParser(BaseParser):
    """标准 MIDI 文件 (SMF) 解析器。"""

    SUPPORTED_EXTENSIONS = [".mid", ".midi"]
    FORMAT_NAME = "Standard MIDI File"

    def _read_variable_length(self, f: BytesIO) -> int:
        """读取 MIDI 可变长度值。"""
        result = 0
        while True:
            byte = f.read(1)
            if not byte:
                raise ValueError("Unexpected end of file")
            value = byte[0]
            result = (result << 7) | (value & 0x7F)
            if not (value & 0x80):
                break
        return result

    def _parse_midi_meta_event(self, f: BytesIO) -> Tuple[int, bytes]:
        """解析 MIDI Meta Event。"""
        meta_type_byte = f.read(1)
        if not meta_type_byte:
            raise ValueError("Unexpected end of file")
        meta_type = meta_type_byte[0]
        length = self._read_variable_length(f)
        data = f.read(length)
        return meta_type, data

    def _parse_midi(self, file_path: Path) -> Dict[str, Any]:
        """解析 MIDI 文件并返回结构化数据。"""
        data = file_path.read_bytes()
        f = BytesIO(data)

        header = f.read(4)
        if header != b"MThd":
            raise ValueError("Not a valid MIDI file (missing MThd header)")

        header_length = struct.unpack(">I", f.read(4))[0]
        if header_length != 6:
            raise ValueError(f"Unexpected MIDI header length: {header_length}")

        format_type = struct.unpack(">H", f.read(2))[0]
        num_tracks = struct.unpack(">H", f.read(2))[0]
        division = struct.unpack(">H", f.read(2))[0]

        # Determine ticks per quarter
        if division & 0x8000:
            # SMPTE timecode
            frames_per_second = -(division >> 8) & 0x7F
            ticks_per_frame = division & 0xFF
            ticks_per_quarter = frames_per_second * ticks_per_frame
        else:
            ticks_per_quarter = division

        tracks_data: List[Dict[str, Any]] = []
        all_tempos: List[Dict[str, Any]] = []
        all_time_sigs: List[Dict[str, Any]] = []

        for track_idx in range(num_tracks):
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
            track_name = ""
            notes: List[Dict[str, Any]] = []
            current_note_on: Dict[int, Tuple[int, int]] = {}  # channel -> (tick, velocity)

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
                    if meta_type == 0x03 and meta_data:
                        try:
                            track_name = meta_data.decode("utf-8", errors="replace")
                        except Exception:
                            track_name = ""
                    elif meta_type == 0x51 and len(meta_data) == 3:
                        micros = struct.unpack(">I", b"\x00" + meta_data)[0]
                        bpm = 60000000.0 / micros
                        all_tempos.append({
                            "tick_position": tick_pos,
                            "bpm": round(bpm, 2),
                        })
                    elif meta_type == 0x58 and len(meta_data) >= 4:
                        num = meta_data[0]
                        den = 2 ** meta_data[1]
                        all_time_sigs.append({
                            "tick_position": tick_pos,
                            "numerator": num,
                            "denominator": den,
                        })
                    elif meta_type == 0x2F:
                        break
                elif 0x80 <= status <= 0x8F:
                    # Note Off
                    channel = status & 0x0F
                    note_num = f.read(1)[0] if f.read(1) else 0
                    f.seek(1, 1)  # velocity
                    if note_num in current_note_on:
                        start_tick, velocity = current_note_on.pop(note_num)
                        notes.append({
                            "tick_on": start_tick,
                            "tick_off": tick_pos,
                            "pitch": note_num,
                            "velocity": velocity,
                            "lyric": "",
                        })
                elif 0x90 <= status <= 0x9F:
                    # Note On
                    channel = status & 0x0F
                    note_num = f.read(1)[0] if f.read(1) else 0
                    vel_byte = f.read(1)
                    velocity = vel_byte[0] if vel_byte else 0
                    if velocity == 0:
                        # Note Off
                        if note_num in current_note_on:
                            start_tick, vel_on = current_note_on.pop(note_num)
                            notes.append({
                                "tick_on": start_tick,
                                "tick_off": tick_pos,
                                "pitch": note_num,
                                "velocity": vel_on,
                                "lyric": "",
                            })
                    else:
                        current_note_on[note_num] = (tick_pos, velocity)
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

            # Close any remaining note-on events
            for note_num, (start_tick, velocity) in current_note_on.items():
                notes.append({
                    "tick_on": start_tick,
                    "tick_off": tick_pos,
                    "pitch": note_num,
                    "velocity": velocity,
                    "lyric": "",
                })

            if notes or track_name:
                tracks_data.append({
                    "index": track_idx,
                    "name": track_name or f"Track {track_idx + 1}",
                    "notes": notes,
                })

        return {
            "format_type": format_type,
            "num_tracks": num_tracks,
            "ticks_per_quarter": ticks_per_quarter,
            "tempos": all_tempos,
            "time_signatures": all_time_sigs,
            "tracks": tracks_data,
        }

    def validate(self, file_path: Path) -> tuple[bool, List[str]]:
        """验证 MIDI 文件。"""
        errors: List[str] = []

        try:
            data = file_path.read_bytes()
        except Exception as e:
            return False, [f"Cannot read file: {e}"]

        if len(data) < 14 or data[:4] != b"MThd":
            errors.append("Not a valid MIDI file (missing MThd header)")
            return False, errors

        try:
            header_length = struct.unpack(">I", data[4:8])[0]
            if header_length != 6:
                errors.append(f"Unexpected MIDI header length: {header_length}")

            format_type = struct.unpack(">H", data[8:10])[0]
            if format_type not in (0, 1, 2):
                errors.append(f"Unknown MIDI format type: {format_type}")
        except Exception as e:
            errors.append(f"Cannot parse MIDI header: {e}")

        return len(errors) == 0, errors

    def info(self, file_path: Path) -> Dict[str, Any]:
        """提取 MIDI 文件信息。"""
        midi_data = self._parse_midi(file_path)

        total_notes = sum(len(t["notes"]) for t in midi_data.get("tracks", []))

        result: Dict[str, Any] = {
            "format": f"Standard MIDI File (Format {midi_data['format_type']})",
            "file_name": file_path.name,
            "format_type": midi_data["format_type"],
            "num_tracks": midi_data["num_tracks"],
            "ticks_per_quarter": midi_data["ticks_per_quarter"],
            "tempos": midi_data["tempos"],
            "time_signatures": midi_data["time_signatures"],
            "tracks": midi_data["tracks"],
            "track_count": len(midi_data["tracks"]),
            "total_notes": total_notes,
        }

        # Default tempo if none found
        if not result["tempos"]:
            result["tempos"] = [{"tick_position": 0, "bpm": 120.0}]

        # Default time signature if none found
        if not result["time_signatures"]:
            result["time_signatures"] = [
                {"tick_position": 0, "numerator": 4, "denominator": 4}
            ]

        return result
