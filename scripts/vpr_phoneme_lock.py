#!/usr/bin/env python3
"""
VPR 音素锁定工具 — 管理 VPR 音符的 isProtected 字段

用法:
    python vpr_phoneme_lock.py <vpr_file> --lock --output fixed.vpr
    python vpr_phoneme_lock.py <vpr_file> --unlock --track 0 --output fixed.vpr
    python vpr_phoneme_lock.py <vpr_file> --lock-only-a --output fixed.vpr
    python vpr_phoneme_lock.py <vpr_file> --status              # 只统计不修改

功能:
    - 批量设置/取消 VPR 音符的 isProtected 字段
    - 可按轨道筛选、按音素内容筛选
    - 用于防止在 V6 编辑器内修改歌词时丢失手动设置的音素

isProtected 字段说明 (VOCALOID 6):
    - false (默认): 在编辑器内修改歌词时，自动根据新歌词更新音素
    - true: 在编辑器内修改歌词时，保留原有音素不自动更新
    - 直接修改 JSON 数据时，isProtected 不影响加载结果
    - 跨语种时建议设为 true，防止用户误操作覆盖音素，但不是加载的必要条件
"""

import argparse
import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional


def parse_vpr(file_path: Path) -> Optional[Dict[str, Any]]:
    """解析 VPR 文件。"""
    try:
        with zipfile.ZipFile(file_path, "r") as zf:
            return json.loads(zf.read("Project/sequence.json").decode("utf-8"))
    except Exception as e:
        print(f"错误: 解析 VPR 失败: {e}", file=sys.stderr)
        return None


