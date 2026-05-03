#!/usr/bin/env python3
"""
VPR 音素诊断工具 — 分析 VOCALOID 6 VPR 文件中的音素分布与问题

用法:
    python vpr_phoneme_inspect.py <vpr_file> [--track N] [--json]
    python vpr_phoneme_inspect.py <vpr_file> --find-a               # 找出音素为 "a" 的音符
    python vpr_phoneme_inspect.py <vpr_file> --check-protected      # 检查 isProtected 覆盖率
    python vpr_phoneme_inspect.py <vpr_file> --summary              # 音素分布统计

功能:
    - 统计各轨道的音素分布（哪些音素被使用、频率如何）
    - 检测音素为 "a" 的音符（通常是音素未正确映射的标志）
    - 检查 isProtected 字段覆盖率（编辑器内歌词修改时的音素保护）
    - 分析音素长度、空格分隔正确性
    - 检测潜在的不合法日语音素

说明:
    - 音素为 "a" 通常表示原始 VPR 中 phoneme 字段未映射，本身就是默认值 "a"
    - isProtected 不影响直接 JSON 修改的加载结果，只影响编辑器内改歌词时的行为
    - 如果修改 JSON 后编辑器仍显示旧音素，请检查是否为编辑器缓存（使用不同文件名）

输出格式: 默认表格 / --json 输出结构化 JSON
"""

import argparse
import json
import sys
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# 日语音库合法音素白名单（X-SAMPA）
JPN_VALID_PHONEMES: Set[str] = {
    # 元音
    "a", "i", "M", "e", "o",
    # 辅音（基本）
    "k", "g", "s", "z", "S", "tS", "ts", "dz", "dZ",
    "t", "d", "n", "J", "N", "N\\",
    "h", "C", "p\\", "b", "p", "m", "j", "w", "4",
    # 特殊
    "?", "Q", "_0", "_h",
    # 腭化标记（附加在辅音后）
    "'",  # 作为后缀使用，如 b', d', t'
}

# 腭化辅音集合
PALATALIZED_CONSONANTS = {"b'", "d'", "t'", "m'", "p'", "g'", "k'", "4'", "p\\'", "N'", "n'"}


def parse_vpr(file_path: Path) -> Optional[Dict[str, Any]]:
    """解析 VPR 文件，返回 sequence.json 内容。"""
    if not file_path.exists():
        print(f"错误: 文件不存在 {file_path}", file=sys.stderr)
        return None

    try:
        with zipfile.ZipFile(file_path, "r") as zf:
            seq_data = zf.read("Project/sequence.json").decode("utf-8")
            return json.loads(seq_data)
    except zipfile.BadZipFile:
        print(f"错误: 不是有效的 ZIP/VPR 文件 {file_path}", file=sys.stderr)
        return None
    except KeyError:
        print(f"错误: VPR 中缺少 Project/sequence.json", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"错误: JSON 解析失败: {e}", file=sys.stderr)
        return None


def extract_notes(seq: Dict[str, Any], track_filter: Optional[int] = None) -> List[Dict[str, Any]]:
    """从 sequence.json 中提取所有音符（或指定轨道）。"""
    notes_list: List[Dict[str, Any]] = []
    tracks = seq.get("tracks", [])

    for tidx, track in enumerate(tracks):
        if track_filter is not None and tidx != track_filter:
            continue

        track_name = track.get("name", f"Track {tidx}")
        track_type = track.get("type", "unknown")

        for part in track.get("parts", []):
            part_start = part.get("start", 0)
            for note in part.get("notes", []):
                note_info = {
                    "track_index": tidx,
                    "track_name": track_name,
                    "track_type": track_type,
                    "part_start": part_start,
                    "pos": note.get("pos", 0),
                    "duration": note.get("duration", 0),
                    "pitch": note.get("number", note.get("pitch", 60)),
                    "lyric": note.get("lyric", ""),
                    "phoneme": note.get("phoneme", ""),
                    "langID": note.get("langID", 0),
                    "isProtected": note.get("isProtected", False),
                    "velocity": note.get("velocity", 64),
                }
                notes_list.append(note_info)

    return notes_list


