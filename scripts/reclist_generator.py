#!/usr/bin/env python3
"""
歌声合成录音表 (Reclist) 生成器。
支持 CV / VCV / CVVC / CVVX / VCCV / ARPAsing 等多种拼接类型。

用法:
    python reclist_generator.py --type cv --lang ja --output reclist.txt
    python reclist_generator.py --type vcv --lang ja --output vcv.txt
    python reclist_generator.py --type cvvc --lang ja --output cvvc.txt
    python reclist_generator.py --type arpasing --lang en --output arpasing.txt
    python reclist_generator.py --type cvvc --lang zh --output zh_cvvc.txt
"""

import argparse
import sys
from pathlib import Path
from typing import List


# ============ 日语 ============
JA_VOWELS = ["a", "i", "u", "e", "o"]
JA_CONSONANTS = [
    "", "k", "s", "sh", "t", "ch", "ts", "n", "h", "f", "m", "y", "r", "w",
    "g", "z", "j", "d", "b", "p",
]
JA_SEMIVOWELS = ["ya", "yu", "yo"]
JA_SPECIAL = ["n", "Q"]  # 拨音、促音


def generate_ja_cv() -> List[str]:
    """日语 CV 录音表。"""
    result = []
    for c in JA_CONSONANTS:
        for v in JA_VOWELS:
            result.append(f"{c}{v}" if c else v)
    # 拗音
    for c in ["k", "sh", "ch", "n", "h", "m", "r", "g", "j", "b", "p"]:
        for sv in JA_SEMIVOWELS:
            result.append(f"{c}{sv}")
    # 特殊
    result.extend(JA_SPECIAL)
    return result


def generate_ja_vcv() -> List[str]:
    """日语 VCV 录音表。"""
    result = []
    # 词首（无前元音）
    for c in JA_CONSONANTS:
        for v in JA_VOWELS:
            result.append(f"- {c}{v}".strip() if c else f"- {v}")
    # 拗音词首
    for c in ["k", "sh", "ch", "n", "h", "m", "r", "g", "j", "b", "p"]:
        for sv in JA_SEMIVOWELS:
            result.append(f"- {c}{sv}")
    # 带前元音
    for pv in JA_VOWELS:
        for c in JA_CONSONANTS:
            for v in JA_VOWELS:
                syllable = f"{c}{v}" if c else v
                result.append(f"{pv} {syllable}")
        for c in ["k", "sh", "ch", "n", "h", "m", "r", "g", "j", "b", "p"]:
            for sv in JA_SEMIVOWELS:
                result.append(f"{pv} {c}{sv}")
        # 拨音、促音
        result.append(f"{pv} n")
        result.append(f"{pv} Q")
    return result


def generate_ja_cvvc() -> List[str]:
    """日语 CVVC 录音表（CV + VC）。"""
    cv = generate_ja_cv()
    vc = []
    # Vowel + Consonant transitions
    for v in JA_VOWELS:
        for c in JA_CONSONANTS:
            if c:
                vc.append(f"{v} {c}")
    return cv + vc


def generate_ja_cvvx() -> List[str]:
    """日语 CVVX 录音表（CV + VV + VC）。"""
    cv = generate_ja_cv()
    vv = []
    for v1 in JA_VOWELS:
        for v2 in JA_VOWELS:
            vv.append(f"{v1} {v2}")
    vc = []
    for v in JA_VOWELS:
        for c in JA_CONSONANTS:
            if c:
                vc.append(f"{v} {c}")
    return cv + vv + vc


# ============ 英语 ============
EN_ARPABET_VOWELS = [
    "AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER", "EY",
    "IH", "IY", "OW", "OY", "UH", "UW",
]
EN_ARPABET_CONSONANTS = [
    "B", "CH", "D", "DH", "F", "G", "HH", "JH", "K", "L",
    "M", "N", "NG", "P", "R", "S", "SH", "T", "TH", "V",
    "W", "Y", "Z", "ZH",
]


