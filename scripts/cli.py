#!/usr/bin/env python3
"""
歌声合成工程文件 CLI 工具集。
支持验证、解析、提取、创建、生成等功能。

用法:
    python -m vsynth.scripts.cli validate <file> [--verbose]
    python -m vsynth.scripts.cli info <file>
    python -m vsynth.scripts.cli extract <file> --output <dir>
    python -m vsynth.scripts.cli list-formats
    python -m vsynth.scripts.cli detect <file>
    python -m vsynth.scripts.cli create --format ust --output <file>
    python -m vsynth.scripts.cli generate reclist --type cv --lang ja --output <file>
    python -m vsynth.scripts.cli generate oto --type cv --lang ja --output <file>
    python cli.py validate <file> [--verbose]
    python cli.py info <file>
    python cli.py extract <file> --output <dir>
    python cli.py list-formats
    python cli.py detect <file>
    python cli.py create --format ust --output <file>
    python cli.py generate reclist --type cv --lang ja --output <file>
    python cli.py generate oto --type cv --lang ja --output <file>
"""

import sys
from pathlib import Path

# Support both module execution and direct execution
if __name__ == "__main__" and __package__ is None:
    __package__ = "vsynth.scripts"
    sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import json
import zipfile
from typing import Any, Dict, List, Optional, Type

try:
    from .base_parser import BaseParser
    from .utils import detect_format, is_zip_file
    from .vsqx_parser import VsqxParser
    from .vsq_parser import VsqParser
    from .vpr_parser import VprParser
    from .ust_parser import UstParser
    from .ustx_parser import UstxParser
    from .svp_parser import SvpParser
    from .s5p_parser import S5pParser
    from .ccs_parser import CcsParser
    from .acep_parser import AcepParser
    from .midi_parser import MidiParser
except ImportError:
    # Allow direct execution: python cli.py
    from base_parser import BaseParser
    from utils import detect_format, is_zip_file
    from vsqx_parser import VsqxParser
    from vsq_parser import VsqParser
    from vpr_parser import VprParser
    from ust_parser import UstParser
    from ustx_parser import UstxParser
    from svp_parser import SvpParser
    from s5p_parser import S5pParser
    from ccs_parser import CcsParser
    from acep_parser import AcepParser
    from midi_parser import MidiParser

# Registry of all parsers
PARSER_REGISTRY: List[Type[BaseParser]] = [
    VsqxParser,
    VsqParser,
    VprParser,
    UstParser,
    UstxParser,
    SvpParser,
    S5pParser,
    CcsParser,
    AcepParser,
    MidiParser,
]


def get_parser_for_file(file_path: Path) -> Optional[BaseParser]:
    """根据文件扩展名获取对应的解析器实例。"""
    ext = file_path.suffix.lower()
    for parser_cls in PARSER_REGISTRY:
        if ext in [e.lower() for e in parser_cls.SUPPORTED_EXTENSIONS]:
            return parser_cls()
    return None


def get_parser_by_format(fmt: str) -> Optional[BaseParser]:
    """根据格式名称获取解析器实例。"""
    fmt_lower = fmt.lower()
    for parser_cls in PARSER_REGISTRY:
        for ext in parser_cls.SUPPORTED_EXTENSIONS:
            if ext.lower().lstrip(".") == fmt_lower:
                return parser_cls()
    return None


def output_json(data: Dict[str, Any], pretty: bool = True) -> None:
    """以 JSON 格式输出数据。"""
    if pretty:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(data, ensure_ascii=False))


def cmd_validate(args: argparse.Namespace) -> int:
    """验证命令。"""
    file_path = Path(args.file)

    if not file_path.exists():
        output_json({"success": False, "error": f"File not found: {file_path}"})
        return 1

    parser = get_parser_for_file(file_path)
    if parser is None:
        # Try auto-detect
        detected = detect_format(file_path)
        if detected:
            parser = get_parser_by_format(detected)

    if parser is None:
        output_json({
            "success": False,
            "error": f"Unsupported file format: {file_path.suffix}",
            "detected_format": detect_format(file_path),
        })
        return 1

    try:
        is_valid, errors = parser.validate(file_path)
    except Exception as e:
        output_json({
            "success": False,
            "format": parser.FORMAT_NAME,
            "error": str(e),
        })
        return 1

    result: Dict[str, Any] = {
        "success": is_valid,
        "format": parser.FORMAT_NAME,
        "file": str(file_path),
        "valid": is_valid,
        "errors": errors,
    }

    if args.verbose:
        try:
            info = parser.info(file_path)
            result["info_preview"] = {
                "version": info.get("version", ""),
                "track_count": info.get("track_count", info.get("tracks", 0)),
                "total_notes": info.get("total_notes", 0),
            }
        except Exception:
            pass

    output_json(result)
    return 0 if is_valid else 1


