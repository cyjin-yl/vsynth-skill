#!/usr/bin/env python3
"""
VPR 跨语种音素映射工具 — 将 VPR 中的拼音歌词批量映射为目标语言的音素

用法:
    python vpr_cross_language.py <vpr_file> --map ja --output fixed.vpr
    python vpr_cross_language.py <vpr_file> --map-file mymap.json --output fixed.vpr
    python vpr_cross_language.py <vpr_file> --map ja --protect --track 0 --output fixed.vpr

功能:
    - 读取 VPR 中所有音符的 lyric（拼音），根据映射表查找对应的目标语言音素
    - 将 phoneme 字段替换为目标音素
    - 可选设置 isProtected=true（防止在编辑器内修改歌词时丢失音素）
    - 支持轨道筛选、试听预览（dry-run）
    - 支持自定义 JSON 映射文件

说明:
    - 直接修改 JSON 的 phoneme 字段后，V6 加载时会直接使用该值，与 isProtected 无关
    - isProtected 只影响编辑器 UI 内的歌词修改行为
    - 输出时建议使用新文件名，避免 V6 编辑器缓存

支持的预设映射:
    ja  — 中文拼音 → 日文 X-SAMPA（日语音库唱中文）
    en  — 中文拼音 → 英文 X-SAMPA（英语音库唱中文）

映射文件格式 (JSON):
    {
      "description": "拼音到日语音素映射",
      "lang_code": "ja",
      "mapping": {
        "a": "a",
        "ai": "a j",
        "an": "a n",
        "ba": "b a",
        "bi": "b' i",
        ...
      }
    }

跨语种核心规则:
    1. lyric 保持拼音（用于编辑器显示和字典索引）
    2. phoneme 替换为目标语言音素（实际控制发音）
    3. isProtected = true（V6 必备，防止自动覆盖）
"""

import argparse
import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# =============================================================================
# 预设映射表：中文拼音 → 日文 X-SAMPA
# 基于 ChnToJpn.lua、ENG to JPN Phoneme Converter.lua 和 V6 实际格式整理
# =============================================================================

