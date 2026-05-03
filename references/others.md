# 其他歌声合成软件格式

> 涵盖 CeVIO、ACE Studio、Piapro Studio、NEUTRINO、DiffSinger、DeepVocal 等

---

## 目录

1. [CeVIO / VoiSona](#1-cevio--voisona)
2. [ACE Studio](#2-ace-studio)
3. [Piapro Studio](#3-piapro-studio)
4. [NEUTRINO](#4-neutrino)
5. [DiffSinger](#5-diffsinger)
6. [其他格式概览](#6-其他格式概览)
7. [格式转换兼容性](#7-格式转换兼容性)
8. [参考链接](#8-参考链接)

---

## 1. CeVIO / VoiSona

### 1.1 概况

CeVIO Creative Studio 是由 Techno-Speech 开发的歌声合成与语音合成软件，后续演进为 CeVIO AI 和 VoiSona。

| 软件 | 文件扩展名 | 说明 |
|------|-----------|------|
| CeVIO Creative Studio (Free) | `.ccs` | 项目文件（免费版） |
| CeVIO Creative Studio (商业版) | `.csv` | 项目文件（商业版） |
| CeVIO AI / VoiSona | `.ccs`, `.ccst` | 兼容导入/导出 |
| VoiSona (PC) | `.tssprj` | VoiSona 专有项目格式 |
| VoiSona (iOS/iPadOS) | `.tsmsln` | 移动端专有项目格式 |
| 时序标签 | `.lab` | 音频时序标签文件 |

### 1.2 .ccs / .ccst 格式

- **基本类型**：基于 **XML** 的标准序列化格式
- **编码**：Unicode 支持
- **内容**：包含会话轨道（Talk）、歌唱轨道（Song）、外部 WAV 轨道的数据
- **参数**：支持 VOL（音量）、PIT（音高）、ALP（音质）、HUS（huskiness）等参数调整
- `.ccs` = CeVIO Project（多轨道项目文件）
- `.ccst` = CeVIO Track（单轨道文件）

**LibSasara** 是 .NET 库，可解析 .ccs/.ccst 文件。

### 1.3 编辑注意事项

- CeVIO Creative Studio 免费版使用 `.ccs`，商业版改用 `.csv`
- VoiSona 可导入旧版 `.ccs` 文件
- 多轨道 `.ccs` 导入时可选择加载哪个轨道
- `TUNE` 参数在 VoiSona 的 `.ccs` 导入中尚不支持

---

## 2. ACE Studio

### 2.1 概况

ACE Studio 是由时域科技开发的 AI 歌声合成软件，前身为移动端 ACE 虚拟歌姬。提供 VST3 插件和独立桌面应用。

| 文件扩展名 | 说明 |
|-----------|------|
| `.acep` | ACE Studio 工程文件 |
| `.acedaw` | ACE-Step DAW 项目文件夹（未来格式） |

### 2.2 .acep 格式

- **基本类型**：基于 **JSON** 的标准序列化格式
- **压缩**：内容使用 **zstandard (zstd)** 压缩
- **加密历史**：
  - 公测期间曾使用 AES 加密 + base64 编码
  - 最终于 **1.7.8 版本移除加密**
- **当前状态**：活跃开发中

**处理流程**（现版本）：
1. 读取 .acep 文件
2. 使用 zstd 解压
3. 得到 JSON 内容
4. 解析和编辑

**历史加密流程**（旧版本）：
1. 原始 JSON 内容
2. zstandard 压缩
3. AES 加密
4. base64 编码 → 得到 `.acep` 文件

### 2.3 Python 处理示例

```python
import zstandard as zstd
import json

# 读取并解压 .acep
with open("project.acep", "rb") as f:
    compressed = f.read()

decompressor = zstd.ZstdDecompressor()
json_bytes = decompressor.decompress(compressed)
data = json.loads(json_bytes.decode("utf-8"))

# 编辑后重新压缩
json_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
compressor = zstd.ZstdCompressor()
compressed = compressor.compress(json_bytes)
with open("modified.acep", "wb") as f:
    f.write(compressed)
```

### 2.4 编辑注意事项

- 公测版 `.acep` 曾有加密，需用解密脚本处理旧文件
- 1.7.8 后版本无加密，zstd 解压即可得 JSON
- 桌面版工程文件目录：`%userprofile%\ACE_Studio\project`

---

## 3. Piapro Studio

### 3.1 概况

Piapro Studio 是 Crypton Future Media 开发的 VOCALOID 配套编辑器，随 Crypton 旗下虚拟歌手捆绑发布。

| 版本 | 文件扩展名 | 说明 |
|------|-----------|------|
| Piapro Studio (旧版) | `.ppsf` | 自定义二进制格式 |
| Piapro Studio NT / NT2 | `.ppsf` | 基于 JSON + zip 压缩 |

### 3.2 文件格式

#### 旧版 `.ppsf`
- **基本类型**：自定义二进制格式
- 逆向工程难度较高

#### NT 版 `.ppsf`
- **基本类型**：混合类型
- **结构**：基于 **JSON**，并使用 **zip 压缩**
- 类似 VPR 的 ZIP 容器结构

### 3.3 支持的导入格式
- VOCALOID1 MIDI 文件
- 标准 MIDI 文件
- `.ppsf` proprietary 格式

---

## 4. NEUTRINO

### 4.1 概况

NEUTRINO 是由 SHACHI 开发的日本神经网络歌声合成软件。使用扩散模型（Muon v2.x）。

| 输入格式 | 说明 |
|---------|------|
| `.musicxml` | 标准乐谱输入格式 |
| `.ust` → `.musicxml` | 通过 UtaFormatix 转换 |

| 输出格式 | 说明 |
|---------|------|
| `.wav` | 合成音频 |

### 4.2 MusicXML 输入格式

NEUTRINO 读取 MusicXML 格式并输出 WAV。MusicXML 可通过以下软件创建：
- Symphony Pro
- Cadencii
- MuseScore
- Finale NotePad
- UtaFormatix

**MusicXML 歌词规则**：
- 仅支持 **平假名** 或 **片假名** 歌词
- 不支持英语/字母歌词
- 所有音符必须输入歌词，空白歌词会报错

**特殊符号**：
- `'`：母音脱落（仅发子音）
- `ー`：重复前一个母音
- 促音 `っ` 单独使用时按 "前音符母音 + っ" 处理

**有效乐谱信息**：
- 音高、音符长、タイ（Tie）、ブレス記号、調号

**无效乐谱信息（被忽略）**：
- スラー、スタッカート、アクセント、強弱記号、速度記号

### 4.3 编辑注意事项

- 1 个短语过长（8~10 秒以上）会导致声音不稳定
- 建议在适当位置插入休符/ブレス分断短语
- ファイル名建议使用字母、数字、连接符和下划线

---

## 5. DiffSinger

### 5.1 概况

DiffSinger 是由上海交通大学等研究机构开发的基于浅层扩散机制的歌声合成系统（AAAI 2022）。OpenVPI 社区维护活跃分支。

| 文件扩展名 | 说明 |
|-----------|------|
| `.ds` | DiffSinger 工程/推理文件 |
| `.yaml` | 配置文件 |
| `.csv` | 训练数据转录文件 |

### 5.2 .ds 格式

- **基本类型**：基于 **JSON** 的标准序列化格式
- **性质**：临时解决方案，用于推理和测试评估
- **内容**：包含音素序列、音素时长、乐谱或曲线参数
- **注意**：`.ds` 文件本质上是改了后缀的 JSON 文件

#### JSON 结构示例

```json
[
  {
    "offset": 7.0,
    "text": "AP 试 着 SP 掬 一 把 星 辰 SP 在 手 心 SP",
    "ph_seq": "AP sh ir zh e SP j v y i b a x in ch en SP z ai sh ou x in SP",
    "ph_dur": "0.3947 0.209 0.2554 0.1509 0.5921 0.1045 ...",
    "ph_num": "2 2 1 2 2 2 2 2 1 2 2 2 1 1",
    "note_seq": "rest D#3 C4 rest D#4 C4 A#3 C4 C4 rest D#3 G3 G#3 rest",
    "note_dur": "0.6 0.4 0.6 0.2 0.4 0.4 0.4 0.2 0.4 0.2 0.4 0.6 1.0 0.05",
    "note_slur": "0 0 0 0 0 0 0 0 0 0 0 0 0 0",
    "f0_seq": "160.3 160.3 160.3 ...",
    "f0_timestep": "0.005"
  }
]
```

#### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `offset` | float | 片段起始时间（秒） |
| `text` | string | 歌词文本 |
| `ph_seq` | string | 音素序列（空格分隔） |
| `ph_dur` | string | 音素时长序列（秒，空格分隔） |
| `ph_num` | string | 每个音符包含的音素数量 |
| `note_seq` | string | 音符序列（音名，如 C4, rest） |
| `note_dur` | string | 音符时长序列（秒） |
| `note_slur` | string | 连音标记（0/1） |
| `f0_seq` | string | 基频序列（Hz） |
| `f0_timestep` | string | f0 采样间隔（秒） |

### 5.3 编辑注意事项

- `.ds` 文件是临时格式，OpenUTAU 是当前推荐的生产环境使用方式
- f0_seq 的 timestep 通常为 0.005s（5ms）
- `AP` = All Phoneme（开头填充），`SP` = Silence Phoneme（词间停顿），`rest` = 休止符
- 训练时需确保 `ph_seq` 与 `ph_dur` 长度一致

---

## 6. 其他格式概览

### 6.1 ENUNU / NNSVS

| 格式 | 说明 |
|------|------|
| `.lab` | HTK 单音素标签文件 |
| `.wav` | 音频文件（单声道） |
| `transcriptions.csv` | 转录文件（DiffSinger 兼容） |
| `.ust` | UTAU 工程文件 |
| `enuconfig.yaml` | ENUNU 配置文件 |

**HTK mono label 格式**：
```
0 5000000 pau
5000000 8000000 a
8000000 12000000 k
```
- 每行包含 `开始时间 结束时间 音素`
- 时间单位通常为 100 纳秒

### 6.2 DeepVocal / SharpKey

| 引擎 | 文件扩展名 | 说明 |
|------|-----------|------|
| SharpKey | `.sk` | 自定义二进制格式 |
| DeepVocal | `.dv` | 自定义二进制格式 |

- 闭源二进制格式，逆向工程难度较高
- 声库格式与 UTAU 根本不同：声音样本打包在单个大型文件中

### 6.3 MUTA

| 版本 | 文件扩展名 | 说明 |
|------|-----------|------|
| MUTA 2 | `.mtp` | 自定义二进制格式 |

- 已停止开发
- 没有公开的格式规范或解析库

### 6.4 NIAONiao（袅袅虚拟歌手）

| 文件扩展名 | 说明 |
|-----------|------|
| `.nn` | NIAONiao 原生工程格式 |

- 自定义文本格式
- 已停止开发（2024年7月）
- 可导入 `.mid/.midi`、`.ust`、`.vsqx`

### 6.5 AISingers

| 平台 | 文件扩展名 | 说明 |
|------|-----------|------|
| AISingers Studio (桌面端) | `.aisp` | 两段 JSON 拼接 |
| 在线编辑器 | `.ais` | JSON 头 + 自定义文本 |

### 6.6 VOICEVOX ソング

- 无独立工程文件格式，在应用内保存
- 完全免费、39+ 角色、商业可用
- 歌声质量不及专业付费软件、仅日语

---

## 7. 格式转换兼容性

### 7.1 跨格式转换矩阵（基于 UtaFormatix / LibreSVIP）

| 源格式 → 目标格式 | VSQX | UST | USTX | MIDI | CCS | SVP | MusicXML | PPSF |
|------------------|------|-----|------|------|-----|-----|----------|------|
| VSQX             | ✓    | ✓   | ✓    | ✓    | ✓   | ✓   | ✓        | ✓    |
| UST              | ✓    | ✓   | ✓    | ✓    | ✓   | ✓   | ✓        | ✓    |
| USTX             | ✓    | ✓   | ✓    | ✓    | ✓   | ✓   | ✓        | ✓    |
| MIDI             | ✓    | ✓   | ✓    | ✓    | ✓   | ✓   | ✓        | ✓    |
| CCS              | ✓    | ✓   | ✓    | ✓    | ✓   | ✓   | ✓        | ✓    |
| SVP              | ✓    | ✓   | ✓    | ✓    | ✓   | ✓   | ✓        | ✓    |
| MusicXML         | ✓    | ✓   | ✓    | ✓    | ✓   | ✓   | ✓        | ✓    |
| PPSF             | ✓    | ✓   | ✓    | ✓    | ✓   | ✓   | ✓        | ✓    |

### 7.2 格式公开程度排序

| 开放程度 | 格式 |
|---------|------|
| 完全公开 | `.ds` (JSON), `.acep` (JSON+zstd), `.aisp` (JSON), `.ais` (JSON+文本), `.ufdata` (JSON) |
| 基于标准 | `.ccs` (XML), MusicXML (XML), MIDI (SMF) |
| 部分已知 | `.ppsf` (旧二进制/新JSON+zip), `.nn` (自定义文本) |
| 闭源/未公开 | `.tssprj`, `.dv/.sk`, `.mtp`, `.srvl` |

### 7.3 推荐转换路径

1. **任何格式 → DiffSinger**：UtaFormatix → MusicXML/UST → 转换为 `.ds`
2. **CeVIO ↔ VoiSona**：通过 `.ccs` 格式互通
3. **UTAU → NEUTRINO**：UtaFormatix 转 MusicXML → NEUTRINO
4. **ACE Studio ↔ 其他**：LibreSVIP 支持 `.acep` 转换

---

## 8. 参考链接

### CeVIO / VoiSona
- LibSasara (.NET 库): https://github.com/InuInu2022/LibSasara
- VoiSona 导入/导出手册: https://manual.voisona.com/en/song/pc/2b6e9bc7efb180f79e77f218506dafc3
- CeVIO Wiki: https://cevio.fandom.com/wiki/CeVIO_Creative_Studio
- VoiSona Wiki: https://cevio.fandom.com/wiki/VoiSona

### ACE Studio
- acep_decrypt: https://github.com/SoulMelody/acep_decrypt
- ACE-Step DAW Native file I/O: https://github.com/ace-step/ACE-Step-DAW/issues/1526

### Piapro Studio
- Piapro Studio Wiki: https://piapro.fandom.com/wiki/Piapro_Studio_(software)
- Piapro Studio NT2 Wiki: https://piapro.fandom.com/wiki/Piapro_Studio_NT2

### NEUTRINO
- 官方网站: https://studio-neutrino.com/
- MusicXML について: https://studio-neutrino.com/332/
- Vocal Synth Wiki: https://vocalsynth.fandom.com/wiki/NEUTRINO
- MIDI-MusicXML 在线转换器: https://github.com/romot-co/midi-musicxml-seq

### DiffSinger
- OpenVPI DiffSinger: https://github.com/openvpi/DiffSinger
- 官方 .ds 示例: https://github.com/openvpi/DiffSinger/tree/main/samples
- 最佳实践文档: https://github.com/openvpi/DiffSinger/blob/main/docs/BestPractices.md

### ENUNU / NNSVS
- NNSVS 标注辅助脚本: https://github.com/UtaUtaUtau/nnsvslabeling
- ENUNU 时间校正器: https://github.com/UtaUtaUtau/enunu_timing_corrector
- OpenUTAU NNSVS 使用方法: https://opensynth.miraheze.org/wiki/音素器

### 通用转换工具
- UtaFormatix (在线转换): https://sdercolin.github.io/utaformatix3/
- LibreSVIP: https://github.com/SoulMelody/LibreSVIP
- OpenSVIP: https://github.com/yqzhishen/opensvip
- 格式文档: https://github.com/SoulMelody/LibreSVIP/blob/main/docs/project_formats.md

---

*本文档收集的歌声合成软件工程文件格式信息截至搜索日期。部分格式（尤其是闭源二进制格式）可能存在逆向工程风险或法律限制，请在合法合规的前提下使用相关信息。*