def cmd_info(args: argparse.Namespace) -> int:
    """提取信息命令。"""
    file_path = Path(args.file)

    if not file_path.exists():
        output_json({"success": False, "error": f"File not found: {file_path}"})
        return 1

    parser = get_parser_for_file(file_path)
    if parser is None:
        detected = detect_format(file_path)
        if detected:
            parser = get_parser_by_format(detected)

    if parser is None:
        output_json({
            "success": False,
            "error": f"Unsupported file format: {file_path.suffix}",
        })
        return 1

    try:
        info = parser.info(file_path)
        info["success"] = True
        info["format_name"] = parser.FORMAT_NAME
    except Exception as e:
        output_json({
            "success": False,
            "format": parser.FORMAT_NAME,
            "error": str(e),
        })
        return 1

    output_json(info)
    return 0


def cmd_extract(args: argparse.Namespace) -> int:
    """提取容器内容命令（vpr/acep）。"""
    file_path = Path(args.file)
    output_dir = Path(args.output)

    if not file_path.exists():
        output_json({"success": False, "error": f"File not found: {file_path}"})
        return 1

    ext = file_path.suffix.lower()

    if ext == ".vpr":
        if not is_zip_file(file_path):
            output_json({"success": False, "error": "Not a valid VPR (ZIP) file"})
            return 1

        output_dir.mkdir(parents=True, exist_ok=True)
        try:
            with zipfile.ZipFile(file_path, "r") as zf:
                zf.extractall(output_dir)
            output_json({
                "success": True,
                "format": "VPR",
                "extracted_to": str(output_dir),
                "files": zf.namelist(),
            })
        except Exception as e:
            output_json({"success": False, "error": str(e)})
            return 1

    elif ext == ".acep":
        # Extract zstd compressed JSON
        try:
            import zstandard as zstd
        except ImportError:
            output_json({
                "success": False,
                "error": "zstandard library not installed. Run: pip install zstandard",
            })
            return 1

        output_dir.mkdir(parents=True, exist_ok=True)
        try:
            compressed_data = file_path.read_bytes()
            decompressor = zstd.ZstdDecompressor()
            decompressed = decompressor.decompress(compressed_data)

            output_file = output_dir / "project.json"
            output_file.write_bytes(decompressed)

            output_json({
                "success": True,
                "format": "ACEP",
                "extracted_to": str(output_file),
                "original_size": len(compressed_data),
                "decompressed_size": len(decompressed),
            })
        except Exception as e:
            output_json({"success": False, "error": str(e)})
            return 1

    else:
        output_json({
            "success": False,
            "error": f"Extraction not supported for {ext} files",
        })
        return 1

    return 0


def cmd_list_formats(args: argparse.Namespace) -> int:
    """列出支持的格式。"""
    formats: List[Dict[str, Any]] = []
    for parser_cls in PARSER_REGISTRY:
        formats.append({
            "name": parser_cls.FORMAT_NAME,
            "extensions": parser_cls.SUPPORTED_EXTENSIONS,
        })

    output_json({
        "success": True,
        "formats": formats,
        "count": len(formats),
    })
    return 0


def cmd_detect(args: argparse.Namespace) -> int:
    """自动检测文件格式。"""
    file_path = Path(args.file)

    if not file_path.exists():
        output_json({"success": False, "error": f"File not found: {file_path}"})
        return 1

    detected = detect_format(file_path)
    parser = None
    if detected:
        parser = get_parser_by_format(detected)

    output_json({
        "success": True,
        "file": str(file_path),
        "detected_format": detected,
        "format_name": parser.FORMAT_NAME if parser else "Unknown",
        "can_parse": parser is not None,
    })
    return 0


# ============ 新增：创建与生成命令 ============