PINYIN_TO_JAPANESE: Dict[str, str] = {
    # === 单韵母 ===
    "a": "a",      # あ
    "o": "o",      # お
    "e": "e",      # え
    "i": "i",      # い
    "u": "M",      # う
    "ü": "M",      # 无 ü，用 う 近似

    # === 复韵母 ===
    "ai": "a j",   # あい
    "ei": "e j",   # えい
    "ao": "a w",   # あお
    "ou": "o w",   # おう
    "an": "a n",   # あん
    "en": "e n",   # えん
    "in": "i n",   # いん
    "un": "M n",   # うん (uen)
    "ün": "M n",   # うん
    "ang": "a N",  # あんぐ
    "eng": "o N",  # おんぐ近似
    "ing": "i N",  # いんぐ
    "ong": "o N",  # おんぐ

    # === 带 i 介音 ===
    "ia": "j a",
    "ie": "j e",
    "iao": "j a w",
    "iu": "j o w",   # iou
    "ian": "j a n",
    "iang": "j a N",
    "iong": "j o N",

    # === 带 u 介音 ===
    "ua": "w a",
    "uo": "w o",
    "uai": "w a j",
    "ui": "w e j",   # uei
    "uan": "w a n",
    "uang": "w a N",

    # === 带 ü 介音 ===
    "üe": "j e",     # yue → j e
    "üan": "j a n",  # yuan → j a n

    # === 整体认读 ===
    "zhi": "tS i",
    "chi": "tS i",
    "shi": "S i",
    "ri": "4 i",
    "zi": "dz i",
    "ci": "ts i",
    "si": "s i",
    "yi": "i",
    "wu": "M",
    "yu": "j M",      # V6 自动识别为 j M（ゆ）
    "yue": "j e",
    "yuan": "j a n",
    "yun": "i n",

    # === 零声母 y/w 开头 ===
    "ya": "j a",
    "ye": "j e",
    "yao": "j a w",
    "you": "j o w",
    "yan": "j a n",
    "yin": "j i n",
    "yang": "j a N",
    "ying": "j i N",
    "yong": "j o N",
    "wa": "w a",
    "wo": "w o",
    "wai": "w a j",
    "wei": "w e j",
    "wan": "w a n",
    "wen": "w e n",
    "wang": "w a N",
    "weng": "w e N",

    # === 声母 b ===
    "ba": "b a",
    "bo": "b o",
    "bi": "b' i",     # 腭化
    "bai": "b a j",
    "bei": "b e j",
    "bao": "b a w",
    "ban": "b a n",
    "ben": "b e n",
    "bin": "b' i n",  # 腭化
    "bing": "b' i N",
    "bie": "b' j e",
    "biao": "b' j a w",
    "bian": "b' j a n",
    "bu": "b M",

    # === 声母 p ===
    "pa": "p a",
    "peng": "p o N",
    "po": "p o",
    "pi": "p' i",     # 腭化
    "pai": "p a j",
    "pei": "p e j",
    "pao": "p a w",
    "pou": "p o w",
    "pan": "p a n",
    "pen": "p e n",
    "pin": "p' i n",
    "ping": "p' i N",
    "pie": "p' j e",
    "piao": "p' j a w",
    "pian": "p' j a n",
    "pu": "p M",

    # === 声母 m ===
    "ma": "m a",
    "mo": "m o",
    "me": "m e",
    "mi": "m' i",     # 腭化
    "mai": "m a j",
    "mei": "m e j",
    "mao": "m a w",
    "mou": "m o w",
    "man": "m a n",
    "men": "m e n",
    "min": "m' i n",
    "ming": "m' i N",
    "mie": "m' j e",
    "miao": "m' a w", # 腭化 + 韵母 iao → a w（j 被吸收）
    "mian": "m' j a n",
    "mu": "m M",

    # === 声母 f ===
    "fa": "p\\ a",
    "fo": "p\\ o",
    "fei": "p\\ e j",
    "fan": "p\\ a n",
    "fen": "p\\ e n",
    "fang": "p\\ a N",
    "feng": "p\\ o N",
    "fu": "p\\ M",
    "fou": "p\\ o w",

    # === 声母 d ===
    "da": "d a",
    "de": "d e",
    "di": "d' i",     # 腭化（V6 自动识别格式）
    "dai": "d a j",
    "dao": "d a w",
    "dou": "d o w",
    "dan": "d a n",
    "dang": "d a N",
    "deng": "d o N",
    "dong": "d o N",
    "dun": "d M n",
    "die": "d' j e",
    "diao": "d' j a w",
    "dian": "d' j a n",
    "ding": "d' i N",
    "du": "d M",
    "duo": "d w o",
    "dui": "d w e j",
    "duan": "d w a n",
    "dui": "d w e j",

    # === 声母 t ===
    "ta": "t a",
    "te": "t e",
    "ti": "t' i",     # 腭化
    "tai": "t a j",
    "tao": "t a w",
    "tou": "t o w",
    "tan": "t a n",
    "tang": "t a N",
    "teng": "t o N",
    "tong": "t o N",
    "tun": "t M n",
    "tie": "t' j e",
    "tiao": "t' j a w",
    "tian": "t' j a n",
    "ting": "t' i N",
    "tu": "t M",
    "tuo": "t w o",
    "tui": "t w e j",
    "tuan": "t w a n",

    # === 声母 n ===
    "na": "n a",
    "neng": "n o N",
    "ne": "n e",
    "ni": "J i",      # 硬腭鼻音
    "nai": "n a j",
    "nei": "n e j",
    "nao": "n a w",
    "nou": "n o w",
    "nan": "n a n",
    "nen": "n e n",
    "nin": "J i n",
    "ning": "J i N",
    "nie": "J e",
    "niao": "J a w",
    "nian": "J a n",
    "niang": "J a N",
    "nu": "n M",
    "nuo": "n w o",
    "nü": "J M",
    "nüe": "J e",
    "nong": "n o N",

    # === 声母 l ===
    "la": "4 a",
    "le": "4 e",
    "li": "4 i",
    "lai": "4 a j",
    "lei": "4 e j",
    "lao": "4 a w",
    "lou": "4 o w",
    "lan": "4 a n",
    "lang": "4 a N",
    "leng": "4 o N",
    "lin": "4 i n",
    "ling": "4 i N",
    "lie": "4 j e",
    "liao": "4 a w",
    "lian": "4 j a n",
    "liang": "4 j a N",
    "lu": "4 M",
    "luo": "4 w o",
    "lü": "4 M",
    "lüe": "4 j e",
    "luan": "4 w a n",
    "lun": "4 M n",
    "long": "4 o N",

    # === 声母 g ===
    "ga": "g a",
    "ge": "g e",
    "gai": "g a j",
    "gei": "g e j",
    "gao": "g a w",
    "gou": "g o w",
    "gan": "g a n",
    "gen": "g e n",
    "gang": "g a N",
    "geng": "g o N",
    "gong": "g o N",
    "gu": "g M",
    "gua": "g w a",
    "guo": "g w o",
    "guai": "g w a j",
    "gui": "g w e j",
    "guan": "g w a n",
    "gun": "g M n",
    "guang": "g w a N",

    # === 声母 k ===
    "ka": "k a",
    "ke": "k e",
    "kai": "k a j",
    "kao": "k a w",
    "kou": "k o w",
    "kan": "k a n",
    "ken": "k e n",
    "kang": "k a N",
    "keng": "k o N",
    "kong": "k o N",
    "ku": "k M",
    "kua": "k w a",
    "kuo": "k w o",
    "kuai": "k w a j",
    "kui": "k w e j",
    "kuan": "k w a n",
    "kun": "k M n",
    "kuang": "k w a N",

    # === 声母 h ===
    "ha": "h a",
    "he": "h e",
    "hai": "h a j",
    "hei": "h e j",
    "hao": "h a w",
    "hou": "h o w",
    "han": "h a n",
    "hen": "h e n",
    "hang": "h a N",
    "heng": "h o N",
    "hong": "h o N",
    "hu": "h M",
    "hua": "h w a",
    "huo": "h w o",
    "huai": "h w a j",
    "hui": "h w e j",
    "huan": "h w a n",
    "hun": "h M n",
    "huang": "h w a N",

    # === 声母 j ===
    "ji": "dZ i",
    "jia": "dZ j a",
    "jie": "dZ j e",
    "jiao": "dZ j a w",
    "jiu": "dZ j o w",
    "jian": "dZ j a n",
    "jin": "dZ i n",
    "jiang": "dZ j a N",
    "jing": "dZ i N",
    "jiong": "dZ j o N",
    "jue": "dZ j e",      # üe 修正
    "juan": "dZ j a n",   # üan 修正
    "ju": "dZ M",
    "jun": "dZ M n",

    # === 声母 q ===
    "qi": "tS i",
    "qia": "tS j a",
    "qie": "tS j e",
    "qiao": "tS j a w",
    "qiu": "tS j o w",
    "qian": "tS j a n",
    "qin": "tS i n",
    "qiang": "tS j a N",
    "qing": "tS i N",
    "qiong": "tS j o N",
    "que": "tS j e",
    "quan": "tS j a n",
    "qu": "tS M",
    "qun": "tS M n",

    # === 声母 x ===
    "xi": "S i",
    "xia": "S j a",
    "xie": "S j e",
    "xiao": "S j a w",
    "xiu": "S j o w",
    "xian": "S j a n",
    "xin": "S i n",
    "xiang": "S j a N",
    "xing": "S i N",
    "xiong": "S j o N",
    "xue": "S j e",
    "xuan": "S j a n",
    "xu": "S M",
    "xun": "S M n",

    # === 声母 zh ===
    "zha": "ts a",
    "zhe": "ts e",
    "zhi": "ts i",
    "zhu": "ts M",
    "zhai": "ts a j",
    "zhao": "ts a w",
    "zhou": "ts o w",
    "zhan": "ts a n",
    "zhen": "ts e n",
    "zhang": "ts a N",
    "zheng": "ts o N",
    "zhong": "ts o N",
    "zhua": "ts w a",
    "zhuo": "ts w o",
    "zhuai": "ts w a j",
    "zhui": "ts w e j",
    "zhuan": "ts w a n",
    "zhun": "ts M n",
    "zhuang": "ts w a N",

    # === 声母 ch ===
    "cha": "ts_h a",
    "che": "ts_h e",
    "chi": "ts_h i",
    "chu": "ts_h M",
    "chai": "ts_h a j",
    "chao": "ts_h a w",
    "chou": "ts_h o w",
    "chan": "ts_h a n",
    "chen": "ts_h e n",
    "chang": "ts_h a N",
    "cheng": "ts_h o N",
    "chong": "ts_h o N",
    "chuo": "ts_h w o",
    "chuai": "ts_h w a j",
    "chui": "ts_h w e j",
    "chuan": "ts_h w a n",
    "chun": "ts_h M n",
    "chuang": "ts_h w a N",

    # === 声母 sh ===
    "sha": "s a",
    "she": "s e",
    "shi": "s i",
    "shu": "s M",
    "shai": "s a j",
    "shao": "s a w",
    "shou": "s o w",
    "shan": "s a n",
    "shen": "s e n",
    "shang": "s a N",
    "sheng": "s o N",
    "shuo": "s w o",
    "shuai": "s w a j",
    "shui": "s w e j",
    "shuan": "s w a n",
    "shun": "s M n",
    "shuang": "s w a N",

    # === 声母 r ===
    "re": "4 e",
    "ri": "4 i",
    "ru": "4 M",
    "rao": "4 a w",
    "rou": "4 o w",
    "ran": "4 a n",
    "ren": "4 e n",
    "rang": "4 a N",
    "reng": "4 o N",
    "ruo": "4 w o",
    "rui": "4 w e j",
    "ruan": "4 w a n",
    "run": "4 M n",
    "rong": "4 o N",

    # === 声母 z ===
    "za": "dz a",
    "ze": "dz e",
    "zi": "dz i",
    "zai": "dz a j",
    "zao": "dz a w",
    "zou": "dz o w",
    "zan": "dz a n",
    "zen": "dz e n",
    "zang": "dz a N",
    "zeng": "dz o N",
    "zong": "dz o N",
    "zu": "dz M",
    "zuo": "dz w o",
    "zui": "dz w e j",
    "zuan": "dz w a n",
    "zun": "dz M n",

    # === 声母 c ===
    "ca": "ts a",
    "ce": "ts e",
    "ci": "ts i",
    "cai": "ts a j",
    "cao": "ts a w",
    "cou": "ts o w",
    "can": "ts a n",
    "cen": "ts e n",
    "cang": "ts a N",
    "ceng": "ts o N",
    "cong": "ts o N",
    "cu": "ts M",
    "cuo": "ts w o",
    "cui": "ts w e j",
    "cuan": "ts w a n",
    "cun": "ts M n",

    # === 声母 s ===
    "sa": "s a",
    "se": "s e",
    "si": "s i",
    "sai": "s a j",
    "sao": "s a w",
    "sou": "s o w",
    "san": "s a n",
    "sen": "s e n",
    "sang": "s a N",
    "seng": "s o N",
    "song": "s o N",
    "su": "s M",
    "suo": "s w o",
    "sui": "s w e j",
    "suan": "s w a n",
    "sun": "s M n",

    # === 特殊 ===
    "er": "a",       # 日语音库无卷舌，用 a 近似
    "-": "-",        # 延长符
    "R": "R",        # 休止符
}