def analyze_phonemes(notes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析音素分布与问题。"""
    all_phonemes: List[str] = []
    a_notes: List[Dict[str, Any]] = []
    empty_notes: List[Dict[str, Any]] = []
    unprotected_notes: List[Dict[str, Any]] = []
    invalid_jpn_tokens: List[str] = []

    for note in notes:
        ph = note["phoneme"]
        lyric = note["lyric"]

        # 统计 "a" 音素
        if ph == "a":
            a_notes.append(note)

        # 统计空音素
        if not ph or ph.strip() == "":
            empty_notes.append(note)

        # 统计未保护
        if not note["isProtected"]:
            unprotected_notes.append(note)

        # 分割音素并统计
        if ph:
            tokens = ph.split()
            all_phonemes.extend(tokens)

            # 检查日语音素合法性（简单检查）
            for token in tokens:
                # 去掉腭化后缀检查基本音素
                base = token.rstrip("'")
                # 忽略下标变体如 _0, _h
                base_clean = base
                for suffix in ["_0", "_h"]:
                    if base_clean.endswith(suffix):
                        base_clean = base_clean[:-len(suffix)]
                        break
                if base_clean and base_clean not in JPN_VALID_PHONEMES:
                    if base_clean not in PALATALIZED_CONSONANTS:
                        invalid_jpn_tokens.append(token)

    phoneme_counter = Counter(all_phonemes)

    return {
        "total_notes": len(notes),
        "a_notes_count": len(a_notes),
        "a_notes_ratio": len(a_notes) / len(notes) if notes else 0,
        "empty_notes_count": len(empty_notes),
        "unprotected_count": len(unprotected_notes),
        "unprotected_ratio": len(unprotected_notes) / len(notes) if notes else 0,
        "unique_phonemes": len(phoneme_counter),
        "phoneme_distribution": dict(phoneme_counter.most_common()),
        "a_notes_preview": a_notes[:20],
        "empty_notes_preview": empty_notes[:10],
        "unprotected_preview": unprotected_notes[:20],
        "invalid_jpn_tokens": list(set(invalid_jpn_tokens)),
    }


def print_summary(result: Dict[str, Any], notes: List[Dict[str, Any]]) -> None:
    """打印诊断摘要（表格格式）。"""
    print("=" * 60)
    print("VPR 音素诊断报告")
    print("=" * 60)
    print(f"\n总音符数: {result['total_notes']}")
    print(f"唯一音素数: {result['unique_phonemes']}")

    # 音素 "a" 警告
    a_count = result["a_notes_count"]
    a_ratio = result["a_notes_ratio"] * 100
    print(f"\n⚠️  音素为 'a' 的音符: {a_count} ({a_ratio:.1f}%)")
    if a_count > 0:
        print("   → 大量 'a' 通常是跨语种失败的标志（V6 无法识别拼音回退到默认元音）")
        print("\n   前 10 个 'a' 音符:")
        for note in result["a_notes_preview"][:10]:
            print(f"      [{note['track_name']}] lyric='{note['lyric']}' pos={note['pos']} pitch={note['pitch']}")

    # isProtected 检查
    unprot_count = result["unprotected_count"]
    unprot_ratio = result["unprotected_ratio"] * 100
    print(f"\n🔒 isProtected=false 的音符: {unprot_count} ({unprot_ratio:.1f}%)")
    if unprot_count > 0:
        print("   → V6 中 isProtected=false 会导致音素被歌词自动覆盖！")
        print("   → 修复: 将这些音符的 isProtected 设为 true")

    # 空音素
    empty_count = result["empty_notes_count"]
    if empty_count > 0:
        print(f"\n⚠️  空音素音符: {empty_count}")

    # 音素分布 Top 20
    print(f"\n📊 音素分布 Top 20:")
    dist = result["phoneme_distribution"]
    for ph, count in list(dist.items())[:20]:
        bar = "█" * min(count // max(1, result["total_notes"] // 50), 20)
        print(f"   {ph:8s} {count:5d} {bar}")

    # 非法音素
    invalid = result.get("invalid_jpn_tokens", [])
    if invalid:
        print(f"\n⚠️  可能不合法的日语音素标记: {', '.join(invalid[:20])}")
        if len(invalid) > 20:
            print(f"   ... 等共 {len(invalid)} 个")

    # 轨道汇总
    print(f"\n🎵 轨道汇总:")
    track_groups: Dict[str, List[Dict]] = {}
    for note in notes:
        key = f"[{note['track_index']}] {note['track_name']} (type={note['track_type']})"
        track_groups.setdefault(key, []).append(note)

    for track_key, tnotes in track_groups.items():
        a_in_track = sum(1 for n in tnotes if n["phoneme"] == "a")
        unprot_in_track = sum(1 for n in tnotes if not n["isProtected"])
        print(f"   {track_key}: {len(tnotes)} notes, a={a_in_track}, unprotected={unprot_in_track}")

    print("\n" + "=" * 60)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="VPR 音素诊断工具 — 分析 VOCALOID 6 VPR 文件中的音素分布与问题",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s song.vpr                    # 完整诊断报告
  %(prog)s song.vpr --track 0         # 只分析轨道 0
  %(prog)s song.vpr --json            # JSON 输出
  %(prog)s song.vpr --find-a          # 只列出音素为 a 的音符
  %(prog)s song.vpr --check-protected # 只检查 isProtected
  %(prog)s song.vpr --summary         # 只输出音素分布统计
        """,
    )
    parser.add_argument("file", help="VPR 文件路径")
    parser.add_argument("--track", type=int, default=None, help="只分析指定轨道索引")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出")
    parser.add_argument("--find-a", action="store_true", help="只列出音素为 'a' 的音符")
    parser.add_argument("--check-protected", action="store_true", help="只检查 isProtected 覆盖率")
    parser.add_argument("--summary", action="store_true", help="只输出音素分布统计")

    args = parser.parse_args()
    file_path = Path(args.file)

    seq = parse_vpr(file_path)
    if seq is None:
        return 1

    notes = extract_notes(seq, track_filter=args.track)
    if not notes:
        print("未找到音符", file=sys.stderr)
        return 1

    # 只列出 a
    if args.find_a:
        a_notes = [n for n in notes if n["phoneme"] == "a"]
        result = {
            "count": len(a_notes),
            "notes": a_notes,
        }
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"音素为 'a' 的音符共 {len(a_notes)} 个:")
            for note in a_notes:
                print(f"  track={note['track_index']} lyric='{note['lyric']}' pos={note['pos']} pitch={note['pitch']}")
        return 0

    # 只检查 protected
    if args.check_protected:
        unprotected = [n for n in notes if not n["isProtected"]]
        result = {
            "total": len(notes),
            "unprotected_count": len(unprotected),
            "ratio": len(unprotected) / len(notes) if notes else 0,
            "notes": unprotected[:50],
        }
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"isProtected 检查: {len(unprotected)}/{len(notes)} 未锁定")
            if unprotected:
                print("前 20 个未锁定音符:")
                for note in unprotected[:20]:
                    print(f"  [{note['track_name']}] lyric='{note['lyric']}' phoneme='{note['phoneme']}'")
        return 0

    # 只输出 summary
    if args.summary:
        result = analyze_phonemes(notes)
        dist = result["phoneme_distribution"]
        if args.json:
            print(json.dumps({"phoneme_distribution": dist}, ensure_ascii=False, indent=2))
        else:
            print("音素分布统计:")
            for ph, count in dist.items():
                print(f"  {ph}: {count}")
        return 0

    # 完整诊断
    result = analyze_phonemes(notes)
    result["file"] = str(file_path)
    result["track_filter"] = args.track

    if args.json:
        # 清理大型数组，保留计数即可
        clean_result = {k: v for k, v in result.items() if not k.endswith("_preview")}
        clean_result["notes_count"] = result["total_notes"]
        print(json.dumps(clean_result, ensure_ascii=False, indent=2))
    else:
        print_summary(result, notes)

    return 0


if __name__ == "__main__":
    sys.exit(main())
