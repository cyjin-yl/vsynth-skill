# UTAU / OpenUtau 格式详解

> 涵盖 UTAU (.ust) 与 OpenUtau (.ustx) 工程文件格式

---

## 目录

1. [格式概述](#1-格式概述)
2. [UTAU .ust 文件格式详解](#2-utau-ust-文件格式详解)
3. [OpenUtau .ustx 文件格式详解](#3-openutau-ustx-文件格式详解)
4. [版本差异对比](#4-版本差异对比)
5. [编辑规范与注意事项](#5-编辑规范与注意事项)
6. [代码示例](#6-代码示例)
7. [参考链接](#7-参考链接)

---

## 1. 格式概述

### 1.1 UTAU .ust 格式

**UST** (UTAU Sequence Text) 是歌声合成软件 UTAU 的原生工程文件格式。它是一种 INI-like 的文本格式，文件扩展名为 `.ust`。

- **本质**: 纯文本文件，采用类似 Windows INI 的分节键值对结构
- **用途**: 存储音符序列、歌词、音高、音量、包络线、音高弯折等参数
- **兼容性**: 被经典 UTAU、UTAU-Synth (Mac)、OpenUtau 等软件支持
- **编码**: 通常为 **Shift-JIS**（经典 UTAU），UTAU-Synth 支持 UTF-8 版本

### 1.2 OpenUtau .ustx 格式

**USTX** (UTAU Sequence Text Extended) 是 OpenUtau 的原生工程文件格式。它是一种基于 **YAML 1.2** 的文本格式，文件扩展名为 `.ustx`。

- **本质**: YAML 1.2 文本格式，UTF-8 编码
- **用途**: 存储多轨歌声合成工程，包含音符、音高曲线、表情参数、音素覆盖等
- **兼容性**: 仅被 OpenUtau 支持，但可以导入 `.ust` 和 `.vsqx` 文件
- **编码**: **UTF-8 with BOM**
- **历史**: OpenUtau 最初使用过 `.usty` 格式（早期版本），后统一为 `.ustx`

### 1.3 核心差异对比

| 特性 | UST (.ust) | USTX (.ustx) |
|------|-----------|-------------|
| 格式类型 | INI-like 文本 | YAML 1.2 |
| 编码 | Shift-JIS / UTF-8 | UTF-8 with BOM |
| 轨数支持 | 单轨 | 多轨 |
| 时间单位 | Tick (480=四分音符) | Tick (480=四分音符) |
| 音高表示 | Mode1 / Mode2 | 控制点曲线 |
| 表情参数 | Flags 字符串 | 结构化表达式 |
| 音频轨道 | 不支持 | 支持 (wave_parts) |
| 音素编辑 | 不支持 | 支持 |

---

## 2. UTAU .ust 文件格式详解

### 2.1 文件结构概览

```ini
[#VERSION]       -- 版本声明
UST Version1.2

[#SETTING]       -- 全局设置
Tempo=120.00
Tracks=1
ProjectName=Test
VoiceDir=%VOICE% voicebank_name
OutFile=output.wav
CacheDir=.
Tool1=wavtool.exe
Tool2=resampler.exe
Mode2=True

[#PREV]          -- 前一个音符（用于插件）
Length=480
Lyric=R
...

[#0000]          -- 音符 0
[#0001]          -- 音符 1
...

[#NEXT]          -- 后一个音符（用于插件）
...

[#TRACKEND]      -- 音轨结束标记
```

### 2.2 标准 Section 说明

#### [#VERSION] -- 版本声明

| 版本格式 | 示例 |
|---------|------|
| UST 1.2 | `[#VERSION]` `UST Version1.2` |
| UST 1.19 | `[#SETTING]` `UstVersion=1.19` |
| UST 1.20 | `[#VERSION]` `UST Version 1.20` |
| UST 2.0 | `[#VERSION]` `UST Version2.0` + `Charset=UTF-8` |

> **注意**: UTAU v0.4.18 同时支持 1.19 和 1.2 格式。当设置 "Output the entry of the old format to plugin-script and UST-file" 选项时，输出 1.19 格式。

#### [#SETTING] -- 全局设置

| 字段 | 类型 | 说明 |
|-----|------|------|
| `Tempo` | float | BPM，默认 120.00 |
| `Tracks` | int | 音轨数量（通常为1） |
| `ProjectName` | string | 工程名称 |
| `VoiceDir` | string | 音源路径，可用 `%VOICE%` 前缀 |
| `OutFile` | string | 输出 WAV 文件名 |
| `CacheDir` | string | 缓存目录 |
| `Tool1` | string | 拼接工具（如 wavtool.exe） |
| `Tool2` | string | 重采样器（如 resampler.exe） |
| `Mode2` | bool | 是否使用 Mode2 音高（True/False） |
| `Flags` | string | 全局 Flags |
| `TimeSignatures` | string | 拍号，格式 `(4/4/0)` |

#### [#0000] ~ [#NNNN] -- 音符 Section

音符按顺序编号，从 `#0000` 开始。每个音符包含以下字段：

**基本参数**

| 字段 | 类型 | 默认值 | 说明 |
|-----|------|--------|------|
| `Length` | int | 480 | 音符长度，480 = 四分音符 |
| `Lyric` | string | - | 歌词/音素标识 |
| `NoteNum` | int | 60 | MIDI 音高编号，C4 = 60 |
| `Intensity` | int/float | 100 | 音量（百分比） |
| `Modulation` | int/float | 0 | 调制/颤音深度 |
| `Velocity` | float | 100 | 辅音速度（百分比） |
| `StartPoint` | float | 0 | 起始点偏移（毫秒） |
| `Tempo` | float | - | 局部 BPM（覆盖全局） |
| `Flags` | string | - | 音符级别 Flags |
| `Label` | string | - | 标签 |
| `$direct` | bool | False | 是否直接渲染 |

**前奏/重叠参数**

| 字段 | 类型 | 说明 |
|-----|------|------|
| `PreUtterance` | float | 先行发声（毫秒） |
| `VoiceOverlap` | float | 重叠（毫秒） |
| `@preuttr` | float | 计算后的先行发声 |
| `@overlap` | float | 计算后的重叠 |
| `@stpoint` | float | 计算后的起始点 |

> **注意**: 在 1.19 版本中，`Modulation` 被错误拼写为 `Moduration`。`Pitches` 被错误拼写为 `Piches`。

#### [#PREV] / [#NEXT] -- 插件辅助 Section

用于 UTAU 插件处理时的前后音符参考，结构与常规音符相同。

#### [#TRACKEND] -- 音轨结束

标记音轨的结束，通常为空 Section。

### 2.3 Mode2 音高弯折参数

Mode2 是 UTAU 的高级音高编辑模式，使用控制点方式定义音高曲线。

| 字段 | 格式 | 说明 |
|-----|------|------|
| `PBS` | `position,height` | 音高弯折起点（毫秒, 音分） |
| `PBW` | 逗号分隔列表 | 控制点之间的时间宽度（毫秒） |
| `PBY` | 逗号分隔列表 | 各控制点的音高偏移（音分，decacents） |
| `PBM` | 逗号分隔列表 | 曲线类型列表 |

**PBM 曲线类型**:
- 空字符串或省略: S-curve（默认）
- `s`: 直线 (Linear)
- `j`: J-curve
- `r`: R-curve
- `i`: 入曲线 (In)
- `o`: 出曲线 (Out)
- `io`: 入出曲线 (In-Out)

**示例**:
```ini
PBS=-45
PBW=89
PBY=0,10,-5
PBM=s,j,r
```

### 2.4 Mode1 音高弯折参数（旧版）

| 字段 | 说明 |
|-----|------|
| `PitchBend` | 逗号分隔的音高值列表（音分） |
| `PBStart` | 音高弯折开始时间（毫秒） |

### 2.5 包络线 (Envelope)

包络线控制音符的音量变化，格式为逗号分隔的数值列表。

**标准格式**（5点 + 可选 % 标记 + 2点）:
```
Envelope=p1,p2,p3,v1,v2,v3,v4,%,p4,p5,v5
```

**字段说明**:

| 位置 | 字段 | 类型 | 说明 |
|-----|------|------|------|
| 1 | p1 | float | 起始点（毫秒） |
| 2 | p2 | float | 衰减开始点（毫秒） |
| 3 | p3 | float | 衰减结束点（毫秒） |
| 4 | v1 | float | 起始音量（%） |
| 5 | v2 | float | 峰值音量（%） |
| 6 | v3 | float | sustain 音量（%） |
| 7 | v4 | float | 衰减前音量（%） |
| 8 | % | string | 可选，百分比标记 |
| 9 | p4 | float | 释音开始点（毫秒） |
| 10 | p5 | float | 释音结束点（毫秒） |
| 11 | v5 | float | 释音结束音量（%） |

**默认包络**: `0,5,35,0,100,100,0,%,0` 或 `0,21,35,0,100,100,0,%,0`

### 2.6 颤音 (Vibrato) 参数

| 字段 | 格式 | 说明 |
|-----|------|------|
| `VBR` | 逗号分隔列表 | 颤音参数 |

**VBR 参数顺序**:
1. `length` - 颤音覆盖音符的百分比长度
2. `cycle` - 周期（毫秒）
3. `depth` - 深度（音分）
4. `fade_in` - 淡入（百分比）
5. `fade_out` - 淡出（百分比）
6. `phase` - 相位偏移（百分比）
7. `height` - 整体音高偏移（音分）
8. `strength` - 强度（百分比）
9. `period_changes` - 周期变化（百分比）

**示例**: `VBR=65,160,35,20,20,0,0,0,0`

---

## 3. OpenUtau .ustx 文件格式详解

### 3.1 基本说明

USTX 是 YAML 1.2 格式的文本文件，使用 UTF-8 编码（带 BOM）。文件中的时间单位与 MIDI 一致：1 四分音符 = 480 ticks。音高使用 MIDI 编号，C4 = 60。

> **开发者提示**: Python 开发者处理 USTX 时应使用 `ruamel.yaml`（支持 YAML 1.2），不要使用 `pyyaml`。

### 3.2 顶层结构

```yaml
name: "Project Name"
ustx_version: "0.6"
resolution: 480
key: 0
time_signatures:
  - ...
tempos:
  - ...
tracks:
  - ...
voice_parts:
  - ...
wave_parts:
  - ...
expressions:
  dyn:
    name: "dynamics (curve)"
    abbr: "dyn"
    type: "Curve"
    min: -240
    max: 120
    default_value: 0
```

### 3.3 UProject 字段

| 字段 | 类型 | 说明 |
|-----|------|------|
| `name` | string | 工程名称 |
| `ustx_version` | string | USTX 格式版本，当前为 0.6 |
| `resolution` | int | 每四分音符的 ticks，固定为 480 |
| `key` | int | 调号，0 = C大调/A小调 |
| `time_signatures` | list | 拍号变化列表 |
| `tempos` | list | 曲速变化列表 |
| `tracks` | list | 轨道列表 |
| `voice_parts` | list | 歌声片段列表 |
| `wave_parts` | list | 音频片段列表 |

> **弃用字段**: `bpm`, `beat_per_bar`, `beat_unit` 在项目根级别已弃用，请使用 `tempos` 和 `time_signatures`。

### 3.4 拍号 (Time Signatures)

```yaml
time_signatures:
  - bar_position: 0
    beat_per_bar: 4    # 分子
    beat_unit: 4       # 分母
```

### 3.5 曲速 (Tempos)

```yaml
tempos:
  - position: 0        # tick 位置
    bpm: 120.0         # BPM 值
```

### 3.6 轨道 (Tracks)

```yaml
tracks:
  - singer: "voicebank_folder"
    phonemizer: "JA CVVC"
    track_name: "Main"
    track_color: "Blue"
    mute: false
    solo: false
    volume: 0.0        # dB
    pan: 0.0
    voice_color_names: []
```

| 字段 | 类型 | 说明 |
|-----|------|------|
| `singer` | string | 音源文件夹名 |
| `phonemizer` | string | 音素器插件 |
| `track_name` | string | 轨道标签 |
| `track_color` | string | 显示颜色 |
| `mute` | bool | 静音 |
| `solo` | bool | 独奏 |
| `volume` | float | 音量 (dB) |
| `pan` | float | 声相 |
| `voice_color_names` | list | 可用音色名称列表 |

### 3.7 歌声片段 (Voice Parts)

```yaml
voice_parts:
  - name: "Part 1"
    comment: ""
    track_no: 0        # 所属轨道索引
    position: 0          # 起始 tick 位置
    duration: 1920     # 总长度（ticks）
    notes:
      - ...
    curves:
      - ...
```

### 3.8 音符 (Notes)

```yaml
notes:
  - position: 0        # 片段内起始 tick
    duration: 480      # 音符长度（ticks）
    tone: 60           # MIDI 音高编号
    lyric: "do"        # 歌词
    pitch:
      data:
        - {x: -40.0, y: 0, shape: "io"}
        - {x: 40.0, y: 0, shape: "io"}
      snap_first: true
    vibrato:
      length: 0
      period: 175
      depth: 25
      in: 10
      out: 10
      shift: 0
      drift: 0
      vol_link: 0
    phoneme_expressions:
      - {index: 0, abbr: "clr", value: 1}
    phoneme_overrides:
      - {index: 1, phoneme: "a"}
      - {index: 0, offset: 65}
```

| 字段 | 类型 | 说明 |
|-----|------|------|
| `position` | int | 片段内起始 tick |
| `duration` | int | 音符长度（ticks），480=四分音符 |
| `tone` | int | MIDI 音高编号 |
| `lyric` | string | 歌词文本 |
| `pitch` | object | 音高控制点 |
| `vibrato` | object | 颤音参数 |
| `phoneme_expressions` | list | 音素级别表情参数 |
| `phoneme_overrides` | list | 音素覆盖/偏移 |

**Pitch 控制点**:
- `x`: 相对于音符起始的时间（毫秒）
- `y`: 音高偏移（音分）
- `shape`: 曲线形状 (`io`, `s`, `j`, `r`, `i`, `o` 等)
- `snap_first`: 是否将第一个控制点对齐到音符起始

**Vibrato 参数**:
- `length`: 颤音长度（百分比）
- `period`: 周期（毫秒）
- `depth`: 深度（音分）
- `in`: 淡入（百分比）
- `out`: 淡出（百分比）
- `shift`: 相位偏移
- `drift`: 音高漂移
- `vol_link`: 音量关联

### 3.9 曲线 (Curves)

自动化曲线（如音高偏移、动态）：

```yaml
curves:
  - xs: [0, 120, 240, 360, 480]    # tick 位置
    ys: [0, 10, 5, -5, 0]          # 数值
    abbr: "pitd"                    # 表达式缩写 (pitch deviation)
```

### 3.10 音频片段 (Wave Parts)

```yaml
wave_parts:
  - name: "Backing Track"
    track_no: 1
    position: 0
    relative_path: "audio/backing.wav"
    file_duration_ms: 180000.0
```

### 3.11 表情 (Expressions)

OpenUtau 定义了多种表情/参数类型：

| 缩写 | 名称 | 类型 | 范围 | 默认值 | Flag |
|------|------|------|------|--------|------|
| `dyn` | dynamics (curve) | Curve | -240 ~ 120 | 0 | - |
| `pitd` | pitch deviation (curve) | Curve | -1200 ~ 1200 | 0 | - |
| `clr` | voice color | Options | 0 ~ -1 | 0 | - |
| `eng` | resampler engine | Options | 0 ~ 1 | 0 | - |
| `vel` | velocity | Numerical | 0 ~ 200 | 100 | - |
| `vol` | volume | Numerical | 0 ~ 200 | 100 | - |
| `atk` | attack | Numerical | 0 ~ 200 | 100 | - |
| `dec` | decay | Numerical | 0 ~ 100 | 0 | - |
| `gen` | gender | Numerical | -100 ~ 100 | 0 | `g` |
| `genc` | gender (curve) | Curve | -100 ~ 100 | 0 | - |
| `bre` | breath | Numerical | 0 ~ 100 | 0 | `B` |
| `brec` | breathiness (curve) | Curve | -100 ~ 100 | 0 | - |
| `lpf` | lowpass | Numerical | 0 ~ 100 | 0 | `H` |
| `mod` | modulation | Numerical | 0 ~ 100 | 0 | - |
| `alt` | alternate | Numerical | 0 ~ 16 | 0 | - |

**表达式类型枚举**:
- `Numerical` = 0: 数值型
- `Options` = 1: 选项型
- `Curve` = 2: 曲线型

---

## 4. 版本差异对比

### 4.1 UST 版本差异

| 特性 | UST 1.19 | UST 1.2 / 1.20 | UST 2.0 |
|------|----------|---------------|---------|
| 版本声明位置 | `[#SETTING]` 内 `UstVersion=1.19` | `[#VERSION]` Section | `[#VERSION]` + `Charset=UTF-8` |
| Modulation | `Moduration`（拼写错误） | `Modulation` | `Modulation` |
| Pitches | `Piches`（拼写错误） | `Pitches` | `Pitches` |
| 编码 | Shift-JIS | Shift-JIS | UTF-8 |
| 兼容性 | 经典 UTAU | 经典 UTAU | UTAU-Synth, OpenUtau |

### 4.2 UST 与 USTX 核心差异

| 方面 | UST | USTX |
|------|-----|------|
| 文件格式 | INI-like 文本 | YAML 1.2 |
| 编码 | Shift-JIS (主要) | UTF-8 with BOM |
| 轨道数 | 单轨 | 多轨 |
| 时间精度 | Tick (整数) | Tick (整数) |
| 音高表示 | PBS/PBW/PBY/PBM | 控制点列表 (x, y, shape) |
| 包络线 | 逗号分隔数值 | 不直接存储（由算法生成） |
| 表情参数 | Flags 字符串 | 结构化表达式定义 |
| 音素覆盖 | 不支持 | 支持 |
| 音频轨道 | 不支持 | 支持 wave_parts |
| 曲速变化 | 仅支持全局 | 支持多个曲速变化点 |
| 拍号变化 | 仅支持全局 | 支持多个拍号变化点 |

---

## 5. 编辑规范与注意事项

### 5.1 UST 文件编辑规范

**编码**:
- 经典 UTAU 使用 **Shift-JIS** 编码
- UTAU-Synth 和跨平台使用建议 **UTF-8**
- 错误的编码会导致 **Mojibake**（文字化け/乱码）

**换行符**:
- Windows 使用 `CRLF` (`\r\n`)
- Unix/Linux/macOS 使用 `LF` (`\n`)
- UTAU 通常接受两种格式，但插件可能敏感

**特殊字符**:
- 歌词中避免使用未转义的特殊字符
- 某些 Flags 可能包含特殊字符（如 `g+5`, `B-10`）

**Section 格式**:
- Section 名使用方括号: `[#SECTION]`
- 键值对使用等号: `Key=Value`
- 值为空时保留等号: `Key=`
- 不支持引号包裹字符串

**数字格式**:
- 整数不加小数点: `Length=480`
- 浮点数使用小数点: `Tempo=120.00`
- 列表使用逗号分隔: `Envelope=0,5,35,0,100,100,0,%,0`

### 5.2 USTX 文件编辑规范

**编码**:
- 必须使用 **UTF-8 with BOM**
- 纯 UTF-8（无 BOM）可能导致 OpenUtau 无法正确识别

**YAML 规范**:
- 遵循 YAML 1.2 标准
- 缩进使用空格（不要使用 Tab！）
- 列表项使用 `-` 前缀
- 映射键值对使用 `:` 后跟空格

**特殊字符限制**:
- 制表符 (Tab) 会导致 YAML 解析错误
- 歌词中包含 Tab 会导致 "Block sequence entries are not allowed in this context" 错误

**字符串处理**:
- 普通字符串不需要引号: `lyric: hello`
- 包含特殊字符时使用引号: `lyric: "hello world"`

### 5.3 常见错误与规避

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| Mojibake / 乱码 | 编码不匹配 | 转换为 Shift-JIS (UST) 或 UTF-8 |
| 插件无法读取 UST | 版本格式不匹配 | 确保使用插件支持的版本格式 |
| OpenUtau 崩溃 | USTX 包含 Tab | 移除所有制表符 |
| YAML 解析错误 | 缩进错误/特殊字符 | 检查空格缩进，移除 Tab |
| 音高不生效 | Mode2=False | 设置 `Mode2=True` |
| 包络线异常 | 值超出范围 | 重置为默认包络 |
| 音源找不到 | 路径错误 | 检查 `VoiceDir` 路径格式 |
| oto.ini 不生效 | 缓存未清除 | 删除音源目录 `.d4c` / `.vs4` 缓存文件 |
| 辅音被切断 | Offset > PreUtterance | 调整 oto 参数，确保 Offset < PreUtterance |

### 5.4 音源与 oto.ini

UTAU 音源制作涉及录音表设计和 oto.ini 参数配置。相关详细内容：
- **录音表 / 拼接类型**: 参见 [utau_voicebank.md](utau_voicebank.md)（CV / VCV / CVVC / CVVX / VCCV / ARPAsing 等各语言录音表）
- **oto.ini 制作**: 参见 [oto_ini.md](oto_ini.md)（参数详解、各拼接类型的 oto 设定、批量生成）

---

## 6. 代码示例

### 6.1 UST 文件示例

```ini
[#VERSION]
UST Version2.0
Charset=UTF-8
[#SETTING]
Tempo=120.00
Tracks=1
ProjectName=Example Song
VoiceDir=%VOICE% Teto
OutFile=output.wav
CacheDir=.
Tool1=wavtool4vcv.exe
Tool2=moresampler.exe
Mode2=True
Flags=g+5
[#0000]
Length=480
Lyric=ー
NoteNum=60
Intensity=100
Modulation=0
Envelope=0,5,35,0,100,100,0,%,0
[#0001]
Length=480
Lyric=ka
NoteNum=62
Intensity=100
Modulation=0
PBS=-40
PBW=80
PBY=0,0
PBM=s,s
Envelope=0,5,35,0,100,100,0,%,0
VBR=65,160,35,20,20,0,0,0,0
[#0002]
Length=480
Lyric=a
NoteNum=64
Intensity=80
Modulation=10
PBS=-50
PBW=100
PBY=0,15,-5
PBM=s,j,r
Envelope=0,10,40,0,100,90,80,%,0
[#0003]
Length=960
Lyric=R
NoteNum=60
Intensity=100
Modulation=0
[#TRACKEND]
```

### 6.2 USTX 文件示例

```yaml
name: Example Song
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
  - singer: "Kasane Teto"
    phonemizer: "JA VCV"
    track_name: "Main Vocal"
    track_color: "Red"
    mute: false
    solo: false
    volume: 0.0
    pan: 0.0
    voice_color_names: []
voice_parts:
  - name: "Intro"
    comment: ""
    track_no: 0
    position: 0
    duration: 1920
    notes:
      - position: 0
        duration: 480
        tone: 60
        lyric: "do"
        pitch:
          data:
            - {x: -40.0, y: 0, shape: "io"}
            - {x: 40.0, y: 0, shape: "io"}
          snap_first: true
        vibrato:
          length: 0
          period: 175
          depth: 25
          in: 10
          out: 10
          shift: 0
          drift: 0
          vol_link: 0
    curves:
      - xs: [0, 240, 480, 720, 960, 1200, 1440, 1680, 1920]
        ys: [0, 0, 5, -5, 0, 0, 3, -3, 0]
        abbr: "pitd"
      - xs: [0, 480, 960, 1440, 1920]
        ys: [100, 100, 80, 90, 100]
        abbr: "dyn"
wave_parts:
  - name: "Backing Track"
    track_no: 1
    position: 0
    relative_path: "audio/backing.wav"
    file_duration_ms: 180000.0
```

### 6.3 Python 读取 USTX 示例

```python
from ruamel.yaml import YAML

# 读取 USTX 文件
yaml = YAML()
with open('song.ustx', 'r', encoding='utf-8-sig') as f:
    data = yaml.load(f)

# 访问项目信息
print(f"Project: {data['name']}")
print(f"Version: {data['ustx_version']}")

# 遍历音符
for part in data.get('voice_parts', []):
    for note in part.get('notes', []):
        print(f"Lyric: {note['lyric']}, Tone: {note['tone']}, Duration: {note['duration']}")

# 修改曲速
data['tempos'][0]['bpm'] = 140.0

# 保存
with open('song_modified.ustx', 'w', encoding='utf-8') as f:
    yaml.dump(data, f)
```

### 6.4 Python 使用 utaupy 处理 UST

```python
import utaupy

# 加载 UST 文件
ust = utaupy.ust.load('song.ust')

# 访问全局设置
print(f"Tempo: {ust.tempo}")

# 遍历音符
for note in ust.notes:
    print(f"Lyric: {note.lyric}, NoteNum: {note.notenum}, Length: {note.length}")

# 修改音符属性
for note in ust.notes:
    note.intensity = 100
    note.modulation = 0

# 保存
ust.write('song_modified.ust')
```

---

## 7. 参考链接

### UTAU 官方/社区文档
1. UTAU Wiki 2.0 - ust 定义: http://utau.wikidot.com/ust
2. UTAU Wiki 2.0 - UTAU-Synth 教程: http://utau.wikidot.com/tutorials:utau-synth-tutorial
3. UTAU Wiki 2.0 - 乱码修复指南: http://utau.wikidot.com/tutorials:gibberish-mojibake
4. UTAU Wiki 2.0 - ARPAsing UST 教程: http://utau.wikidot.com/tutorials:arpasing-ust-tutorial

### OpenUtau 官方文档
5. OpenUtau GitHub Wiki - USTX 文件格式: https://github.com/stakira/OpenUtau/wiki/USTX-file-format
6. OpenUtau GitHub - 项目源码 (USTx 实现): https://github.com/stakira/OpenUtau/tree/master/OpenUtau.Core/Ustx
7. OpenUtau GitHub Wiki - 批量编辑 API: https://github.com/stakira/OpenUtau/blob/master/OpenUtau.Core/Editing/README.md
8. OpenUtau 日本语 Wiki - ustx 文件: https://w.atwiki.jp/openutau/pages/16.html

### 第三方库与工具
9. utaupy (Python UTAU 工具库): https://github.com/oatsu-gh/utaupy
10. utaupy DeepWiki - UST 文件详解: https://deepwiki.com/oatsu-gh/utaupy/2.1-ust-files
11. UtaFormatix (Kotlin 跨格式转换): https://jsr.io/@sevenc-nanashi/utaformatix-ts
12. USTConvert (编码转换): https://github.com/UMUISM/USTConvert

### 教程与指南
13. UTAU 编码指南 (FelineWasteland): https://utau.felinewasteland.com/ref/encoding
14. OpenUtau 编码/乱码技术分析: https://blog.gitcode.com/19c677d60e2a93a21ef8e969659fe731.html
15. 中文 UTAU 技术贴 (Bilibili): https://www.bilibili.com/read/cv10987379/
16. UTAU 入门教程 (utau.us): https://utau.us/ust.html

### 文件格式参考
17. UST File Extension 说明 (Solvusoft): https://www.solvusoft.com/en/file-extensions/file-extension-ust/
18. USTX FileInfo 说明: https://fileinfo.com/extension/ustx
19. 中文 OtomadWiki - UTAU/UST: https://otomad.wiki/UTAU/UST
20. OpenUtau Wiki (Fandom): https://utau.fandom.com/wiki/OpenUtau

### 相关项目
21. PyUtauCli (Python UTAU CLI): https://github.com/delta-kimigatame/PyUtauCli
22. Libresvip (Python USTX 读写): https://github.com/SoulMelody/LibreSVIP
23. UTAU TextEncode Convert Helper: https://utau.info/resources/tools/
24. ENUNU (AI 歌声合成): https://github.com/oatsu-gh/ENUNU
25. DiffSinger Support (OpenUtau): https://github.com/stakira/OpenUtau/wiki/DiffSinger-support

---

*本文档基于公开可获取的技术文档、源代码和社区资料整理而成。文件格式可能随软件版本更新而变化。*