def generate_en_arpasing() -> List[str]:
    """英语 ARPAsing 录音表（ARPAbet 音素）。"""
    result = []
    # 单音素
    result.extend(EN_ARPABET_VOWELS)
    result.extend(EN_ARPABET_CONSONANTS)
    # CV / VC 组合
    for v in EN_ARPABET_VOWELS:
        for c in EN_ARPABET_CONSONANTS:
            result.append(f"- {c} {v}")
            result.append(f"{v} {c}")
    return result


def generate_en_vccv() -> List[str]:
    """英语 VCCV 录音表（简化版）。"""
    result = []
    vowels = ["a", "e", "i", "o", "u"]
    consonants = ["b", "d", "f", "g", "h", "k", "l", "m", "n", "p", "r", "s", "t", "v", "w", "y", "z"]
    clusters = ["br", "bl", "cr", "cl", "dr", "fr", "fl", "gr", "gl", "pr", "pl", "sk", "sp", "st", "str", "spl", "shr", "thr"]
    for v in vowels:
        for c in consonants:
            for v2 in vowels:
                result.append(f"{v} {c} {v2}")
        for cl in clusters:
            for v2 in vowels:
                result.append(f"{v} {cl} {v2}")
    return result


# ============ 中文 ============
ZH_INITIALS = [
    "b", "p", "m", "f", "d", "t", "n", "l",
    "g", "k", "h", "j", "q", "x",
    "zh", "ch", "sh", "r", "z", "c", "s",
    "y", "w",
]
ZH_FINALS = [
    "a", "o", "e", "i", "u", "v",
    "ai", "ei", "ao", "ou", "an", "en", "ang", "eng", "er",
    "ia", "iao", "ian", "iang", "ie", "in", "ing", "iong",
    "ua", "uo", "uai", "ui", "uan", "un", "uang", "ong",
    "ve", "ue",
]


def generate_zh_cvvc() -> List[str]:
    """中文 CVVC 录音表。"""
    cv = []
    # 零声母
    for f in ZH_FINALS:
        cv.append(f)
    # 声母+韵母
    for i in ZH_INITIALS:
        for f in ZH_FINALS:
            # 跳过不存在的组合（简化处理，完整需用拼音表过滤）
            cv.append(f"{i}{f}")
    # VC 过渡
    vc = []
    # 韵母尾音到声母的过渡（简化版）
    finals_end = ["a", "i", "u", "e", "o", "n", "ng", "r"]
    for fe in finals_end:
        for i in ZH_INITIALS:
            vc.append(f"{fe} {i}")
    return cv + vc


# ============ 韩语 ============
KO_CONSONANTS = [
    "g", "k", "n", "d", "t", "r", "m", "b", "p", "s", "ss", "", "j", "ch", "k2", "t2", "p2", "h"
]
KO_VOWELS = [
    "a", "ya", "eo", "yeo", "o", "yo", "u", "yu", "ae", "yae", "e", "ye", "wa", "wae", "wo", "we", "wi", "ui", "eu", "i"
]
KO_FINALS = ["", "g", "k", "k2", "n", "n2", "n3", "t", "r", "l", "l2", "m", "p", "p2", "b", "s", "ss", "ng", "ch", "t2", "h"]


def generate_ko_cvvc() -> List[str]:
    """韩语 CVVC 录音表（简化）。"""
    cv = []
    for c in KO_CONSONANTS:
        for v in KO_VOWELS:
            cv.append(f"{c}{v}" if c else v)
    vc = []
    for v in KO_VOWELS:
        for fc in KO_FINALS:
            if fc:
                vc.append(f"{v} {fc}")
    return cv + vc


# ============ 主程序 ============

