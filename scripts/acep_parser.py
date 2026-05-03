"""
ACE Studio .acep (zstd + JSON) 文件解析器。
ACE Studio 1.7.8+ 版本使用 zstandard 压缩，无加密。
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_parser import BaseParser
from .utils import safe_get

# Try to import zstandard
try:
    import zstandard as zstd
    HAS_ZSTD = True
except ImportError:
    HAS_ZSTD = False


class AcepParser(BaseParser):
    """ACE Studio ACEP (zstd + JSON) 文件解析器。"""

    SUPPORTED_EXTENSIONS = [".acep"]
    FORMAT_NAME = "ACE Studio ACEP"

    def _decompress_acep(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        解压 ACEP 文件并解析 JSON。

        ACEP 1.7.8+ 文件格式:
        1. zstandard 压缩的 JSON 数据

        旧版本格式（1.7.8之前）:
        1. zstandard 压缩
        2. AES 加密
        3. base64 编码
        （旧版本需要额外解密步骤，本工具仅支持 1.7.8+）
        """
        if not HAS_ZSTD:
            raise ImportError("zstandard library not available. Install with: pip install zstandard")

        try:
            compressed_data = file_path.read_bytes()
        except Exception as e:
            raise ValueError(f"Cannot read file: {e}")

        # Try direct zstd decompression
        try:
            decompressor = zstd.ZstdDecompressor()
            decompressed = decompressor.decompress(compressed_data)
            text = decompressed.decode("utf-8", errors="replace")
            text = text.lstrip("\ufeff").replace("\x00", "")
            return json.loads(text)
        except (zstd.ZstdError, json.JSONDecodeError):
            pass

        # Try with stream reader (handles framing)
        try:
            decompressor = zstd.ZstdDecompressor()
            with decompressor.stream_reader(compressed_data) as reader:
                decompressed = reader.read()
            text = decompressed.decode("utf-8", errors="replace")
            text = text.lstrip("\ufeff").replace("\x00", "")
            return json.loads(text)
        except (zstd.ZstdError, json.JSONDecodeError, OSError):
            pass

        # Try with max_window_size (for large files)
        try:
            decompressor = zstd.ZstdDecompressor(max_window_size=2**31)
            decompressed = decompressor.decompress(compressed_data)
            text = decompressed.decode("utf-8", errors="replace")
            text = text.lstrip("\ufeff").replace("\x00", "")
            return json.loads(text)
        except (zstd.ZstdError, json.JSONDecodeError):
            pass

        return None

    def validate(self, file_path: Path) -> tuple[bool, List[str]]:
        """验证 ACEP 文件。"""
        errors: List[str] = []

        if not HAS_ZSTD:
            errors.append("zstandard library not installed. Run: pip install zstandard")
            return False, errors

        try:
            data = self._decompress_acep(file_path)
        except Exception as e:
            return False, [f"Cannot decompress/parse file: {e}"]

        if data is None:
            errors.append("Cannot decompress ACEP file (may be encrypted/old format, or not a valid zstd stream)")
            return False, errors

        if "project" not in data and "tracks" not in data:
            errors.append("Missing 'project' or 'tracks' field in JSON")

        return len(errors) == 0, errors

    def info(self, file_path: Path) -> Dict[str, Any]:
        """提取 ACEP 文件信息。"""
        data = self._decompress_acep(file_path)
        if data is None:
            raise ValueError("Cannot parse ACEP file: decompression failed or invalid format")

        # ACEP JSON structure can vary; handle different layouts
        project = data.get("project", data)

        result: Dict[str, Any] = {
            "format": "ACE Studio ACEP",
            "file_name": file_path.name,
            "version": data.get("version", project.get("version", "")),
            "name": project.get("name", project.get("title", "")),
        }

        # Tempos
        tempos: List[Dict[str, Any]] = []
        for tp in project.get("tempos", []):
            tempos.append({
                "tick_position": tp.get("position", 0),
                "bpm": tp.get("bpm", 120.0),
            })
        result["tempos"] = tempos if tempos else [{"tick_position": 0, "bpm": 120.0}]

        # Time signatures
        time_sigs: List[Dict[str, Any]] = []
        for ts in project.get("time_signatures", []):
            time_sigs.append({
                "measure_position": ts.get("bar", 0),
                "numerator": ts.get("numerator", 4),
                "denominator": ts.get("denominator", 4),
            })
        result["time_signatures"] = time_sigs if time_sigs else [
            {"measure_position": 0, "numerator": 4, "denominator": 4}
        ]

        # Tracks
        tracks: List[Dict[str, Any]] = []
        total_notes = 0

        for track_idx, track in enumerate(project.get("tracks", [])):
            track_name = track.get("name", f"Track {track_idx + 1}")
            track_info: Dict[str, Any] = {
                "index": track_idx,
                "name": track_name,
                "type": track.get("type", "vocal"),
                "notes": [],
            }

            # Singer info
            singer = track.get("singer", {})
            if singer:
                track_info["singer"] = singer.get("name", "")
                track_info["singer_id"] = singer.get("id", "")

            # Notes
            for note in track.get("notes", []):
                pos = note.get("position", 0)
                duration = note.get("duration", 480)
                pitch = note.get("pitch", 60)
                lyric = note.get("lyric", "")
                phoneme = note.get("phoneme", "")

                track_info["notes"].append({
                    "tick_on": pos,
                    "tick_off": pos + duration,
                    "pitch": pitch,
                    "lyric": lyric,
                    "phoneme": phoneme,
                })
                total_notes += 1

            # Parameters
            params = track.get("parameters", {})
            if params:
                track_info["parameters"] = {
                    k: {"count": len(v) if isinstance(v, list) else 0}
                    for k, v in params.items()
                }

            tracks.append(track_info)

        result["tracks"] = tracks
        result["track_count"] = len(tracks)
        result["total_notes"] = total_notes

        return result