def save_vpr(seq: Dict[str, Any], source_vpr: Path, output_path: Path) -> None:
    """将修改后的 sequence.json 重新打包为 VPR。"""
    tmp_dir = Path(tempfile.mkdtemp())
    try:
        seq_dir = tmp_dir / "Project"
        seq_dir.mkdir(parents=True, exist_ok=True)
        (seq_dir / "sequence.json").write_text(
            json.dumps(seq, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        with zipfile.ZipFile(source_vpr, "r") as zf_in:
            for item in zf_in.infolist():
                if item.filename != "Project/sequence.json":
                    zf_in.extract(item, tmp_dir)

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf_out:
            for path in tmp_dir.rglob("*"):
                if path.is_file():
                    arcname = str(path.relative_to(tmp_dir)).replace("\\", "/")
                    zf_out.write(path, arcname)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def modify_isProtected(
    seq: Dict[str, Any],
    lock: bool,
    track_filter: Optional[int] = None,
    only_phoneme: Optional[str] = None,
    only_empty: bool = False,
    only_unprotected: bool = False,
) -> Dict[str, Any]:
    """修改 isProtected 字段，返回统计信息。"""
    stats = {
        "total_notes": 0,
        "modified": 0,
        "already_correct": 0,
        "skipped_filter": 0,
    }

    for tidx, track in enumerate(seq.get("tracks", [])):
        if track_filter is not None and tidx != track_filter:
            continue

        for part in track.get("parts", []):
            for note in part.get("notes", []):
                stats["total_notes"] += 1

                phoneme = note.get("phoneme", "")
                current = note.get("isProtected", False)

                # 筛选条件
                if only_phoneme is not None and phoneme != only_phoneme:
                    stats["skipped_filter"] += 1
                    continue

                if only_empty and phoneme.strip() != "":
                    stats["skipped_filter"] += 1
                    continue

                if only_unprotected and current:
                    stats["skipped_filter"] += 1
                    continue

                # 执行修改
                if current != lock:
                    note["isProtected"] = lock
                    stats["modified"] += 1
                else:
                    stats["already_correct"] += 1

    return stats


def get_status(seq: Dict[str, Any], track_filter: Optional[int] = None) -> Dict[str, Any]:
    """获取 isProtected 状态统计。"""
    total = 0
    locked = 0
    unlocked = 0
    track_stats = []

    for tidx, track in enumerate(seq.get("tracks", [])):
        if track_filter is not None and tidx != track_filter:
            continue

        t_total = 0
        t_locked = 0
        t_unlocked = 0

        for part in track.get("parts", []):
            for note in part.get("notes", []):
                t_total += 1
                if note.get("isProtected", False):
                    t_locked += 1
                else:
                    t_unlocked += 1

        track_stats.append({
            "index": tidx,
            "name": track.get("name", f"Track {tidx}"),
            "type": track.get("type", "unknown"),
            "total": t_total,
            "locked": t_locked,
            "unlocked": t_unlocked,
            "lock_ratio": t_locked / t_total if t_total else 0,
        })

        total += t_total
        locked += t_locked
        unlocked += t_unlocked

    return {
        "total_notes": total,
        "locked": locked,
        "unlocked": unlocked,
        "lock_ratio": locked / total if total else 0,
        "tracks": track_stats,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="VPR 音素锁定工具 — 管理 VPR 音符的 isProtected 字段",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s song.vpr --lock --output fixed.vpr
  %(prog)s song.vpr --unlock --track 1 --output t1_unlocked.vpr
  %(prog)s song.vpr --lock-only-a --output fixed.vpr
  %(prog)s song.vpr --status --json
  %(prog)s song.vpr --lock --only-unprotected --output fixed.vpr
        """,
    )
    parser.add_argument("file", help="输入 VPR 文件路径")
    parser.add_argument("--output", "-o", help="输出 VPR 文件路径（修改模式必须）")
    parser.add_argument("--lock", action="store_true", help="设置 isProtected = true")
    parser.add_argument("--unlock", action="store_true", help="设置 isProtected = false")
    parser.add_argument("--lock-only-a", action="store_true",
                        help="只锁定 phoneme == 'a' 的音符（跨语种失败标记）")
    parser.add_argument("--only-unprotected", action="store_true",
                        help="只操作当前 isProtected == false 的音符")
    parser.add_argument("--track", type=int, default=None, help="只操作指定轨道")
    parser.add_argument("--status", action="store_true", help="只统计状态，不修改")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出")
    parser.add_argument("--dry-run", action="store_true", help="预览修改但不写入")

    args = parser.parse_args()
    vpr_path = Path(args.file)

    if not vpr_path.exists():
        print(f"错误: 文件不存在 {vpr_path}", file=sys.stderr)
        return 1

    seq = parse_vpr(vpr_path)
    if seq is None:
        return 1

    # 状态查询模式
    if args.status:
        status = get_status(seq, track_filter=args.track)
        if args.json:
            print(json.dumps(status, ensure_ascii=False, indent=2))
        else:
            print("=" * 50)
            print("isProtected 状态统计")
            print("=" * 50)
            print(f"总音符:   {status['total_notes']}")
            print(f"已锁定:   {status['locked']} ({status['lock_ratio']*100:.1f}%)")
            print(f"未锁定:   {status['unlocked']}")
            print(f"\n轨道明细:")
            for t in status["tracks"]:
                ratio = t["lock_ratio"] * 100
                bar = "█" * int(ratio / 5)
                print(f"  [{t['index']}] {t['name']} (type={t['type']}): {t['locked']}/{t['total']} 锁定 {ratio:.0f}% {bar}")
        return 0

    # 修改模式需要验证参数
    if not args.lock and not args.unlock and not args.lock_only_a:
        print("错误: 修改模式必须指定 --lock, --unlock 或 --lock-only-a", file=sys.stderr)
        return 1

    if not args.output:
        print("错误: 修改模式必须指定 --output", file=sys.stderr)
        return 1

    # 确定操作
    if args.lock_only_a:
        lock_target = True
        only_phoneme = "a"
        only_unprotected = args.only_unprotected
    elif args.lock:
        lock_target = True
        only_phoneme = None
        only_unprotected = args.only_unprotected
    else:  # unlock
        lock_target = False
        only_phoneme = None
        only_unprotected = args.only_unprotected

    stats = modify_isProtected(
        seq,
        lock=lock_target,
        track_filter=args.track,
        only_phoneme=only_phoneme,
        only_unprotected=only_unprotected,
    )

    if args.json:
        result = {
            "action": "lock" if lock_target else "unlock",
            "total_notes": stats["total_notes"],
            "modified": stats["modified"],
            "already_correct": stats["already_correct"],
            "skipped_filter": stats["skipped_filter"],
            "dry_run": args.dry_run,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        action_name = "锁定" if lock_target else "解锁"
        print("=" * 50)
        print(f"isProtected {action_name}结果")
        print("=" * 50)
        print(f"总音符:     {stats['total_notes']}")
        print(f"已修改:     {stats['modified']}")
        print(f"无需修改:   {stats['already_correct']}")
        if stats['skipped_filter']:
            print(f"筛选跳过:   {stats['skipped_filter']}")

    if not args.dry_run and args.output:
        save_vpr(seq, vpr_path, Path(args.output))
        if not args.json:
            print(f"\n✓ 已保存到 {args.output}")
    elif args.dry_run and not args.json:
        print("\n⚠️  这是预览模式 (dry-run)，未实际写入文件")

    return 0


if __name__ == "__main__":
    sys.exit(main())