def load_mapping(preset: Optional[str] = None, map_file: Optional[Path] = None) -> Dict[str, str]:
    """加载映射表。"""
    if map_file:
        data = json.loads(map_file.read_text(encoding="utf-8"))
        mapping = data.get("mapping", data)
        return mapping

    if preset == "ja":
        return PINYIN_TO_JAPANESE.copy()

    if preset == "en":
        # 英语映射待扩展
        raise NotImplementedError("英语映射尚未实现，请使用 --map-file 提供自定义映射")

    raise ValueError(f"未知预设映射: {preset}")


def apply_mapping_to_vpr(
    vpr_path: Path,
    mapping: Dict[str, str],
    output_path: Optional[Path] = None,
    protect: bool = True,
    track_filter: Optional[int] = None,
    dry_run: bool = False,
    unmatched_policy: str = "warn",
) -> Dict[str, Any]:
    """将映射应用到 VPR 文件。"""

    with zipfile.ZipFile(vpr_path, "r") as zf:
        seq = json.loads(zf.read("Project/sequence.json").decode("utf-8"))

    stats = {
        "total_notes": 0,
        "mapped": 0,
        "skipped": 0,
        "unmatched": 0,
        "protected_set": 0,
        "phoneme_changed": 0,
        "unmatched_lyrics": [],
        "changes_preview": [],
    }

    for tidx, track in enumerate(seq.get("tracks", [])):
        if track_filter is not None and tidx != track_filter:
            continue

        for part in track.get("parts", []):
            for note in part.get("notes", []):
                lyric = note.get("lyric", "")
                old_phoneme = note.get("phoneme", "")

                stats["total_notes"] += 1

                if not lyric:
                    stats["skipped"] += 1
                    continue

                # 查找映射
                new_phoneme = mapping.get(lyric)

                if new_phoneme is None:
                    stats["unmatched"] += 1
                    if len(stats["unmatched_lyrics"]) < 50:
                        stats["unmatched_lyrics"].append(lyric)
                    if unmatched_policy == "skip":
                        continue
                    # 默认 warn: 保留原音素，但记录
                    new_phoneme = old_phoneme

                # 应用音素
                if new_phoneme != old_phoneme:
                    note["phoneme"] = new_phoneme
                    stats["phoneme_changed"] += 1
                    if len(stats["changes_preview"]) < 20:
                        stats["changes_preview"].append({
                            "track": tidx,
                            "lyric": lyric,
                            "old": old_phoneme,
                            "new": new_phoneme,
                        })

                # 设置 isProtected
                if protect:
                    if note.get("isProtected") != True:
                        note["isProtected"] = True
                        stats["protected_set"] += 1

                stats["mapped"] += 1

    if not dry_run:
        # 重新打包 VPR
        tmp_dir = Path(tempfile.mkdtemp())
        try:
            # 写入新 sequence.json
            seq_dir = tmp_dir / "Project"
            seq_dir.mkdir(parents=True, exist_ok=True)
            (seq_dir / "sequence.json").write_text(
                json.dumps(seq, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            # 复制其他 ZIP 成员
            with zipfile.ZipFile(vpr_path, "r") as zf_in:
                for item in zf_in.infolist():
                    if item.filename != "Project/sequence.json":
                        zf_in.extract(item, tmp_dir)

            # 打包
            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf_out:
                for path in tmp_dir.rglob("*"):
                    if path.is_file():
                        arcname = str(path.relative_to(tmp_dir)).replace("\\", "/")
                        zf_out.write(path, arcname)

        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    return stats


def main() -> int:
    parser = argparse.ArgumentParser(
        description="VPR 跨语种音素映射工具 — 批量将拼音歌词映射为目标语言音素",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s song.vpr --map ja --output fixed.vpr
  %(prog)s song.vpr --map ja --protect --dry-run        # 预览映射结果
  %(prog)s song.vpr --map ja --track 0 --output t0.vpr  # 只处理轨道0
  %(prog)s song.vpr --map-file mymap.json --output out.vpr
  %(prog)s song.vpr --map ja --unmatched skip --output fixed.vpr  # 跳过未映射
        """,
    )
    parser.add_argument("file", nargs="?", default=None, help="输入 VPR 文件路径（导出映射时可省略）")
    parser.add_argument("--output", "-o", default=None, help="输出 VPR 文件路径")
    parser.add_argument("--map", choices=["ja", "en"], default=None, help="使用内置预设映射")
    parser.add_argument("--map-file", type=Path, default=None, help="自定义 JSON 映射文件路径")
    parser.add_argument("--protect", action="store_true", default=True, help="设置 isProtected=true（防止编辑器内改歌词时丢失音素，默认启用）")
    parser.add_argument("--no-protect", action="store_true", help="不设置 isProtected（仅影响编辑器内歌词修改行为）")
    parser.add_argument("--track", type=int, default=None, help="只处理指定轨道索引")
    parser.add_argument("--dry-run", action="store_true", help="只预览修改，不写入文件")
    parser.add_argument("--unmatched", choices=["warn", "skip", "error"], default="warn",
                        help="遇到未映射歌词时的策略")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出结果")
    parser.add_argument("--export-map", type=Path, default=None,
                        help="导出内置映射表到 JSON 文件（仅导出，不处理 VPR）")

    args = parser.parse_args()

    # 导出映射表模式
    if args.export_map:
        mapping = PINYIN_TO_JAPANESE
        export_data = {
            "description": "中文拼音到日文 X-SAMPA 映射（日语音库跨语种唱中文）",
            "lang_code": "ja",
            "note": "基于 ChnToJpn.lua 和 VOCALOID 6 实际格式整理",
            "entry_count": len(mapping),
            "mapping": mapping,
        }
        args.export_map.write_text(json.dumps(export_data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已导出映射表到 {args.export_map}，共 {len(mapping)} 条")
        return 0

    # 导出映射表模式（不需要 VPR 文件）
    if args.export_map:
        mapping = PINYIN_TO_JAPANESE
        export_data = {
            "description": "中文拼音到日文 X-SAMPA 映射（日语音库跨语种唱中文）",
            "lang_code": "ja",
            "note": "基于 ChnToJpn.lua 和 VOCALOID 6 实际格式整理",
            "entry_count": len(mapping),
            "mapping": mapping,
        }
        Path(args.export_map).write_text(json.dumps(export_data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已导出映射表到 {args.export_map}，共 {len(mapping)} 条")
        return 0

    # 验证参数
    if not args.file:
        print("错误: 必须指定输入 VPR 文件路径", file=sys.stderr)
        return 1

    if not args.map and not args.map_file:
        print("错误: 必须指定 --map 或 --map-file", file=sys.stderr)
        return 1

    vpr_path = Path(args.file)
    if not vpr_path.exists():
        print(f"错误: 文件不存在 {vpr_path}", file=sys.stderr)
        return 1

    # 加载映射
    try:
        mapping = load_mapping(preset=args.map, map_file=args.map_file)
    except Exception as e:
        print(f"错误: 加载映射失败: {e}", file=sys.stderr)
        return 1

    protect = args.protect and not args.no_protect

    # 应用映射
    try:
        out_path = Path(args.output) if args.output else None
        stats = apply_mapping_to_vpr(
            vpr_path=vpr_path,
            mapping=mapping,
            output_path=out_path,
            protect=protect,
            track_filter=args.track,
            dry_run=args.dry_run,
            unmatched_policy=args.unmatched,
        )
    except Exception as e:
        print(f"错误: 处理 VPR 失败: {e}", file=sys.stderr)
        return 1

    # 输出结果
    if args.json:
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    else:
        print("=" * 50)
        print("跨语种音素映射结果")
        print("=" * 50)
        print(f"输入:  {vpr_path}")
        print(f"输出:  {args.output}")
        print(f"映射:  {args.map or args.map_file} ({len(mapping)} 条规则)")
        print(f"\n总音符:     {stats['total_notes']}")
        print(f"成功映射:   {stats['mapped']}")
        print(f"音素变更:   {stats['phoneme_changed']}")
        print(f"isProtected: {stats['protected_set']} 个已锁定")
        print(f"未匹配:     {stats['unmatched']} ({len(set(stats['unmatched_lyrics']))} 种唯一)")
        if stats['unmatched_lyrics']:
            unique_unmatched = sorted(set(stats['unmatched_lyrics']))
            print(f"\n未映射歌词 ({len(unique_unmatched)} 种):")
            for lyric in unique_unmatched[:30]:
                print(f"  - {lyric}")
            if len(unique_unmatched) > 30:
                print(f"  ... 等共 {len(unique_unmatched)} 种")

        if stats["changes_preview"]:
            print(f"\n变更预览 (前 {len(stats['changes_preview'])} 个):")
            for ch in stats["changes_preview"]:
                print(f"  [{ch['track']}] {ch['lyric']}: '{ch['old']}' → '{ch['new']}'")

        if args.dry_run:
            print("\n⚠️  这是预览模式 (dry-run)，未实际写入文件")
        else:
            print(f"\n✓ 已保存到 {args.output}")
        print("=" * 50)

    return 0


if __name__ == "__main__":
    sys.exit(main())
