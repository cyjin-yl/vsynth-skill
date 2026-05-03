#!/usr/bin/env python3
"""
o to.ini 批量生成器。
支持 CV / VCV / CVVC / CVVX 等拼接类型的 oto 参数模板生成与调整。

用法:
    python oto_generator.py --type cv --lang ja --output oto.ini
    python oto_generator.py --type cvvc --lang ja --output oto.ini
    python oto_generator.py --template base_oto.ini --adjustments adj.json --output new_oto.ini
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple


# ============ 参数模板 ============

CV_TEMPLATES = {
    "ja": {
        "default": {"offset": 60, "consonant": 40, "cutoff": 0, "preutterance": 70, "overlap": 30},
        "plosive": {"offset": 70, "consonant": 35, "cutoff": 0, "preutterance": 80, "overlap": 22},
        "fricative": {"offset": 80, "consonant": 50, "cutoff": 0, "preutterance": 90, "overlap": 35},
        "nasal": {"offset": 60, "consonant": 40, "cutoff": 0, "preutterance": 70, "overlap": 30},
        "liquid": {"offset": 55, "consonant": 35, "cutoff": 0, "preutterance": 65, "overlap": 25},
        "vowel": {"offset": 20, "consonant": 80, "cutoff": 0, "preutterance": 30, "overlap": 15},
    },
    "zh": {
        "default": {"offset": 50, "consonant": 50, "cutoff": 0, "preutterance": 65, "overlap": 28},
        "plosive": {"offset": 60, "consonant": 40, "cutoff": 0, "preutterance": 75, "overlap": 25},
        "affricate": {"offset": 70, "consonant": 55, "cutoff": 0, "preutterance": 85, "overlap": 30},
        "fricative": {"offset": 75, "consonant": 60, "cutoff": 0, "preutterance": 90, "overlap": 35},
        "nasal": {"offset": 55, "consonant": 45, "cutoff": 0, "preutterance": 70, "overlap": 28},
        "vowel": {"offset": 25, "consonant": 75, "cutoff": 0, "preutterance": 35, "overlap": 15},
    },
    "en": {
        "default": {"offset": 40, "consonant": 50, "cutoff": 0, "preutterance": 55, "overlap": 20},
        "plosive": {"offset": 50, "consonant": 40, "cutoff": 0, "preutterance": 65, "overlap": 18},
        "vowel": {"offset": 20, "consonant": 70, "cutoff": 0, "preutterance": 30, "overlap": 12},
    },
}

VCV_TEMPLATES = {
    "ja": {
        "default": {"offset": 120, "consonant": 80, "cutoff": -500, "preutterance": 130, "overlap": 110},
        "head": {"offset": 30, "consonant": 80, "cutoff": 0, "preutterance": 40, "overlap": 20},
    }
}

CVVC_TEMPLATES = {
    "ja": {
        "cv": {"offset": 60, "consonant": 35, "cutoff": -200, "preutterance": 70, "overlap": 30},
        "vc": {"offset": 30, "consonant": 60, "cutoff": -300, "preutterance": 40, "overlap": 20},
        "vv": {"offset": 20, "consonant": 80, "cutoff": -400, "preutterance": 30, "overlap": 15},
    },
    "zh": {
        "cv": {"offset": 50, "consonant": 45, "cutoff": -250, "preutterance": 65, "overlap": 28},
        "vc": {"offset": 30, "consonant": 55, "cutoff": -350, "preutterance": 45, "overlap": 20},
    },
}


def classify_consonant(consonant: str, lang: str) -> str:
    """根据辅音分类返回模板键。"""
    c = consonant.lower()
    if lang == "ja":
        if c in ["k", "t", "p", "b", "d", "g"]:
            return "plosive"
        if c in ["s", "sh", "h", "f"]:
            return "fricative"
        if c in ["n", "m", "ng"]:
            return "nasal"
        if c in ["r", "w", "y"]:
            return "liquid"
        if c == "":
            return "vowel"
        return "default"
    elif lang == "zh":
        if c in ["b", "p", "d", "t", "g", "k"]:
            return "plosive"
        if c in ["zh", "ch", "sh", "z", "c", "s", "j", "q", "x", "f", "h", "r"]:
            return "fricative"
        if c in ["zh", "ch", "sh", "z", "c", "s"]:
            return "affricate"
        if c in ["m", "n", "ng"]:
            return "nasal"
        if c == "":
            return "vowel"
        return "default"
    elif lang == "en":
        if c in ["b", "p", "d", "t", "g", "k"]:
            return "plosive"
        if c == "":
            return "vowel"
        return "default"
    return "default"


def generate_cv_oto(lang: str) -> List[str]:
    """生成 CV 类型 oto.ini 内容。"""
    if lang not in CV_TEMPLATES:
        raise ValueError(f"语言 {lang} 暂不支持 CV oto 生成")
    tpl = CV_TEMPLATES[lang]
    lines = []

    if lang == "ja":
        vows = ["a", "i", "u", "e", "o"]
        cons = ["", "k", "s", "sh", "t", "ch", "ts", "n", "h", "f", "m", "y", "r", "w",
                "g", "z", "j", "d", "b", "p"]
        for c in cons:
            cat = classify_consonant(c, "ja")
            t = tpl.get(cat, tpl["default"])
            for v in vows:
                name = f"{c}{v}.wav" if c else f"{v}.wav"
                line = f"{name}={t['offset']},{t['consonant']},{t['cutoff']},{t['preutterance']},{t['overlap']}"
                lines.append(line)
        # 拗音
        for c in ["k", "sh", "ch", "n", "h", "m", "r", "g", "j", "b", "p"]:
            cat = classify_consonant(c, "ja")
            t = tpl.get(cat, tpl["default"])
            for sv in ["ya", "yu", "yo"]:
                name = f"{c}{sv}.wav"
                lines.append(f"{name}={t['offset']},{t['consonant']},{t['cutoff']},{t['preutterance']},{t['overlap']}")
        # 特殊
        for sp in ["n", "Q"]:
            lines.append(f"{sp}.wav=20,60,0,30,15")
    elif lang == "zh":
        initials = ["", "b", "p", "m", "f", "d", "t", "n", "l", "g", "k", "h",
                    "j", "q", "x", "zh", "ch", "sh", "r", "z", "c", "s", "y", "w"]
        finals = ["a", "o", "e", "i", "u", "ai", "ei", "ao", "ou", "an", "en", "ang", "eng", "er"]
        for i in initials:
            cat = classify_consonant(i, "zh")
            t = tpl.get(cat, tpl["default"])
            for f in finals:
                name = f"{i}{f}.wav" if i else f"{f}.wav"
                lines.append(f"{name}={t['offset']},{t['consonant']},{t['cutoff']},{t['preutterance']},{t['overlap']}")
    elif lang == "en":
        cons = ["", "b", "d", "f", "g", "h", "k", "l", "m", "n", "p", "r", "s", "sh", "t", "v", "w", "y", "z"]
        vows = ["a", "e", "i", "o", "u"]
        for c in cons:
            cat = classify_consonant(c, "en")
            t = tpl.get(cat, tpl["default"])
            for v in vows:
                name = f"{c}{v}.wav" if c else f"{v}.wav"
                lines.append(f"{name}={t['offset']},{t['consonant']},{t['cutoff']},{t['preutterance']},{t['overlap']}")
    return lines


def generate_cvvc_oto(lang: str) -> List[str]:
    """生成 CVVC 类型 oto.ini 内容。"""
    if lang not in CVVC_TEMPLATES:
        raise ValueError(f"语言 {lang} 暂不支持 CVVC oto 生成")
    tpl = CVVC_TEMPLATES[lang]
    lines = generate_cv_oto(lang)

    # 为 CV 部分更新 cutoff
    cv_tpl = tpl["cv"]
    updated = []
    for line in lines:
        if "=" not in line:
            updated.append(line)
            continue
        name, params = line.split("=", 1)
        parts = params.split(",")
        parts[2] = str(cv_tpl["cutoff"])
        updated.append(f"{name}={','.join(parts)}")
    lines = updated

    # 添加 VC 部分
    vc_tpl = tpl["vc"]
    if lang == "ja":
        vows = ["a", "i", "u", "e", "o"]
        cons = ["k", "s", "sh", "t", "ch", "ts", "n", "h", "f", "m", "y", "r", "w",
                "g", "z", "j", "d", "b", "p"]
        for v in vows:
            for c in cons:
                name = f"{v} {c}.wav"
                lines.append(f"{name}={vc_tpl['offset']},{vc_tpl['consonant']},{vc_tpl['cutoff']},{vc_tpl['preutterance']},{vc_tpl['overlap']}")
    elif lang == "zh":
        initials = ["b", "p", "m", "f", "d", "t", "n", "l", "g", "k", "h",
                    "j", "q", "x", "zh", "ch", "sh", "r", "z", "c", "s", "y", "w"]
        finals_end = ["a", "o", "e", "i", "u", "n", "ng", "r"]
        for fe in finals_end:
            for i in initials:
                name = f"{fe} {i}.wav"
                lines.append(f"{name}={vc_tpl['offset']},{vc_tpl['consonant']},{vc_tpl['cutoff']},{vc_tpl['preutterance']},{vc_tpl['overlap']}")
    return lines


def generate_vcv_oto(lang: str) -> List[str]:
    """生成 VCV 类型 oto.ini 内容。"""
    if lang not in VCV_TEMPLATES:
        raise ValueError(f"语言 {lang} 暂不支持 VCV oto 生成")
    tpl = VCV_TEMPLATES[lang]
    lines = []
    if lang == "ja":
        vows = ["a", "i", "u", "e", "o"]
        cons = ["", "k", "s", "sh", "t", "ch", "ts", "n", "h", "f", "m", "y", "r", "w",
                "g", "z", "j", "d", "b", "p"]
        # 词首
        ht = tpl["head"]
        for c in cons:
            for v in vows:
                name = f"- {c}{v}.wav" if c else f"- {v}.wav"
                lines.append(f"{name}={ht['offset']},{ht['consonant']},{ht['cutoff']},{ht['preutterance']},{ht['overlap']}")
        # VCV
        dt = tpl["default"]
        for pv in vows:
            for c in cons:
                for v in vows:
                    name = f"{pv} {c}{v}.wav" if c else f"{pv} {v}.wav"
                    lines.append(f"{name}={dt['offset']},{dt['consonant']},{dt['cutoff']},{dt['preutterance']},{dt['overlap']}")
    return lines


def parse_oto(path: Path) -> Dict[str, str]:
    """解析 oto.ini 为字典。"""
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if "=" in line:
            name, params = line.split("=", 1)
            result[name.strip()] = params.strip()
    return result


def adjust_oto(base_path: Path, adjustments_path: Path, output_path: Path) -> None:
    """基于 JSON 调整文件批量修改 oto。"""
    base = parse_oto(base_path)
    adj = json.loads(adjustments_path.read_text(encoding="utf-8"))

    # adj format: {"suffix_or_prefix": {"offset": 10, "preutterance": -5, ...}}
    result = []
    for name, params in base.items():
        parts = params.split(",")
        # Ensure 5 parts minimum
        while len(parts) < 5:
            parts.append("0")

        applied = False
        for key, deltas in adj.items():
            if name.startswith(key) or name.endswith(key) or key in name:
                if "offset" in deltas:
                    parts[0] = str(float(parts[0]) + float(deltas["offset"]))
                if "consonant" in deltas:
                    parts[1] = str(float(parts[1]) + float(deltas["consonant"]))
                if "cutoff" in deltas:
                    parts[2] = str(float(parts[2]) + float(deltas["cutoff"]))
                if "preutterance" in deltas:
                    parts[3] = str(float(parts[3]) + float(deltas["preutterance"]))
                if "overlap" in deltas:
                    parts[4] = str(float(parts[4]) + float(deltas["overlap"]))
                applied = True

        result.append(f"{name}={','.join(parts)}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(result) + "\n", encoding="utf-8")
    print(f"已生成调整后的 oto: {output_path} ({len(result)} 行)")


def main() -> int:
    parser = argparse.ArgumentParser(description="oto.ini 批量生成器")
    sub = parser.add_subparsers(dest="command")

    # generate
    gen = sub.add_parser("generate", help="从模板生成 oto.ini")
    gen.add_argument("--type", "-t", required=True, choices=["cv", "vcv", "cvvc"])
    gen.add_argument("--lang", "-l", required=True, choices=["ja", "zh", "en"])
    gen.add_argument("--output", "-o", required=True)

    # adjust
    adj = sub.add_parser("adjust", help="基于调整文件修改已有 oto.ini")
    adj.add_argument("--base", "-b", required=True, help="基础 oto.ini")
    adj.add_argument("--adjustments", "-a", required=True, help="JSON 调整文件")
    adj.add_argument("--output", "-o", required=True)

    args = parser.parse_args()

    if args.command == "generate":
        try:
            if args.type == "cv":
                lines = generate_cv_oto(args.lang)
            elif args.type == "cvvc":
                lines = generate_cvvc_oto(args.lang)
            elif args.type == "vcv":
                lines = generate_vcv_oto(args.lang)
            else:
                print(f"不支持类型: {args.type}", file=sys.stderr)
                return 1
        except ValueError as e:
            print(f"错误: {e}", file=sys.stderr)
            return 1

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"已生成 oto.ini: {output_path} ({len(lines)} 行)")
        return 0

    elif args.command == "adjust":
        adjust_oto(Path(args.base), Path(args.adjustments), Path(args.output))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