CREATE_TEMPLATES: Dict[str, str] = {
    "ust": """[#VERSION]
UST Version2.0
Charset=UTF-8
[#SETTING]
Tempo=120.00
Tracks=1
ProjectName=New Project
VoiceDir=%VOICE% voicebank_name
OutFile=output.wav
CacheDir=.
Tool1=wavtool.exe
Tool2=resampler.exe
Mode2=True
[#0000]
Length=480
Lyric=R
NoteNum=60
Intensity=100
Modulation=0
[#TRACKEND]
""",
    "ustx": """name: New Project
ustx_version: "0.6"
resolution: 480
key: 0
time_signatures:
  - bar_position: 0
    beat_per_bar: 4
    beat_unit: 4
tempos:
  - position: 0
    bpm: 120.0
tracks:
  - singer: voicebank_name
    phonemizer: JA CVVC
    track_name: Track 1
    track_color: Blue
    mute: false
    solo: false
    volume: 0.0
    pan: 0.0
    voice_color_names: []
voice_parts:
  - name: Part 1
    comment: ""
    track_no: 0
    position: 0
    duration: 1920
    notes:
      - position: 0
        duration: 480
        tone: 60
        lyric: "do"
""",
    "vsqx": """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<vsq4 xmlns="http://www.yamaha.co.jp/vocaloid/schema/vsq4/"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.yamaha.co.jp/vocaloid/schema/vsq4/ vsq4.xsd">
  <vender>Yamaha corporation</vender>
  <version>4.0.0.0</version>
  <vVoiceTable>
    <vVoice>
      <vBS>0</vBS>
      <vPC>0</vPC>
      <compID>BCNFCYQH8GRLZLYQ</compID>
      <vVoiceName>Miku</vVoiceName>
      <vVoiceParam>
        <bre>0</bre><bri>0</bri><cle>0</cle><gen>0</gen>
      </vVoiceParam>
    </vVoice>
  </vVoiceTable>
  <mixer>
    <masterUnit>
      <vol>0</vol><pan>0</pan>
    </masterUnit>
    <vsUnit>
      <vsTrackNo>0</vsTrackNo><mute>0</mute><solo>0</solo><pan>0</pan><vol>0</vol>
    </vsUnit>
  </mixer>
  <masterTrack>
    <seqName>New Project</seqName>
    <comment></comment>
    <resolution>480</resolution>
    <preMeasure>1</preMeasure>
    <timeSig><m>0</m><nu>4</nu><de>4</de></timeSig>
    <tempo><t>7680</t><v>12000</v></tempo>
  </masterTrack>
  <vsTrack>
    <vsTrackNo>0</vsTrackNo>
    <name>Track 1</name>
    <comment></comment>
    <vsPart>
      <t>7680</t>
      <dur>1920</dur>
      <name>Part1</name>
      <note>
        <t>0</t><dur>480</dur><n>60</n><v>64</v>
        <y>do</y><p>d o</p>
        <nStyle>
          <seq id="vibDep"><p>0</p></seq>
          <seq id="vibRate"><p>0</p></seq>
          <seq id="vibLen"><p>0</p></seq>
        </nStyle>
      </note>
    </vsPart>
  </vsTrack>
</vsq4>
""",
    "svp": """{
  "version": "1.0.0",
  "timeAxis": {
    "tempo": [{"position": 0, "beatPerMinute": 120.0}],
    "timeSignature": [{"measure": 0, "numerator": 4, "denominator": 4}]
  },
  "tracks": [{
    "name": "Track 1",
    "noteGroups": [{
      "notes": [{
        "onset": 0,
        "duration": 7056000,
        "dF0": 0,
        "lyrics": "la",
        "phonemes": "l a",
        "pitch": [{"t": 0, "v": 0}]
      }]
    }]
  }]
}
""",
}


