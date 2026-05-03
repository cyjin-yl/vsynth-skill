<div align="center">

# vsynth-skill

> *"终于不用手工灌词啦！他娘的 Tab 键我要按烂了；；"*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

<br>

跨 15+ 格式的歌声合成工程编辑 Skill<br>
让 AI Agent 真正读懂 VOCALOID / UTAU / SynthV / CeVIO / ACE Studio 的工程文件<br>
然后帮你批量调 pitch、改歌词、拆音素、转格式、验证文件完整性

[安装](#安装) · [快速开始](#快速开始) · [支持格式](#支持格式) · [CLI 命令](#cli-命令) · [项目结构](#项目结构)

</div>

---

## 安装

### Claude Code

```bash
# 安装到当前项目（在 git 仓库根目录执行）
mkdir -p .claude/skills
git clone https://github.com/255doesnotexist/vsynth-skill .claude/skills/vsynth

# 或安装到全局（所有项目都能用）
git clone https://github.com/255doesnotexist/vsynth-skill ~/.claude/skills/vsynth
```

### 依赖

```bash
pip install ruamel.yaml zstandard
```

---

## 快速开始

在 Claude Code 中对话：

```
你: 打开这个 .svp 工程，把第三小节的歌词改成「月光」，然后验证文件
```

Agent 会自动：检测格式 → 解析工程 → 定位音符 → 修改歌词 → 调用 CLI 验证

```
你: 把这个 .ust 转成 SynthV 的 .svp 格式
```

Agent 会自动：解析 UTAU 工程 → 映射时间系统（ticks → blicks）→ 映射参数（PBY → pitchDelta）→ 生成 .svp 
【不太稳定，不建议这么用。你不是有 utaformatix 吗？不过 Agent 有时候能把气声参数写脚本一起迁移到另一个版本软件的工程里。这可能有点用。】

```
你: 给这段副歌加点气声和颤音
```

Agent 会读取 `references/tuning.md`，按引擎类型（VOCALOID 的 DYN+PBS / SynthV 的 loudness+vibrato）生成对应参数曲线。
【别这么干，小心颤音抖得没边了！】

以上均为模仿某个 Skill 炒作仓库写的不代表本仓库实际功能哈 over。

---

## 支持格式

| 软件 | 扩展名 | 格式类型 | 状态 |
|------|--------|----------|------|
| VOCALOID 2 | `.vsq` | SMF + INI | Legacy |
| VOCALOID 3/4 | `.vsqx` | XML (vsq3/vsq4) | Active |
| VOCALOID 5/6 | `.vpr` | ZIP + JSON | Active |
| UTAU | `.ust` | INI-like text | Active |
| OpenUtau | `.ustx` | YAML 1.2 | Active |
| Synthesizer V Studio | `.svp` | JSON (blick time) | Active |
| Synthesizer V Editor | `.s5p` | JSON (legacy) | Discontinued |
| CeVIO / VoiSona | `.ccs` / `.ccst` | XML | Active |
| ACE Studio | `.acep` | zstd + JSON | Active |
| DiffSinger | `.ds` | JSON | Active |
| Piapro Studio NT | `.ppsf` | JSON + ZIP | Active |
| NEUTRINO | `.musicxml` | MusicXML | Active |
| DeepVocal | `.dv` | Custom binary | Discontinued |
| Standard MIDI | `.mid` | SMF | Universal |

---

## 核心能力

### 解析 & 验证

- 自动检测文件格式（按扩展名）
- 解析工程元数据：音符、轨道、节拍、参数
- 校验文件结构完整性
- 支持 Shift-JIS / UTF-8 / UTF-8 BOM 编码自动检测

### 编辑操作

- **歌词编辑** — 全格式歌词修改
- **音高曲线** — PIT / PBS / PBW / pitchDelta 编辑
- **力度控制** — DYN / loudness / VEL 调节
- **颤音参数** — vibrato depth / rate / frequency / delay
- **音素拆分** — 改善咬字清晰度
- **轨道拆分** — 多轨编排与和声
- **特殊记号** — Asp、Sil、br、cl、-、R 等

### 生成 & 创建

- 创建空白工程模板（.ust / .ustx / .vsqx / .svp）
- 生成 UTAU 录音表（reclist）：CV / VCV / CVVC / CVVX / VCCV
- 生成 oto.ini 模板

### 跨格式转换

- 格式间的参数自动映射：
  - 时间系统：VOCALOID ticks ↔ SynthV blicks ↔ CeVIO clocks
  - 音高系统：PIT×PBS/8191 ↔ SynthV cents ↔ UTAU PBY×10
  - 力度系统：VOCALOID DYN 0-127 ↔ SynthV dB

### 调音技术

- 颤音（vibrato）技巧
- 滑音（portamento / glide）
- 气息控制（breath / expression）
- 跨语言演唱（中文 ↔ 日文 ↔ 英文）
- 音源缺陷识别与修复策略【待贡献完善】
- XSY（Cross-Synthesis）策略

---

## CLI 命令

```bash
# 校验工程文件
python -m vsynth.scripts.cli validate <file> [--verbose]

# 查看工程信息
python -m vsynth.scripts.cli info <file>

# 检测文件格式
python -m vsynth.scripts.cli detect <file>

# 提取容器内容（.vpr → ZIP，.acep → zstd JSON）
python -m vsynth.scripts.cli extract <file> --output <dir>

# 列出所有支持格式
python -m vsynth.scripts.cli list-formats

# 创建空白工程模板
python -m vsynth.scripts.cli create --format <type> --output <file>

# 生成录音表
python -m vsynth.scripts.cli generate reclist --type <type> --lang ja --output <file>

# 生成 oto.ini 模板
python -m vsynth.scripts.cli generate oto --type <type> --lang ja --output <file>
```

---

## 项目结构

本项目遵循 [AgentSkills](https://agentskills.io) 开放标准【那是什么？】：

```
vsynth/
├── SKILL.md                    # Skill 入口（官方 frontmatter）
├── references/                 # 参考文档（20 个文件）
│   ├── vocaloid.md             #   VOCALOID 格式规格（.vsq / .vsqx / .vpr）
│   ├── utau.md                 #   UTAU / OpenUtau 格式规格（.ust / .ustx）
│   ├── synthv.md               #   Synthesizer V 格式规格（.svp / .s5p）
│   ├── others.md               #   CeVIO / ACE / DiffSinger / NEUTRINO
│   ├── tuning.md               #   调音技巧与参数术语表
│   ├── notations.md            #   特殊音素记号处理
│   ├── phoneme_splitting.md    #   音素拆分技巧
│   ├── track_splitting.md      #   多轨编排策略
│   ├── voicebank_defects.md    #   音源缺陷识别与修复
│   ├── cross_language.md       #   跨语言演唱技巧
│   ├── vpr_cross_language.md   #   VPR 专项跨语言处理
│   ├── utau_voicebank.md       #   UTAU 音源制作/编辑
│   ├── oto_ini.md              #   oto.ini 配置与生成
│   ├── preprocessing.md        #   音频预处理流水线
│   ├── xsampa.md               #   X-SAMPA 音素系统参考
│   ├── xml_guidelines.md       #   XML 格式编辑规范
│   ├── json_guidelines.md      #   JSON 格式编辑规范
│   ├── yaml_guidelines.md      #   YAML 格式编辑规范
│   ├── ini_guidelines.md       #   INI 格式编辑规范
│   └── lessons_learned.md      #   最佳实践与踩坑记录
└── scripts/                    # Python CLI 工具集
    ├── cli.py                  #   主入口
    ├── base_parser.py          #   解析器基类
    ├── vsq_parser.py           #   VOCALOID .vsq 解析
    ├── vsqx_parser.py          #   VOCALOID .vsqx 解析
    ├── vpr_parser.py           #   VOCALOID .vpr 解析
    ├── vpr_cross_language.py   #   VPR 跨语言工具
    ├── vpr_phoneme_inspect.py  #   VPR 音素检查
    ├── vpr_phoneme_lock.py     #   VPR 音素锁定
    ├── ust_parser.py           #   UTAU .ust 解析
    ├── ustx_parser.py          #   OpenUtau .ustx 解析
    ├── svp_parser.py           #   SynthV .svp 解析
    ├── s5p_parser.py           #   SynthV .s5p 解析
    ├── ccs_parser.py           #   CeVIO .ccs 解析
    ├── acep_parser.py          #   ACE Studio .acep 解析
    ├── midi_parser.py          #   标准 MIDI 解析
    ├── reclist_generator.py    #   录音表生成
    ├── oto_generator.py        #   oto.ini 模板生成
    ├── utils.py                #   共用工具函数
    └── requirements.txt        #   依赖：ruamel.yaml, zstandard
```

---

## 技术架构

* 有毛线架构。全是 vibe 的。

### 解析器系统

- `BaseParser` 抽象基类定义统一接口
- 格式专属解析器继承 BaseParser
- 所有解析器输出标准化 JSON
- 注册表模式按扩展名自动选择解析器
- 支持模块执行和脚本直连两种方式

### 编码处理

- Shift-JIS ↔ UTF-8 自动检测
- UTF-8 BOM 正确处理
- XML 实体转义
- JSON NaN 处理（SynthV）
- YAML 缩进与 BOM 兼容（OpenUtau）

---

## 参考文档导航

| 文件 | 覆盖内容 | 何时读取 |
|------|----------|----------|
| `references/vocaloid.md` | .vsq / .vsqx / .vpr | 处理 VOCALOID 工程时 |
| `references/utau.md` | .ust / .ustx | 处理 UTAU / OpenUtau 工程时 |
| `references/synthv.md` | .svp / .s5p | 处理 Synthesizer V 工程时 |
| `references/others.md` | .ccs / .acep / .ds / .musicxml | 处理 CeVIO / ACE / DiffSinger 时 |
| `references/tuning.md` | 调音参数体系 | 需要调音技巧和参数对照时 |
| `references/cross_language.md` | 中日英跨语言音素 | 制作多语言歌曲时 |
| `references/voicebank_defects.md` | 音源问题诊断 | 音源出现杂音、音色崩坏时 |
| `references/lessons_learned.md` | 踩坑记录 | 编辑前必读 |

---

## 使用建议

- **先校验再编辑** — 每次修改后用 `validate` 命令确认文件完整
- **读 guidelines 再动手** — XML / JSON / YAML / INI 各有坑，编辑前先读对应规范
- **编码别猜** — Shift-JIS 和 UTF-8 的 .ust 都存在，用 `detect` 命令确认
- **跨格式转换注意映射** — 时间系统和音高系统不能直接搬运，需要转换公式
- **颤音别套模板** — 不同引擎的 vibrato 参数差异很大，参考 `tuning.md` 的引擎对照表

---

### 写在最后

这个 Skill 不会替你做音乐判断。它只是确保 AI 能读懂你选择的格式、尊重你选择的引擎、在你想批量改什么的时候不再对着工程文件发呆。

哦还有就是，填词的时候 AI 终于能读到气口、以及音调的升降在哪里了，因此可以写出更符合中文填词规矩的词。可喜可贺。可喜可贺。

MIT License