def main() -> int:
    parser = argparse.ArgumentParser(description="歌声合成录音表生成器")
    parser.add_argument("--type", "-t", required=True,
                        choices=["cv", "vcv", "cvvc", "cvvx", "vccv", "arpasing"],
                        help="拼接类型")
    parser.add_argument("--lang", "-l", required=True,
                        choices=["ja", "en", "zh", "ko", "es"],
                        help="语言")
    parser.add_argument("--output", "-o", required=True, help="输出文件路径")
    parser.add_argument("--format", "-f", default="plain",
                        choices=["plain", "numbered", "with_bpm"],
                        help="输出格式")
    parser.add_argument("--bpm", default=120, type=int, help="BPM（仅 with_bpm 格式）")
    parser.add_argument("--offset", default=1.0, type=float, help="起始偏移秒数（仅 with_bpm 格式）")
    args = parser.parse_args()

    # 生成录音表
    reclist: List[str] = []
    if args.lang == "ja":
        if args.type == "cv":
            reclist = generate_ja_cv()
        elif args.type == "vcv":
            reclist = generate_ja_vcv()
        elif args.type == "cvvc":
            reclist = generate_ja_cvvc()
        elif args.type == "cvvx":
            reclist = generate_ja_cvvx()
        else:
            print(f"错误: 日语不支持 {args.type} 类型", file=sys.stderr)
            return 1
    elif args.lang == "en":
        if args.type == "arpasing":
            reclist = generate_en_arpasing()
        elif args.type == "vccv":
            reclist = generate_en_vccv()
        elif args.type == "cv":
            # 英语简化 CV
            reclist = [f"{c}{v}" for c in ["b", "d", "f", "g", "h", "k", "l", "m", "n", "p", "r", "s", "sh", "t", "v", "w", "y", "z"] for v in ["a", "e", "i", "o", "u"]]
            reclist += ["a", "e", "i", "o", "u"]
        else:
            print(f"错误: 英语不支持 {args.type} 类型（推荐 arpasing 或 vccv）", file=sys.stderr)
            return 1
    elif args.lang == "zh":
        if args.type == "cvvc":
            reclist = generate_zh_cvvc()
        elif args.type == "cv":
            # 中文简化 CV（仅常见组合）
            initials = ["b", "p", "m", "f", "d", "t", "n", "l", "g", "k", "h", "j", "q", "x", "zh", "ch", "sh", "r", "z", "c", "s"]
            finals = ["a", "o", "e", "i", "u", "ai", "ei", "ao", "ou", "an", "en", "ang", "eng"]
            reclist = [f"{i}{f}" for i in initials for f in finals] + finals
        else:
            print(f"错误: 中文目前主要支持 cvvc / cv 类型", file=sys.stderr)
            return 1
    elif args.lang == "ko":
        if args.type == "cvvc":
            reclist = generate_ko_cvvc()
        elif args.type == "cv":
            reclist = [f"{c}{v}" for c in KO_CONSONANTS if c for v in KO_VOWELS] + KO_VOWELS
        else:
            print(f"错误: 韩语目前主要支持 cvvc / cv 类型", file=sys.stderr)
            return 1
    elif args.lang == "es":
        if args.type == "cv":
            cons = ["b", "ch", "d", "f", "g", "h", "j", "k", "l", "ll", "m", "n", "p", "q", "r", "rr", "s", "t", "v", "w", "x", "y", "z"]
            vows = ["a", "e", "i", "o", "u"]
            reclist = [f"{c}{v}" for c in cons for v in vows] + vows
        else:
            print(f"错误: 西班牙语目前仅支持 cv 类型", file=sys.stderr)
            return 1

    # 格式化输出
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines: List[str] = []
    if args.format == "plain":
        lines = reclist
    elif args.format == "numbered":
        for idx, item in enumerate(reclist, 1):
            lines.append(f"{idx:04d} {item}")
    elif args.format == "with_bpm":
        lines.append(f"#BPM {args.bpm}")
        lines.append(f"#OFFSET {args.offset}")
        lines.extend(reclist)

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"已生成录音表: {output_path} ({len(reclist)} 项)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