def cmd_create(args: argparse.Namespace) -> int:
    """创建空的工程文件模板。"""
    fmt = args.format.lower()
    output_path = Path(args.output)

    if fmt not in CREATE_TEMPLATES:
        supported = ", ".join(CREATE_TEMPLATES.keys())
        output_json({
            "success": False,
            "error": f"Unsupported format: {fmt}. Supported: {supported}",
        })
        return 1

    ext_map = {
        "ust": ".ust",
        "ustx": ".ustx",
        "vsqx": ".vsqx",
        "svp": ".svp",
    }

    content = CREATE_TEMPLATES[fmt]
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 自动补全扩展名
    if not output_path.suffix:
        output_path = output_path.with_suffix(ext_map[fmt])

    if fmt == "ustx":
        output_path.write_text("\ufeff" + content, encoding="utf-8")
    elif fmt == "ust":
        output_path.write_text(content, encoding="utf-8")
    else:
        output_path.write_text(content, encoding="utf-8")

    output_json({
        "success": True,
        "format": fmt,
        "file": str(output_path),
        "message": f"Created empty {fmt.upper()} project template",
    })
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    """生成录音表或 oto.ini。"""
    gen_type = args.gen_type.lower()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if gen_type == "reclist":
        try:
            import subprocess
            script_dir = Path(__file__).parent
            cmd = [
                sys.executable,
                str(script_dir / "reclist_generator.py"),
                "--type", args.type,
                "--lang", args.lang,
                "--output", str(output_path),
            ]
            if args.format:
                cmd += ["--format", args.format]
            if args.bpm:
                cmd += ["--bpm", str(args.bpm)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                output_json({"success": False, "error": result.stderr})
                return 1
            output_json({
                "success": True,
                "type": "reclist",
                "file": str(output_path),
                "lang": args.lang,
                "reclist_type": args.type,
                "stdout": result.stdout,
            })
            return 0
        except Exception as e:
            output_json({"success": False, "error": str(e)})
            return 1

    elif gen_type == "oto":
        try:
            import subprocess
            script_dir = Path(__file__).parent
            cmd = [
                sys.executable,
                str(script_dir / "oto_generator.py"),
                "generate",
                "--type", args.type,
                "--lang", args.lang,
                "--output", str(output_path),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                output_json({"success": False, "error": result.stderr})
                return 1
            output_json({
                "success": True,
                "type": "oto",
                "file": str(output_path),
                "lang": args.lang,
                "oto_type": args.type,
                "stdout": result.stdout,
            })
            return 0
        except Exception as e:
            output_json({"success": False, "error": str(e)})
            return 1

    else:
        output_json({"success": False, "error": f"Unknown generate type: {gen_type}"})
        return 1


def main() -> int:
    """CLI 入口点。"""
    parser = argparse.ArgumentParser(
        prog="vsynth-scripts",
        description="Vocal synthesis project file tools: validate, parse, extract, create, generate",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # validate
    validate_parser = subparsers.add_parser("validate", help="验证文件格式")
    validate_parser.add_argument("file", help="要验证的文件路径")
    validate_parser.add_argument("--verbose", "-v", action="store_true", help="显示详细信息")

    # info
    info_parser = subparsers.add_parser("info", help="显示文件信息")
    info_parser.add_argument("file", help="要解析的文件路径")

    # extract
    extract_parser = subparsers.add_parser("extract", help="提取容器内容")
    extract_parser.add_argument("file", help="要提取的文件路径")
    extract_parser.add_argument("--output", "-o", required=True, help="输出目录")

    # list-formats
    subparsers.add_parser("list-formats", help="列出支持的格式")

    # detect
    detect_parser = subparsers.add_parser("detect", help="检测文件格式")
    detect_parser.add_argument("file", help="要检测的文件路径")

    # create
    create_parser = subparsers.add_parser("create", help="创建空的工程文件模板")
    create_parser.add_argument("--format", "-f", required=True,
                                choices=["ust", "ustx", "vsqx", "svp"],
                                help="工程文件格式")
    create_parser.add_argument("--output", "-o", required=True, help="输出文件路径")

    # generate
    gen_parser = subparsers.add_parser("generate", help="生成录音表或 oto.ini")
    gen_parser.add_argument("gen_type", choices=["reclist", "oto"], help="生成类型")
    gen_parser.add_argument("--type", "-t", required=True,
                            help="拼接类型 (cv, vcv, cvvc, cvvx, vccv, arpasing)")
    gen_parser.add_argument("--lang", "-l", required=True,
                            choices=["ja", "en", "zh", "ko", "es"],
                            help="语言")
    gen_parser.add_argument("--output", "-o", required=True, help="输出文件路径")
    gen_parser.add_argument("--format", default="plain",
                            choices=["plain", "numbered", "with_bpm"],
                            help="录音表格式 (仅 reclist)")
    gen_parser.add_argument("--bpm", type=int, default=120, help="BPM (仅 reclist with_bpm)")

    args = parser.parse_args()

    if args.command == "validate":
        return cmd_validate(args)
    elif args.command == "info":
        return cmd_info(args)
    elif args.command == "extract":
        return cmd_extract(args)
    elif args.command == "list-formats":
        return cmd_list_formats(args)
    elif args.command == "detect":
        return cmd_detect(args)
    elif args.command == "create":
        return cmd_create(args)
    elif args.command == "generate":
        return cmd_generate(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
