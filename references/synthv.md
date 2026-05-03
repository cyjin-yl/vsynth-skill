# Synthesizer V 格式详解

> 涵盖 .svp (Synthesizer V Studio) 与 .s5p (Synthesizer V Editor) 工程文件格式

---

## 目录

1. [文件格式概述](#1-文件格式概述)
2. [版本历史与版本差异](#2-版本历史与版本差异)
3. [.svp 文件结构详解](#3-svp-文件结构详解)
4. [.s5p 文件格式说明](#4-s5p-文件格式说明)
5. [关键对象详解](#5-关键对象详解)
6. [参数系统详解](#6-参数系统详解)
7. [编辑规范与注意事项](#7-编辑规范与注意事项)
8. [代码示例](#8-代码示例)
9. [参考链接](#9-参考链接)

---

## 1. 文件格式概述

### 1.1 基本特性

Synthesizer V 的工程文件采用 **JSON 文本格式** 存储所有项目数据。文件为纯文本，可直接使用文本编辑器查看和修改。

| 格式 | 文件扩展名 | 适用软件 | 基本类型 | 状态 |
|------|-----------|---------|---------|------|
| Synthesizer V Studio 工程 | `.svp` | Synthesizer V Studio / Studio 2 | 标准序列化格式 (JSON) | 活跃开发 |
| Synthesizer V Editor 工程 | `.s5p` | Synthesizer V Editor (旧版) | 标准序列化格式 (JSON) | 停止开发 |

### 1.2 核心特点

- **纯 JSON 结构**：.svp 和 .s5p 文件都是 JSON 格式的文本文件
- **时间单位**：使用 `blick` 作为内部时间单位（1 blick = 1/705600000 拍，约 1.418 纳秒/拍）
- **音高表示**：使用 MIDI 音符编号（C4 = 60）
- **参数曲线**：由控制点（节点）和插值方法组成
- **分组管理**：音符和参数归属于音符组（NoteGroup），可在轨道上复用

### 1.3 文件类型关系

```
.svp (Synthesizer V Studio) ── 当前活跃格式
├── 版本 1: Synthesizer V Studio 1.x (2018-2024)
└── 版本 2: Synthesizer V Studio 2 Pro (2025-至今)

.s5p (Synthesizer V Editor) ── 旧版格式
└── Synthesizer V Editor Build 018 (2019) 最终版本
    可由新版软件导入并转换为 .svp
```

---

## 2. 版本历史与版本差异

### 2.1 软件版本演进

| 软件 | 版本 | 时期 | 文件格式 | 主要特点 |
|------|------|------|---------|---------|
| Synthesizer V Editor | Build 017-018 | 2019 | .s5p | 初代编辑器，JSON 格式 |
| Synthesizer V Studio | 1.0.0 - 1.11.x | 2020-2024 | .svp | 全新架构，引入 AI 歌声 |
| Synthesizer V Studio 2 | 2.0.0 - 2.2.x | 2025-至今 | .svp | 全新引擎，更快渲染 |

### 2.2 .svp 版本 1 与版本 2 的关键差异

| 特性 | 版本 1 (SVS1) | 版本 2 (SVS2) |
|------|--------------|--------------|
| **轨道结构** | 音符和参数直接放在轨道上 | 必须先创建音符组，再放音符 |
| **手动模式** | 有专门的 Manual Mode 开关 | 移除，改为 Smart Pitch Controls |
| **AI Retakes** | Expressiveness / Enhancement | 改为 Expression Pad (X/Y 坐标) |
| **新参数** | 无 | Mouth Opening（嘴型开合） |
| **语音模式** | 影响音色 | 影响音高、音色、发音 |
| **音素面板** | 滑块调整比例 | 直接可视化拖拽调整 |
| **兼容性** | 可保存为 1.9.0/1.10.0 兼容 | 可导入 V1 工程并转换 |
| **渲染速度** | 基准 | 快达 300% |
| **语言支持** | 日/英/中/粤/西 | 增加韩语支持 |

### 2.3 版本兼容性

- **SVS2 打开 SVS1 的 .svp**：自动显示项目转换对话框，可正确转换音高曲线等数据
- **SVS1 打开 SVS2 的 .svp**：需要使用 "Save As (Version 1.10.0-Compatible)" 保存
- **SVS2 打开 .s5p**：自动转换，保存后变为 .svp 格式
- **向下兼容限制**：V2 专属数据（如 Mouth Opening）在 V1 中会被丢弃

---

## 3. .svp 文件结构详解

### 3.1 顶层结构

```json
{
  "version": 2,
  "timeAxis": {
    "tempo": [...],
    "measure": [...]
  },
  "tracks": [...],
  "library": [...],
  "renderConfig": {...},
  "settings": {...}
}
```

### 3.2 timeAxis（时间轴）

存储全局曲速和拍号信息。

#### tempo 数组元素

| 字段 | 类型 | 说明 |
|------|------|------|
| `position` | integer | 位置（blick 单位） |
| `beatPerMinute` | number | BPM 值（范围：10-1000） |

#### measure（拍号）数组元素

| 字段 | 类型 | 说明 |
|------|------|------|
| `position` | integer | 位置（blick 单位） |
| `numerator` | integer | 拍号分子 |
| `denominator` | integer | 拍号分母 |

> **注意**：拍号只能在小节开头设置，不能在小节中间改变。

### 3.3 tracks（轨道）

轨道分为**歌声轨**和**伴奏轨**两种类型。

#### 轨道对象结构

```json
{
  "displayOrder": 0,
  "name": "Track 1",
  "color": "#FF6B6B",
  "dbDefaults": {
    "name": "Saki AI",
    "language": "japanese",
    "phoneset": "x-sampa"
  },
  "groups": [...],
  "mixer": {
    "gain": 0,
    "pan": 0,
    "mute": false,
    "solo": false
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `displayOrder` | integer | 显示顺序（与存储索引可能不同） |
| `name` | string | 轨道名称 |
| `color` | string | 颜色（HEX 格式，如 `#FF6B6B`） |
| `dbDefaults` | object | 默认声库设置 |
| `groups` | array | 音符组引用列表 |
| `mixer` | object | 混音器设置（版本 2.1.1+） |

#### dbDefaults（默认声库）

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 声库名称 |
| `language` | string | 语言（japanese/english/mandarin/cantonese/korean/spanish） |
| `phoneset` | string | 音素集（如 `x-sampa`） |

#### 伴奏轨（Instrumental Track）

伴奏轨的 `dbDefaults` 中存储音频文件路径信息，通过 `NoteGroupReference` 的 `audio` 字段引用音频文件。

### 3.4 library（库）

项目库中存储所有可复用的 `NoteGroup` 对象。每个 `NoteGroup` 有唯一的 UUID。

```json
{
  "name": "Chorus",
  "uuid": "ab85d637-d80b-4628-9c27-007ea74029af",
  "notes": [...],
  "parameters": {...},
  "pitchControls": [...]
}
```

### 3.5 groups（音符组引用）

`NoteGroupReference` 将库中的 `NoteGroup` 放置到轨道上。

```json
{
  "groupID": "ab85d637-d80b-4628-9c27-007ea74029af",
  "timeOffset": 211680000,
  "pitchOffset": 0,
  "voice": {
    "paramLoudness": 0,
    "paramTension": 0,
    "paramBreathiness": 0,
    "paramGender": 0,
    "paramToneShift": 0,
    "vocalModeParams": {
      "Soft": {"pitch": 50, "timbre": 30, "pronunciation": 0}
    }
  },
  "isInstrumental": false,
  "muted": false
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `groupID` | string | 引用的 NoteGroup UUID |
| `timeOffset` | integer | 时间偏移（blick） |
| `pitchOffset` | integer | 音高偏移（半音） |
| `voice` | object | 该实例的声库和参数设置 |
| `isInstrumental` | boolean | 是否为伴奏轨引用 |
| `muted` | boolean | 是否静音（版本 2.1.1+） |

---

## 4. .s5p 文件格式说明

### 4.1 格式概述

.s5p 是旧版 **Synthesizer V Editor**（俗称 "SV1代" / "R1"）使用的工程文件格式。该软件最后更新为 Build 018（2019年9月），现已停止开发。

### 4.2 与 .svp 的核心差异

| 特性 | .s5p (Editor) | .svp (Studio) |
|------|---------------|---------------|
| 软件 | Synthesizer V Editor | Synthesizer V Studio |
| 状态 | 停止开发 | 活跃开发 |
| 底层引擎 | 传统采样合成 | AI 神经网络 |
| 轨道结构 | 简单轨道 | NoteGroup 系统 |
| 参数系统 | 基础参数 | 丰富参数 + Vocal Modes |
| 文件结构 | JSON | JSON（扩展后） |
| 兼容方向 | 可被 SVS 导入 | 不能被 Editor 打开 |

### 4.3 导入行为

当 Synthesizer V Studio（版本 1 或 2）打开 .s5p 文件时：
1. 自动读取并解析 JSON 结构
2. 转换为内部 .svp 格式表示
3. 保存时写入为 .svp 文件
4. 原 .s5p 文件保持不变

### 4.4 .s5p 文件结构

.s5p 同样使用 JSON 格式，顶层结构较 .svp 更简单：

```json
{
  "version": 1,
  "song": {
    "tempo": [...],
    "timeSignature": [...],
    "tracks": [...]
  }
}
```

> **注意**：.s5p 没有 NoteGroup/库的概念，音符直接存储在轨道上。

---

## 5. 关键对象详解

### 5.1 Note（音符）

#### 基本字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `onset` | integer | 起始位置（blick） |
| `duration` | integer | 时长（blick） |
| `lyrics` | string | 歌词文本 |
| `phonemes` | string | 自定义音素（空格分隔，如 `"hh ah ll ow"`） |
| `pitch` | integer | 音高（MIDI 编号，C4=60） |
| `detune` | number | 微调（音分，100音分=1半音） |
| `attributes` | object | 扩展属性 |

#### 版本 1 专属属性（attributes）

| 字段 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `tF0Offset` | number | 音高过渡 - 偏移（秒） | NaN |
| `tF0Left` | number | 音高过渡 - 左持续时间（秒） | NaN |
| `tF0Right` | number | 音高过渡 - 右持续时间（秒） | NaN |
| `dF0Left` | number | 音高过渡 - 左深度（半音） | NaN |
| `dF0Right` | number | 音高过渡 - 右深度（半音） | NaN |
| `tF0VbrStart` | number | 颤音 - 开始时间（秒） | NaN |
| `tF0VbrLeft` | number | 颤音 - 左淡入（秒） | NaN |
| `tF0VbrRight` | number | 颤音 - 右淡出（秒） | NaN |
| `dF0Vbr` | number | 颤音 - 深度（半音） | NaN |
| `pF0Vbr` | number | 颤音 - 相位（弧度，-π 到 π） | NaN |
| `fF0Vbr` | number | 颤音 - 频率（Hz） | NaN |
| `tNoteOffset` | number | 音素时序 - 音符偏移（秒） | NaN |
| `exprGroup` | string | 表情组（仅标准声库） | 可选 |
| `dur` | number[] | 音素时长缩放（0.2-1.8） | 可选 |
| `alt` | number[] | 音素替代发音 | 可选 |

#### 版本 2 通用属性（attributes）

| 字段 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `rTone` | number | 说唱 - 音调 | NaN |
| `rIntonation` | number | 说唱 - 语调 | NaN |
| `dF0VbrMod` | number | 颤音调制深度 | NaN |
| `expValueX` | number | 表情垫 X 参数（版本 2.1.1+） | NaN |
| `expValueY` | number | 表情垫 Y 参数（版本 2.1.1+） | NaN |
| `muted` | boolean | 音符是否静音（版本 2.1.1+） | false |
| `evenSyllableDuration` | boolean | 多音节平均分割（版本 2.1.1+） | false |
| `languageOverride` | string | 音符级语言覆盖（版本 2.1.1+） | "" |
| `phonesetOverride` | string | 音符级音素集覆盖（版本 2.1.1+） | "" |
| `phonemes` | object[] | 音素级属性（版本 2.1.1+） | 可选 |
| `musicalType` | string | 音符类型（"sing" 或 "rap"） | "sing" |

#### phonemes 音素级属性（版本 2.1.1+）

每个音素对象包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| `leftOffset` | number | 音素左边界偏移 |
| `position` | number | 音素位置 |
| `activity` | number | 音素活跃度（对塞音/破擦音） |
| `strength` | number | 发音强度（0.2-1.8） |

### 5.2 NoteGroup（音符组）

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 组名称 |
| `uuid` | string | 唯一标识符 |
| `notes` | Note[] | 音符列表（按时序排序） |
| `parameters` | object | 参数曲线集合 |
| `pitchControls` | array | 音高控制点/曲线（版本 2.1.0+） |

### 5.3 NoteGroupReference（音符组引用）

| 字段 | 类型 | 说明 |
|------|------|------|
| `groupID` | string | 目标 NoteGroup 的 UUID |
| `timeOffset` | integer | 时间偏移（blick） |
| `pitchOffset` | integer | 音高偏移（半音） |
| `voice` | object | 声音属性 |
| `isInstrumental` | boolean | 是否为伴奏 |
| `muted` | boolean | 是否静音 |

#### voice 对象属性

| 字段 | 类型 | 说明 |
|------|------|------|
| `paramLoudness` | number | 响度（dB） |
| `paramTension` | number | 张力 |
| `paramBreathiness` | number | 气声 |
| `paramGender` | number | 性别/共振峰 |
| `paramToneShift` | number | 音区偏移（音分） |
| `vocalModeParams` | object | 语音模式参数（版本 2.1.1+） |

### 5.4 Track（轨道）

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 轨道名称 |
| `displayOrder` | number | 显示顺序 |
| `color` | string | 颜色（HEX） |
| `dbDefaults` | object | 默认声库 |
| `groups` | NoteGroupReference[] | 组引用列表 |
| `mixer` | TrackMixer | 混音器设置 |
| `isBounced` | boolean | 是否导出到文件 |

---

## 6. 参数系统详解

### 6.1 参数类型总览

Synthesizer V Studio 提供丰富的参数控制。参数曲线由**控制点**（节点）组成，两点之间通过插值计算。

| 参数名称 | typeName | 显示名称 | 范围 | 单位 | 默认值 |
|---------|----------|---------|------|------|--------|
| 音高偏差 | `pitchDelta` | Pitch Deviation | [-1200, 1200] | 音分 | 0 |
| 颤音包络 | `vibratoEnv` | Vibrato Envelope | [0, 2] | 倍率 | 1 |
| 响度 | `loudness` | Loudness | [-48, 12] | dB | 0 |
| 张力 | `tension` | Tension | [-1.0, 1.0] | - | 0 |
| 气声 | `breathiness` | Breathiness | [-1.0, 1.0] | - | 0 |
| 浊度 | `voicing` | Voicing | [0.0, 1.0] | - | 1 |
| 性别/共振峰 | `gender` | Gender | [-1.0, 1.0] | - | 0 |
| 音区偏移 | `toneShift` | Tone Shift | [-800, 800] | 音分 | 0 |
| 嘴型开合 | `mouthOpening` | Mouth Opening | - | - | - |
| 音素速度 | `phonemeSpeed` | Phoneme Speed | - | - | - |
| 帽子重音 | `hatAccent` | Hat Accent | - | - | - |
| 语音模式 | `vocalMode_*` | Vocal Mode | [0, 150] | - | 0 |

### 6.2 参数插值方法

控制点之间的插值支持三种方法：

| 方法 | 说明 |
|------|------|
| Linear | 线性插值 |
| Cosine | 余弦插值 |
| Cubic | 改良 Catmull-Rom 样条插值 |

### 6.3 参数曲线数据结构

```json
{
  "pitchDelta": {
    "mode": "cubic",
    "points": [
      [0, 0],
      [70560000, 100],
      [141120000, -50]
    ]
  }
}
```

每个 `points` 数组元素为 `[position, value]`：
- `position`：blick 位置
- `value`：参数值

### 6.4 Vocal Mode（语音模式）

语音模式是 AI 声库的特色功能，每种声库有不同的预设模式（如 "Light"、"Powerful"、"Soft" 等）。

版本 2 中，语音模式参数的结构：

```json
{
  "vocalModeParams": {
    "Soft": {
      "pitch": 50,
      "timbre": 30,
      "pronunciation": 0
    },
    "Powerful": {
      "pitch": 0,
      "timbre": 80,
      "pronunciation": 20
    }
  }
}
```

每个语音模式有三个维度（范围 0-150）：
- `pitch`：音高影响
- `timbre`：音色影响
- `pronunciation`：发音影响

---

## 7. 编辑规范与注意事项

### 7.1 JSON 规范要求

1. **编码格式**：UTF-8（推荐）或 UTF-16
2. **缩进**：原版使用紧凑格式，但标准 JSON 解析器支持任意缩进
3. **数字精度**：浮点数保留足够精度，避免舍入误差
4. **字段顺序**：JSON 对象字段顺序理论上不影响解析，但建议保持合理结构

### 7.2 时间单位（blick）

- 1 **blick** = 1/705600000 拍
- 转换关系：`秒数 = blicks / (705600000 * BPM / 60)`

### 7.3 音高表示

- 使用 **MIDI 音符编号**：C4 = 60
- 微调使用 `detune` 字段（音分，100 音分 = 1 半音）

### 7.4 NaN 值处理

- 在 Note 的属性中，`NaN` 表示该属性使用默认值（基于所属 NoteGroupReference 的设置）
- 编写解析器时需正确处理 JavaScript 风格的 `NaN` 值

### 7.5 UUID 生成

- NoteGroup 使用 UUID 进行唯一标识
- 格式示例：`"ab85d637-d80b-4628-9c27-007ea74029af"`
- 引用时必须确保 UUID 在 library 中存在

### 7.6 轨道限制

- **Basic 版**：最多 3 条轨道（包括伴奏轨）
- **Pro 版**：无轨道数量限制

### 7.7 伴奏轨注意事项

- 支持的音频格式：WAV、FLAC、OGG
- MP3 格式可导入但可能导致同步问题（建议转换为 WAV）
- 伴奏轨不参与最终渲染，需在 DAW 中混音

### 7.8 参数曲线编辑原则

- 参数曲线与音符**解耦**：移动音符不会自动移动参数
- 参数在 NoteGroup 级别定义，而非轨道级别
- 主组（main group）的参数会影响所有子组

### 7.9 常见错误避免

1. 不要创建重叠的音符（除非故意需要特殊效果）
2. 拍号只能设在小节开头
3. 保持 UUID 的唯一性和有效性
4. 音符的 `phonemes` 字段为空时，使用默认发音
5. 注意版本 2 中所有音符必须属于某个 NoteGroup

---

## 8. 代码示例

### 8.1 最小项目结构示例

```json
{
  "version": 2,
  "timeAxis": {
    "tempo": [
      {"position": 0, "beatPerMinute": 120}
    ],
    "measure": [
      {"position": 0, "numerator": 4, "denominator": 4}
    ]
  },
  "tracks": [
    {
      "displayOrder": 0,
      "name": "Lead Vocal",
      "color": "#4A90D9",
      "dbDefaults": {
        "name": "Saki AI",
        "language": "japanese",
        "phoneset": "x-sampa"
      },
      "groups": [
        {
          "groupID": "main-group-uuid",
          "timeOffset": 0,
          "pitchOffset": 0,
          "voice": {
            "paramLoudness": 0,
            "paramTension": 0,
            "paramBreathiness": 0,
            "paramGender": 0,
            "paramToneShift": 0
          },
          "isInstrumental": false
        }
      ]
    }
  ],
  "library": [
    {
      "name": "Main",
      "uuid": "main-group-uuid",
      "notes": [
        {
          "onset": 0,
          "duration": 70560000,
          "lyrics": "la",
          "phonemes": "l a",
          "pitch": 60,
          "detune": 0,
          "attributes": {
            "dF0VbrMod": 1.0
          }
        }
      ],
      "parameters": {
        "pitchDelta": {
          "mode": "cubic",
          "points": [[0, 0], [35280000, 50], [70560000, 0]]
        },
        "vibratoEnv": {
          "mode": "linear",
          "points": [[0, 1], [70560000, 1]]
        }
      }
    }
  ]
}
```

### 8.2 参数曲线示例

```json
{
  "parameters": {
    "pitchDelta": {
      "mode": "cubic",
      "points": [
        [0, 0],
        [17640000, 25],
        [35280000, -25],
        [52920000, 10],
        [70560000, 0]
      ]
    },
    "loudness": {
      "mode": "linear",
      "points": [
        [0, 0],
        [35280000, 3],
        [70560000, -2]
      ]
    },
    "tension": {
      "mode": "cosine",
      "points": [
        [0, 0],
        [70560000, 0.5]
      ]
    }
  }
}
```

### 8.3 Python 读取与编辑 SVP 示例

```python
import json
import uuid

# 读取 SVP 文件
with open("project.svp", "r", encoding="utf-8") as f:
    project = json.load(f)

# 获取版本
version = project.get("version", 1)
print(f"Project version: {version}")

# 遍历所有音符
for track in project.get("tracks", []):
    track_name = track.get("name", "Unnamed")
    print(f"\nTrack: {track_name}")
    
    for group_ref in track.get("groups", []):
        group_id = group_ref.get("groupID")
        time_offset = group_ref.get("timeOffset", 0)
        
        # 在库中查找对应的 NoteGroup
        for group in project.get("library", []):
            if group.get("uuid") == group_id:
                for note in group.get("notes", []):
                    onset = note.get("onset", 0) + time_offset
                    pitch = note.get("pitch", 60)
                    lyrics = note.get("lyrics", "")
                    print(f"  Note: {lyrics} @ pitch {pitch}, onset {onset}")
                break

# 修改歌词示例
for group in project.get("library", []):
    for note in group.get("notes", []):
        if note.get("lyrics") == "old_lyric":
            note["lyrics"] = "new_lyric"

# 添加新的 NoteGroup
new_group_id = str(uuid.uuid4())
new_group = {
    "name": "New Section",
    "uuid": new_group_id,
    "notes": [],
    "parameters": {}
}
project["library"].append(new_group)

# 在轨道上引用新组
for track in project.get("tracks", []):
    track["groups"].append({
        "groupID": new_group_id,
        "timeOffset": 0,
        "pitchOffset": 0,
        "voice": {
            "paramLoudness": 0,
            "paramTension": 0
        },
        "isInstrumental": False
    })

# 保存
with open("modified.svp", "w", encoding="utf-8") as f:
    json.dump(project, f, ensure_ascii=False, indent=2)
```

### 8.4 blick 时间转换工具函数

```python
BLICKS_PER_BEAT = 705600000
TICKS_PER_BEAT = 480

def blick_to_tick(blicks):
    """将 blick 转换为 tick（假设 480 tick/四分音符）"""
    return blicks * TICKS_PER_BEAT / BLICKS_PER_BEAT

def tick_to_blick(ticks):
    """将 tick 转换为 blick"""
    return int(ticks * BLICKS_PER_BEAT / TICKS_PER_BEAT)

def blick_to_seconds(blicks, bpm):
    """将 blick 转换为秒数"""
    beats = blicks / BLICKS_PER_BEAT
    return beats * 60 / bpm

def seconds_to_blick(seconds, bpm):
    """将秒数转换为 blick"""
    beats = seconds * bpm / 60
    return int(beats * BLICKS_PER_BEAT)
```

---

## 9. 参考链接

### 官方文档
- Synthesizer V Studio 2 Pro 用户手册：https://svdocs.dreamtonics.com/en/synthv/basic-usage/project
- Synthesizer V Studio 1 用户手册：https://sv1.docs.dreamtonics.com/en/synthv/basic-usage/project
- 版本 1 到版本 2 迁移指南：https://svdocs.dreamtonics.com/en/synthv/upgrade/migration-guide
- Note Groups 说明：https://svdocs.dreamtonics.com/en/synthv/advanced-usage/library
- 参数面板说明：https://svdocs.dreamtonics.com/en/synthv/advanced-usage/parameters

### 官方脚本手册
- Synthesizer V Studio Scripting Manual：https://resource.dreamtonics.com/scripting/
- Note 类参考：https://resource.dreamtonics.com/scripting/Note.html
- NoteGroup 类参考：https://resource.dreamtonics.com/scripting/NoteGroup.html
- NoteGroupReference 类参考：https://resource.dreamtonics.com/scripting/NoteGroupReference.html
- Track 类参考：https://resource.dreamtonics.com/scripting/Track.html
- Project 类参考：https://resource.dreamtonics.com/scripting/Project.html
- Automation 类参考：https://resource.dreamtonics.com/scripting/Automation.html
- SV 全局对象参考：https://resource.dreamtonics.com/scripting/SV.html

### 第三方工具
- LibreSVIP：https://github.com/SoulMelody/LibreSVIP
- OpenSVIP：https://github.com/yqzhishen/opensvip
- UtaFormatix：https://sdercolin.github.io/utaformatix3/
- wav2svp：https://github.com/SUC-DriverOld/wav2svp

### 社区 Wiki
- Synthesizer V Studio Wiki：https://synthv.fandom.com/wiki/Synthesizer_V_Studio
- Synthesizer V Studio 2 Wiki：https://synthv.fandom.com/wiki/Synthesizer_V_Studio_2
- Synthesizer V (Editor) Wiki：https://synthv.fandom.com/wiki/Synthesizer_V
- SynthV 非官方用户手册：https://manual.synthv.info/
- Dreamtonics 官方论坛：https://forum.dreamtonics.com/

### 技术参考
- Synthesizer V 官方网站：https://dreamtonics.com/synthesizerv/
- Studio 2 Pro 功能介绍：https://dreamtonics.com/synthesizer-v-studio-2-pro-walkthrough-video/
- 2.1.1 更新说明：https://dreamtonics.com/synthesizer-v-studio-2-1-1-final-update/

---

*本文档基于公开的技术文档、官方手册、脚本 API 参考和第三方开源项目分析整理而成。*
