# VOCALOID 格式详解

> 涵盖 VOCALOID 1/2/3/4/5/6 工程文件格式：.vsq (SMF+INI), .vsqx (XML), .vpr (ZIP+JSON)

---

## 目录

1. [格式概述与版本历史](#1-格式概述与版本历史)
2. [.vsq 文件格式详解](#2-vsq-文件格式详解vocaloid-2)
3. [.vsqx 文件格式详解](#3-vsqx-文件格式详解vocaloid-34)
4. [.vpr 文件格式详解](#4-vpr-文件格式详解vocaloid-56)
5. [版本差异与兼容性](#5-版本差异与兼容性)
6. [编码与编辑规范](#6-编码与编辑规范)
7. [代码示例](#7-代码示例)
8. [参考链接](#8-参考链接)

---

## 1. 格式概述与版本历史

| VOCALOID 版本 | 文件扩展名 | 基础格式 | 编码 | 备注 |
|--------------|-----------|---------|------|------|
| VOCALOID 1 | `.mid` | SMF | - | 标准 MIDI 文件 |
| VOCALOID 2 | `.vsq` | SMF Format 1 + INI | Shift-JIS | 基于 MIDI 的自定义格式 |
| VOCALOID 3 | `.vsqx` | XML (vsq3 命名空间) | UTF-8 | 纯 XML 格式 |
| VOCALOID 4 | `.vsqx` | XML (vsq4 命名空间) | UTF-8 | 在 V3 基础上扩展 |
| VOCALOID 5 | `.vpr` | ZIP + JSON | UTF-8 | 全新格式 |
| VOCALOID 6 | `.vpr` | ZIP + JSON | UTF-8 | 增加 AI 轨道等新特性 |

---

## 2. .vsq 文件格式详解（VOCALOID 2）

### 2.1 格式概述

.vsq 文件基于 **Standard MIDI File (SMF) Format 1** 规范：
- **数值存储**：Big-Endian（大端序）
- **声乐数据**：以 **INI 格式** 存储在 MIDI Text Meta Event (0xFF 0x01) 中
- **文本编码**：日语歌词使用 **Shift-JIS**
- **轨道结构**：Master Track（tempo/拍子）+ Editor Track（钢琴卷帘信息）

### 2.2 INI 数据的分割存储机制

VSQ 中的 INI 文档被分割成多个 MIDI Text Meta Event 存储：

| 属性 | 说明 |
|-----|------|
| 分割单位 | 每段 Text Meta Event 的字符串字节数固定为 **127 byte (0x7F)** |
| 末尾段 | 最后一段长度 ≤ 127 byte |
| 行尾符 | 原始换行符被替换为 `0x0A` |
| 前缀格式 | `DM:` + N.ToString("0000") + `:` |

**拼接示例**：
```
DM:0000:[INI_DATA_PART_1]
DM:0001:[INI_DATA_PART_2]
...
DM:00NN:[INI_DATA_PART_LAST]
```

### 2.3 INI Section 结构

| Section 名 | 说明 |
|-----------|------|
| `[Common]` | 应用和合成引擎信息 |
| `[Master]` | 主轨道设定 |
| `[Mixer]` | 混音器设定 |
| `[EventList]` | 事件时间轴列表 |
| `[ID#XXXX]` | 特定命令（XXXX 为四位零基索引） |
| `[h#XXXX]` | 被其他 section 引用的句柄数据 |

**EventList Section 示例**：
```ini
[EventList]
0=ID#0000
768=ID#0001
1536=ID#0002
...
```

**Anote 类型属性**：

| 属性名 | 说明 |
|-------|------|
| `Length` | 音符长度（tick 单位） |
| `Note#` | MIDI 音符编号（C4=60） |
| `Dynamics` | 力度 |
| `PMBendDepth` | 滑音深度 |
| `PMBendLength` | 滑音长度 |
| `LyricHandle` | 引用 `h#XXXX` 中的歌词信息 |
| `VibratoHandle` | 引用 `h#XXXX` 中的颤音信息 |
| `VibratoDelay` | 颤音延迟 |

### 2.4 NRPN 控制变更

Meta Text Event 之后，VSQ 文件记录使用 **NRPN** 的 MIDI Control Change 事件，用于存储连续的参数自动化数据（DYN, BRE, BRI 等）。

---

## 3. .vsqx 文件格式详解（VOCALOID 3/4）

### 3.1 核心特征

- 纯 XML 格式，Well-formed XML
- **UTF-8 编码（无 BOM）**
- VOCALOID 3 使用 `vsq3` 命名空间
- VOCALOID 4 使用 `vsq4` 命名空间
- 安装目录下包含 `vsq3.xsd` / `vsq4.xsd` Schema 定义文件

### 3.2 XML 根元素与命名空间

#### VOCALOID 3（vsq3）

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<vsq3 xmlns="http://www.yamaha.co.jp/vocaloid/schema/vsq3/"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.yamaha.co.jp/vocaloid/schema/vsq3/ vsq3.xsd">
  <vender>Yamaha corporation</vender>
  <version>3.0.0.11</version>
  ...
</vsq3>
```

#### VOCALOID 4（vsq4）

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<vsq4 xmlns="http://www.yamaha.co.jp/vocaloid/schema/vsq4/"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.yamaha.co.jp/vocaloid/schema/vsq4/ vsq4.xsd">
  <vender>Yamaha corporation</vender>
  <version>4.0.0.0</version>
  ...
</vsq4>
```

> **重要区别**：
> - V3 编辑器**无法**打开 `vsq4` 根元素的文件（报错：`no declaration found for element 'vsq4'`）
> - V4 编辑器可以打开 `vsq3` 和 `vsq4` 两种文件
> - V4 的 VSQX 是 V3 的"减缩版"，代码更精简

### 3.3 XML 节点结构（层级关系）

```
vsq3 / vsq4 (根)
├── vender              [CDATA]  固定'Yamaha corporation'
├── version             [CDATA]  文件格式版本
├── vVoiceTable         [vVoice+]
│   └── vVoice          [vBS, vPC, compID, vVoiceName, vVoiceParam]
├── mixer               [masterUnit, vsUnit+, seUnit, karaokeUnit]
├── masterTrack         [seqName, comment, resolution, preMeasure, timeSig+, tempo+]
│   ├── resolution      [整数值]  时间分解能（默认480 tick/四分音符）
│   ├── preMeasure      [整数值]  前置小节数（通常为1，对应7680 tick）
│   ├── timeSig         [posMes, nume, denomi]
│   └── tempo           [t, v]    t=tick位置, v=BPM*100
├── vsTrack+            [vsTrackNo, trackName, comment, musicalPart*]
│   └── musicalPart     [pos, tick, musPtName, note*, singer, cc*]
│       ├── note        [t, dur, n, v, y, p, nStyle]
│       │   └── nStyle  [seq id="vibDep"/"vibRate"/"vibLen"/...]
│       └── cc          [id, posTick, value]  控制参数
├── seTrack             [wavPart*]
├── karaokeTrack        [...]
└── aux                 [auxID, content]
```

### 3.4 关键节点详细说明

#### `<masterTrack>` - 主轨道

```xml
<masterTrack>
  <seqName>Untitled_0</seqName>
  <comment></comment>
  <resolution>480</resolution>       <!-- 四分音符分解能: 480 tick -->
  <preMeasure>1</preMeasure>          <!-- 前置小节数 -->
  <timeSig>
    <posMes>0</posMes>                 <!-- 第0小节 -->
    <nume>4</nume>                      <!-- 4/4拍 -->
    <denomi>4</denomi>
  </timeSig>
  <tempo>
    <t>7680</t>                         <!-- 第7680 tick (前置1小节×4×480) -->
    <v>12000</v>                        <!-- 120.00 BPM -->
  </tempo>
</masterTrack>
```

**时间计算**：
- 1 小节 = 4 拍 × 480 tick = 1920 tick（4/4 拍时）
- `preMeasure` 通常为 1，对应 7680 tick = 4 小节（前置空白区域）
- 实际音符的 tick 位置需要减去前置小节的 tick 数

#### `<note>` 音符元素

| 子元素 | 数据类型 | 说明 |
|--------|---------|------|
| `<t>` | 整数 | 音符起始 tick（相对 musicalPart 的 pos） |
| `<dur>` | 整数 | 音符持续时间（tick） |
| `<n>` | 整数 (0-127) | MIDI 音符编号 |
| `<v>` | 整数 (0-127) | Velocity / 力度 |
| `<y>` | CDATA | 歌词文本（lyric） |
| `<p>` | CDATA | 音素文本（phoneme，X-SAMPA 格式，空格分隔） |
| `<nStyle>` | 复合元素 | 包含多个 `<seq>` 参数序列 |

**X-SAMPA 音素编辑**: 详见 [xsampa.md](xsampa.md)。VOCALOID 使用标准 X-SAMPA 标记音素（如日语 `k a`、英语 `k { t`），通过 `<p>` 节点覆盖默认发音。编辑时注意：
- 音素间必须空格分隔
- 大小写敏感（`S` 为龈后擦音 ɕ，`s` 为齿龈擦音 s）
- 特殊符号需转义：`p\` 表示双唇摩擦音 [ɸ]，`4` 表示闪音 [ɾ]

**nStyle / seq 的 id 属性值**：

| id 值 | 参数名 | 说明 |
|--------|-------|------|
| `vibDep` | Vibrato Depth | 颤音深度 |
| `vibRate` | Vibrato Rate | 颤音速率 |
| `vibLen` | Vibrato Length | 颤音长度比例（0-100%） |
| `risePort` | Rise Portamento | 上升滑音 |
| `fallPort` | Fall Portamento | 下降滑音 |
| `accent` | Accent | 重音 |
| `decGain` | Decay Gain | 衰减增益 |
| `opn` | Opening | 开口度 |

**seq 中的 p 值含义**：
- `p` 表示在音符内的相对位置，范围 0~65536
- 0 = 音符起始位置，65536 = 音符结束位置

#### `<cc>` 控制参数（Control Change）

```xml
<cc>
  <id>DYN</id>
  <posTick>0</posTick>
  <value>64</value>
</cc>
```

**常见参数 ID**：

| ID | 全称 | 说明 |
|----|------|------|
| `DYN` | Dynamics | 音量/动态 |
| `BRE` | Breath | 气息 |
| `BRI` | Brightness | 明亮度 |
| `CLE` | Clearness | 清晰度 |
| `GEN` | Gender Factor | 性别因子 |
| `PIT` | Pitch Bend | 音高弯音 |
| `PBS` | Pitch Bend Sensitivity | 音高弯音灵敏度 |
| `XSY` | Cross Synthesis | 交叉合成（V4+） |

### 3.5 VSQX 版本间标签映射（V3 vs V4）

| 含义 | VSQ3 标签 | VSQ4 标签 |
|------|----------|----------|
| 小节位置 | `posMes` | `m` |
| 分子 | `nume` | `nu` |
| 分母 | `denomi` | `de` |
| tick 位置 | `posTick` | `t` |
| BPM 值 | `bpm` | `v` |
| 轨道名 | `trackName` | `name` |
| 音乐片段 | `musicalPart` | `vsPart` |
| 持续时间 | `durTick` | `dur` |
| 音符编号 | `noteNum` | `n` |
| 歌词 | `lyric` | `y` |
| 音素 | `phnms` | `p` |
| 控制器 | `mCtrl` | `cc` |
| PBS | `PBS` | `S` |
| PIT | `PIT` | `P` |

---

## 4. .vpr 文件格式详解（VOCALOID 5/6）

### 4.1 格式概述

.vpr 文件本质是一个 **ZIP 压缩包**：
- 将扩展名从 `.vpr` 改为 `.zip` 即可解压查看
- 内部主要文件为 `Project/sequence.json`
- JSON 数据采用 **驼峰命名法 (CamelCase)**
- 编码为 **UTF-8**

### 4.2 ZIP 容器内部结构

```
song.vpr (ZIP 压缩包)
├── Project/
│   └── sequence.json     <-- 主要工程数据文件
└── [其他可能的资源文件]
```

### 4.3 sequence.json 顶层结构

```json
{
  "version": "5.0.0",
  "vendor": "Yamaha corporation",
  "title": "Untitled",
  "masterTrack": {
    "tempo": [...],
    "timeSignature": [...],
    "samplingRate": 44100,
    "loop": false
  },
  "tracks": [
    {
      "type": "vocaloid",           // 或 "vocaloidAI", "audio", "mono", "stereo"
      "name": "Track 1",
      "parts": [
        {
          "type": "musical",
          "start": 0,
          "duration": 1920,
          "notes": [
            {
              "pos": 0,
              "duration": 480,
              "pitch": 60,
              "lyric": "do",
              "phoneme": "d o",
              "velocity": 64,
              "dynamics": 64,
              "pitchBend": [...],
              "vibrato": {...}
            }
          ],
          "parameters": {...}
        }
      ]
    }
  ],
  "mixer": {
    "master": {...},
    "tracks": [...]
  }
}
```

### 4.4 关键 JSON 字段说明

**Track 对象**：

| 字段名 | 数据类型 | 说明 |
|--------|---------|------|
| `type` | 字符串 | 轨道类型：`vocaloid`, `vocaloidAI`, `audio`, `mono`, `stereo` |
| `name` | 字符串 | 轨道名称 |
| `parts` | 数组 | 轨道内的片段列表 |
| `volume` | 数值 | 轨道音量 |
| `pan` | 数值 | 轨道声像 |
| `mute` | 布尔 | 静音 |
| `solo` | 布尔 | 独奏 |

**VOCALOID 6 新增轨道类型**：
- `vocaloidAI`：VOCALOID:AI 轨道，使用 AI 合成引擎
- `vocaloid`：传统轨道（兼容 V3/V4/V5 声库）
- `audio`：音频轨道（立体声）
- `mono`：单声道轨道（呼吸音等）

### 4.5 VOCALOID 6 的 VPR 特有扩展

1. **VOCALOID:AI 轨道** (`type: "vocaloidAI"`)：
   - 使用 AI 歌声合成引擎
   - 支持 "TAKE" 功能（最多 10 个备选合成结果）
   - 支持 "Air" 参数控制气息强度
   - 支持 "Character" 参数（替代 Gender Factor）

2. **Pitch Pencil / Pitch Eraser 工具**（V6.5+）
3. **Cross-Synthesis (XSY)**（V6.5 重新引入）
4. **Project Tuning**：可在项目设置中调整 A4 参考音高

### 4.6 VPR Note 结构（V6 实际格式）

```json
{
  "pos": 32655,
  "duration": 480,
  "number": 69,
  "lyric": "kan",
  "phoneme": "k a n",
  "langID": 0,
  "velocity": 0.75,
  "accent": 0.25,
  "isAiVibratoEnabled": true,
  "aiExp": {
    "opening": 0.5,
    "accent": 0.25,
    "decay": 0.5
  },
  "singingSkill": {
    "id": "vibrato",
    "value": 0.5
  }
}
```

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `pos` | 整数 | tick 位置（相对于 part 起始） |
| `duration` | 整数 | 音符持续时间（tick） |
| `number` | 整数 (0-127) | MIDI 音符编号（音高） |
| `lyric` | 字符串 | 歌词文本 |
| `phoneme` | 字符串 | 音素文本（空格分隔的 X-SAMPA） |
| `langID` | 整数 | 语言 ID（0=日语, 1=英语, 2=中文等） |
| `velocity` | 浮点 (0-1) | 力度 |
| `accent` | 浮点 | 重音 |
| `isProtected` | 布尔 | 音素保护（编辑器内修改歌词时生效） |
| `isAiVibratoEnabled` | 布尔 | AI 颤音开关（V6 AI 轨道） |
| `aiExp` | 对象 | AI 表情参数（opening, accent, decay） |
| `singingSkill` | 对象 | 唱歌技巧参数 |

> **V6 跨语种注意**：V6 的 `phoneme` 字段在 AI 轨道（`type: 2`）和传统轨道（`type: 0`）中均有效。直接修改 JSON 的 `phoneme` 字段后，V6 加载时会直接使用该值，与 `isProtected` 无关。`isProtected` 的作用是在编辑器 UI 内：当用户手动修改歌词时，决定是否根据新歌词自动更新音素（`false` = 自动更新，`true` = 保留原音素）。因此跨语种时建议设为 `true`，防止用户在编辑器内调整歌词时意外覆盖手动设置的音素。V6 编辑器中的音素显示格式为方括号包裹（如 `[d' i]`、`[tS M]`），但 JSON 的 `phoneme` 字段本身不包含方括号，使用空格分隔的 X-SAMPA（如 `"d' i"`、`"tS M"`）。
>
> **腭化音素标记**：V6 使用 `'` 表示日语腭化辅音（如 `b'`、`d'`、`t'`、`m'` 等）。例如拼音 `ni` 对应 `"J i"`，拼音 `di` 对应 `"d' i"`，拼音 `yu` 对应 `"j M"`。跨语种时务必参考日语音素表设置正确的腭化标记。

---

## 5. 版本差异与兼容性

### 5.1 文件格式兼容性表

| 读取软件 | .vsq (V2) | .vsqx (V3) | .vsqx (V4) | .vpr (V5) | .vpr (V6) |
|---------|-----------|-----------|-----------|-----------|-----------|
| VOCALOID 2 | ✅ | ❌ | ❌ | ❌ | ❌ |
| VOCALOID 3 | ✅ | ✅ | ❌ | ❌ | ❌ |
| VOCALOID 4 | ✅ | ✅ | ✅ | ❌ | ❌ |
| VOCALOID 5 | ❌ | ✅ (导入) | ✅ (导入) | ✅ | ❌ |
| VOCALOID 6 | ❌ | ✅ (导入) | ✅ (导入) | ✅ | ✅ |
| Synthesizer V (Gen1) | ❌ | ✅ | ✅ | ❌ | ❌ |
| Synthesizer V (Gen2) | ❌ | ✅ | ✅ | ✅ | - |

### 5.2 VSQX 版本间兼容性详情

| 操作 | 结果 |
|------|------|
| V3 打开 V4 保存的 VSQX | ❌ 失败（`no declaration found for element 'vsq4'`） |
| V4 打开 V3 保存的 VSQX | ✅ 成功 |
| V4.1.0 打开 V4.2.0 保存的 VSQX | ❌ 失败 |
| V4.2.0 打开 V4.1.0 保存的 VSQX | ✅ 成功 |

### 5.3 导出能力对比

| 软件版本 | 可导出格式 |
|---------|-----------|
| VOCALOID 2 | .vsq, .wav |
| VOCALOID 3 | .vsqx (vsq3), .vsq, .wav |
| VOCALOID 4 | .vsqx (vsq4), .wav |
| VOCALOID 5 | .vpr, .mid (SMF), .wav |
| VOCALOID 6 | .vpr, .mid (SMF), .wav (16/24bit, 44.1/48/96/192kHz) |

---

## 6. 编码与编辑规范

### 6.1 各格式编码方式

| 格式 | 文件编码 | 歌词/文本编码 | 备注 |
|------|---------|--------------|------|
| VSQ (V2) | 二进制 (SMF) | Shift-JIS | 日语歌词必须使用 Shift-JIS |
| VSQX (V3/V4) | UTF-8 (无 BOM) | UTF-8 | XML 声明中显式指定 `encoding="UTF-8"` |
| VPR (V5/V6) | UTF-8 | UTF-8 | JSON 内部使用 Unicode |
| MIDI 导入/导出 | - | 可配置 | V6 支持选择 Shift-JIS 或 UTF-8 |

### 6.2 VSQX XML 编辑规范

1. **命名空间必须正确**：
   - V3 文件必须使用 `http://www.yamaha.co.jp/vocaloid/schema/vsq3/`
   - V4 文件必须使用 `http://www.yamaha.co.jp/vocaloid/schema/vsq4/`
   - 根元素名必须对应（`vsq3` 或 `vsq4`）

2. **版本号格式**：
   - `vender` 元素固定为 `Yamaha corporation`（注意是 vender 不是 vendor）
   - `version` 元素如 `3.0.0.11`（V3）或 `4.x.x.x`（V4）

3. **时间基准**：
   - 全局时间基准为 `<resolution>` 值（通常为 480 ticks/四分音符）
   - `<preMeasure>` 默认值为 1（对应 7680 ticks = 4 小节前导区域）
   - 实际音乐从 tick 7680 开始

### 6.3 VPR JSON 编辑规范

1. **ZIP 容器结构**：必须保持 `Project/sequence.json` 的内部路径
2. **驼峰命名法**：JSON 字段名使用 CamelCase（如 `vsTrackNo`, `musPtName`）
3. **轨道类型枚举**：`vocaloid` = 传统歌声，`vocaloidAI` = AI 歌声（V6）

---

## 7. 代码示例

### 7.1 VSQX Python 解析与编辑示例

```python
from lxml import etree

# 解析 VSQX
parser = etree.XMLParser(strip_cdata=False)
tree = etree.parse("input.vsqx", parser)
root = tree.getroot()

# 定义命名空间（V4）
ns = {"ns": "http://www.yamaha.co.jp/vocaloid/schema/vsq4/"}

# 获取 masterTrack 的 tempo
tempo_elements = root.find('ns:masterTrack', namespaces=ns).findall('ns:tempo', namespaces=ns)
for tempo in tempo_elements:
    t = int(tempo.find('ns:t', namespaces=ns).text)    # tick 位置
    v = int(tempo.find('ns:v', namespaces=ns).text) / 100  # BPM
    print(f"Tempo: {v} BPM at tick {t}")

# 修改歌词示例
notes = root.find('ns:vsTrack', namespaces=ns).find('ns:vsPart', namespaces=ns).findall('ns:note', namespaces=ns)
for note in notes:
    lyric_node = note.find('ns:y', namespaces=ns)
    if lyric_node is not None and lyric_node.text == "old_lyric":
        lyric_node.text = "new_lyric"

# 保存修改
tree.write("output.vsqx", encoding="UTF-8", xml_declaration=True)
```

### 7.2 VPR Python 解析与编辑示例

```python
import json
import zipfile
import io

# 读取 VPR 文件
with zipfile.ZipFile("input.vpr", "r") as z:
    with z.open("Project/sequence.json") as f:
        data = json.load(f)

# 修改项目标题
data["title"] = "New Title"

# 遍历轨道和音符
for track in data.get("tracks", []):
    for part in track.get("parts", []):
        if part.get("type") == "musical":
            for note in part.get("notes", []):
                if note.get("lyric") == "do":
                    note["lyric"] = "ra"

# 保存回 VPR
import os
# 创建新的 ZIP
with zipfile.ZipFile("output.vpr", "w", zipfile.ZIP_DEFLATED) as z:
    json_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    z.writestr("Project/sequence.json", json_bytes)
```

### 7.3 vpr-parser 使用示例

```python
from vpr_parser import VPRParser

parser = VPRParser()
project = parser.parse("song.vpr")

# 访问项目信息
print(project.title)
print(project.version)

# 遍历轨道
for track in project.tracks:
    print(track.name, track.type)
    for part in track.parts:
        for note in part.notes:
            print(f"  Note: pitch={note.pitch}, lyric={note.lyric}")

# 修改并保存
project.title = "New Title"
parser.dump(project, "modified.vpr")
```

---

## 8. 参考链接

### 官方文档
- VOCALOID 6 官方规格：https://www.vocaloid.com/vocaloid6/specs/
- VOCALOID 6 Reference Manual：https://rsc-net.vocaloid.com/assets/pdf_files/bb/VOCALOID_Reference_Manual_ENG.pdf
- VOCALOID 5 Reference Guide：https://rsc-net.vocaloid.com/assets/pdf_files/VOCALOID5_Reference_Manual_ENG.pdf
- VOCALOID 6 旧版文件兼容性：https://www.vocaloid.com/en/learn/ln6212
- VOCALOID 6.5 更新说明：https://www.vocaloid.com/en/learn/ln6214
- VOCALOID 6.6 更新说明：https://www.vocaloid.com/en/learn/ln6215
- MIDI 歌词编码设置：https://www.vocaloid.com/en/learn/ln6211

### 维基与社区
- VSQ file format | Vocaloid Wiki：https://vocaloid.fandom.com/wiki/VSQ_file_format
- VOCALOID4 | Vocal Synthesizer Wiki：https://vocalsynth.fandom.com/wiki/VOCALOID4
- VOCALOID5 | Vocal Synthesizer Wiki：https://vocalsynth.fandom.com/wiki/VOCALOID5
- VOCALOID6 | Vocal Synthesizer Wiki：https://vocalsynth.fandom.com/wiki/VOCALOID6

### 技术博客
- vsqx - KimI's DTM memo：https://kimi.secret.jp/wiki/dtm.php?vsqx
- VSQ のファイル仕様(推定) - cadencii_jp：https://w.atwiki.jp/boare/pages/16.html
- VSQX ファイルの役割と互換性：https://cmusic.work/vocaloid-251/

### 学术论文
- Expression Control of Singing Voice Synthesis (UPC)：https://www.tdx.cat/bitstream/handle/10803/361103/tmum.pdf

### 开源项目
- vpr-parser：https://github.com/0x24a/vpr-parser
- vocaloid5tools：https://github.com/TheerapakG/vocaloid5tools
- VOCALOIDParser (NuGet)：https://www.nuget.org/packages/VOCALOIDParser
- Cadencii：https://github.com/cadencii/cadencii
- UtaFormatix 3：https://sdercolin.github.io/utaformatix3/
- LibreSVIP：https://github.com/SoulMelody/LibreSVIP
- harmoloid2：https://github.com/sdercolin/harmoloid2

### 文件格式参考
- FileInfo - VSQX：https://fileinfo.com/extension/vsqx
- FileInfo - VPR：https://fileinfo.com/extension/vpr
- FileExt - VPR：https://filext.com/file-extension/VPR

---

*本文档基于公开的技术文档、官方手册、脚本 API 参考和第三方开源项目分析整理而成。*
