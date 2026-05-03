# 拆轨技法

> 多轨歌声合成工程的组织与管理

---

## 目录

1. [为什么拆轨](#1-为什么拆轨)
2. [多轨管理](#2-多轨管理)
3. [轨道类型与用途](#3-轨道类型与用途)
4. [轨道组织建议](#4-轨道组织建议)
5. [各软件的轨道限制](#5-各软件的轨道限制)
6. [拆轨弥补声库缺陷](#6-拆轨弥补声库缺陷)
7. [代码示例](#7-代码示例)

---

## 1. 为什么拆轨

### 拆轨的目的

拆轨（Track Splitting）是将一首歌拆分为多个独立轨道进行编辑的技术：

1. **和声处理**：为原曲添加和声层
2. **双轨效果**：同旋律双轨增加厚度
3. **耳语层**：添加耳语/气息层增加表现力
4. **垫音轨**：低音或高音垫音填充频谱
5. **分角色演唱**：不同虚拟歌手分担不同段落
6. **备份安全**：保留原版的同时进行实验性编辑

### 拆轨的典型应用场景

| 场景 | 轨道组织 | 效果 |
|------|---------|------|
| 标准流行 | Lead + Harmony x2 + Double | 丰满的和声 |
| 抒情慢歌 | Lead + Soft Double + 呼吸层 | 温柔深情 |
| 摇滚力量 | Lead + Shout Layer + Harmony | 力量爆发 |
| ACG 萌系 | Lead + Chipmunk Layer + 和声 | 可爱风格 |
| 合唱效果 | Lead x4 (声像分散) | 合唱团效果 |

---

## 2. 多轨管理

### 轨道命名规范

```
Track 1: Lead Vocal (主唱)
Track 2: Lead Double (双轨)
Track 3: Harmony High (高音和声)
Track 4: Harmony Low (低音和声)
Track 5: Whisper (耳语层)
Track 6: Shout (呐喊层)
Track 7: Pad Low (低音垫)
Track 8+: Instrument (伴奏轨)
```

### 轨道颜色管理

| 轨道类型 | 建议颜色 | HEX 示例 |
|---------|---------|---------|
| 主唱 | 蓝色 | `#4A90D9` |
| 双轨 | 浅蓝 | `#7AB8E8` |
| 高音和声 | 绿色 | `#5CB85C` |
| 低音和声 | 青色 | `#5BC0DE` |
| 耳语 | 紫色 | `#9B59B6` |
| 呐喊 | 红色 | `#E74C3C` |
| 垫音 | 灰色 | `#95A5A6` |
| 伴奏 | 黄色 | `#F1C40F` |

---

## 3. 轨道类型与用途

### 主唱轨 (Lead Vocal)

- **作用**：歌曲主旋律
- **音量**：0 dB（基准）
- **声像**：居中 (0)
- **参数**：标准设置，适度表情

### 双轨 (Lead Double)

- **作用**：与主唱同旋律，增加厚度
- **音量**：-3 ~ -6 dB（略低于主唱）
- **声像**：±15（轻微偏离中心）
- **参数**：与主唱相似但略有不同（如微小音高差异）
- **技巧**：使用不同声库或同一声库的不同设置

### 高音和声 (Harmony High)

- **作用**：在主旋律上方三度或五度和声
- **音量**：-4 ~ -6 dB
- **声像**：+20 ~ +40（偏右）
- **参数**：可能使用更明亮的音色（BRI 较高）
- **技巧**：注意和声与主旋律的音程关系

### 低音和声 (Harmony Low)

- **作用**：在主旋律下方三度或五度和声
- **音量**：-4 ~ -6 dB
- **声像**：-20 ~ -40（偏左）
- **参数**：可能使用更深沉的音色（GEN 调整）

### 耳语轨 (Whisper)

- **作用**：添加耳语/气息效果
- **音量**：-10 ~ -15 dB
- **声像**：宽声像（-50 ~ +50）
- **参数**：
  - VOCALOID: BRE 高 + DYN 低
  - UTAU: Breath Flag
  - SynthV: voicing 降低 + breathiness 升高

### 呐喊轨 (Shout)

- **作用**：爆发段落的强调层
- **音量**：-5 ~ -8 dB（仅在爆发段出现）
- **声像**：居中或 ±10
- **参数**：GWL (VOCALOID4+), tension (SynthV)

### 垫音轨 (Pad)

- **作用**：填充频谱空洞
- **音量**：-10 ~ -15 dB
- **声像**：宽声像
- **参数**：长音符，柔和音色

---

## 4. 轨道组织建议

### 标准流行歌曲轨道模板

```
┌──────────────────────────────────────┐
│ Track 8+ │ 伴奏轨 (Instrumental)      │
├──────────────────────────────────────┤
│ Track 7  │ Pad Low (低音垫，可选)      │
├──────────────────────────────────────┤
│ Track 6  │ Shout (呐喊层，爆发段)      │
├──────────────────────────────────────┤
│ Track 5  │ Whisper (耳语层)           │
├──────────────────────────────────────┤
│ Track 4  │ Harmony Low (低音和声)      │
├──────────────────────────────────────┤
│ Track 3  │ Harmony High (高音和声)     │
├──────────────────────────────────────┤
│ Track 2  │ Lead Double (双轨)         │
├──────────────────────────────────────┤
│ Track 1  │ Lead Vocal (主唱)          │ ← 0 dB, Center
└──────────────────────────────────────┘
```

### 混音参数速查

| 轨道 | 音量 (dB) | 声像 | 备注 |
|------|----------|------|------|
| Lead | 0 | 0 | 基准 |
| Double | -3 ~ -6 | ±15 | 增加厚度 |
| Harmony High | -4 ~ -6 | +35 | 右侧 |
| Harmony Low | -4 ~ -6 | -35 | 左侧 |
| Whisper | -10 | Wide | 氛围层 |
| Shout | -5 | ±10 | 爆发段 |
| Pad | -12 | Wide | 填充 |

### 轨道参数设置建议

#### VOCALOID

```xml
<!-- 主唱轨 - 标准设置 -->
<cc><id>DYN</id><posTick>0</posTick><value>64</value></cc>
<cc><id>BRE</id><posTick>0</posTick><value>10</value></cc>
<cc><id>BRI</id><posTick>0</posTick><value>64</value></cc>

<!-- 耳语轨 - 气声效果 -->
<cc><id>BRE</id><posTick>0</posTick><value>80</value></cc>
<cc><id>DYN</id><posTick>0</posTick><value>40</value></cc>
<cc><id>BRI</id><posTick>0</posTick><value>30</value></cc>
```

#### UTAU / OpenUtau

```ini
; 主唱轨 Flags
Flags=g+0B0

; 耳语轨 Flags
Flags=g+0B80
```

```yaml
# OpenUtau 轨道设置
tracks:
  - track_name: "Lead"
    volume: 0.0
    pan: 0.0
  - track_name: "Whisper"
    volume: -10.0
    pan: 0.0
```

#### SynthV

```json
{
  "tracks": [
    {
      "name": "Lead",
      "mixer": {"gain": 0, "pan": 0}
    },
    {
      "name": "Whisper",
      "mixer": {"gain": -10, "pan": 0}
    }
  ]
}
```

---

## 5. 各软件的轨道限制

| 软件 | 版本 | 最大轨道数 | 和声限制 | 导出格式 |
|------|------|-----------|---------|---------|
| VOCALOID 3 | 编辑器 | 16 轨 | 16 | .vsqx |
| VOCALOID 4 | 编辑器 | 16 轨 | 16 | .vsqx |
| VOCALOID 5 | Editor | 8 轨 | 16 | .vpr |
| VOCALOID 6 | Editor | 无限制 | 无限制 | .vpr |
| UTAU | 经典版 | 1 轨 | 无 | .ust |
| UTAU-Synth | Mac版 | 1 轨 | 无 | .ust |
| OpenUtau | 最新版 | 无限制 | 无 | .ustx |
| SynthV Studio | Basic | 3 轨 | 无 | .svp |
| SynthV Studio | Pro | 无限制 | 无 | .svp |
| SynthV Studio 2 | Basic | 3 轨 | 无 | .svp |
| SynthV Studio 2 | Pro | 无限制 | 无 | .svp |
| CeVIO CS | Free | 多轨 | 有 | .ccs |
| CeVIO AI | 商业版 | 多轨 | 有 | .ccs |
| ACE Studio | 桌面版 | 多轨 | 有 | .acep |

### 轨道类型限制

| 软件 | 歌声轨限制 | 伴奏轨支持 | 特殊轨道 |
|------|-----------|-----------|---------|
| VOCALOID 5 | 最大 8 | 是 | 不支持音频编辑 |
| VOCALOID 6 | 无限制 | 是 | 支持 AI 轨、音频轨 |
| OpenUtau | 无限制 | 是 (wave_parts) | - |
| SynthV | 3 (Basic) / 无限制 (Pro) | 是 | 伴奏轨 |
| CeVIO | 多轨 | 是 | Talk/Song 双模式 |

---

## 6. 拆轨弥补声库缺陷

拆轨除了用于和声与效果，还可用于**解决声库本身的质量缺陷**。详见 [voicebank_defects.md](voicebank_defects.md)。

### 音域拆轨

当歌曲音域超出主声库 Optimum Range 时：
- **低音轨**: 使用擅长低音的声库（如 VY2、KAITO）
- **高音轨**: 使用擅长高音的声库（如 Miku V4X Solid / Sweet、Rin）
- **切换点**: 选择小节线或休止处，重叠 1-2 个音符做交叉淡化

### 声区拆轨

针对真声/假声突变（如 kokone V3）：
- **真声轨**: 主音域使用主声库真声采样
- **假声轨**: 高音区切换到假声采样或专门高音声库

### XSY 辅助轨 (VOCALOID4+)

使用副声库弥补主声库缺陷：
- 在缺陷频段设置 `XSY` 参数，混入副声库音色
- 例如 ARSLOID V4 音质低，可搭配 Fukase V4 作为副声库

### 双重唱弥补

当声库音色单薄或辅音缺失时：
- 叠加另一声库演唱同旋律，增加厚度和清晰度
- 偏移 ±10-15 cents + 轻微延迟 10-30ms，避免相位抵消

---

## 7. 代码示例

### 生成多轨 USTX

```python
from ruamel.yaml import YAML

def create_multitrack_ustx(name, tracks_config):
    """
    生成多轨 USTX 文件
    
    tracks_config: list of dict with keys:
        - name: 轨道名
        - singer: 音源
        - phonemizer: 音素器
        - volume: 音量 (dB)
        - pan: 声像 (-100 to 100)
        - track_color: 颜色名
        - notes: 音符列表
    """
    data = {
        "name": name,
        "ustx_version": "0.6",
        "resolution": 480,
        "key": 0,
        "time_signatures": [{"bar_position": 0, "beat_per_bar": 4, "beat_unit": 4}],
        "tempos": [{"position": 0, "bpm": 120.0}],
        "tracks": [],
        "voice_parts": [],
        "expressions": {
            "dyn": {"name": "dynamics (curve)", "abbr": "dyn", "type": "Curve", "min": -240, "max": 120, "default_value": 0},
            "pitd": {"name": "pitch deviation (curve)", "abbr": "pitd", "type": "Curve", "min": -1200, "max": 1200, "default_value": 0},
            "vel": {"name": "velocity", "abbr": "vel", "type": "Numerical", "min": 0, "max": 200, "default_value": 100},
            "vol": {"name": "volume", "abbr": "vol", "type": "Numerical", "min": 0, "max": 200, "default_value": 100},
            "bre": {"name": "breath", "abbr": "bre", "type": "Numerical", "min": 0, "max": 100, "default_value": 0},
            "gen": {"name": "gender", "abbr": "gen", "type": "Numerical", "min": -100, "max": 100, "default_value": 0},
        }
    }
    
    for i, config in enumerate(tracks_config):
        # 轨道
        track = {
            "singer": config.get("singer", ""),
            "phonemizer": config.get("phonemizer", ""),
            "track_name": config.get("name", f"Track {i+1}"),
            "track_color": config.get("track_color", "Blue"),
            "mute": config.get("mute", False),
            "solo": config.get("solo", False),
            "volume": config.get("volume", 0.0),
            "pan": config.get("pan", 0.0),
            "voice_color_names": config.get("voice_color_names", [])
        }
        data["tracks"].append(track)
        
        # 歌声片段
        part = {
            "name": config.get("name", f"Part {i+1}"),
            "comment": "",
            "track_no": i,
            "position": 0,
            "duration": config.get("duration", 1920),
            "notes": config.get("notes", [])
        }
        data["voice_parts"].append(part)
    
    return data

# 使用示例
tracks = [
    {
        "name": "Lead",
        "singer": "Kasane Teto",
        "phonemizer": "JA VCV",
        "track_color": "Blue",
        "volume": 0.0,
        "pan": 0.0,
        "duration": 1920,
        "notes": [
            {"position": 0, "duration": 480, "tone": 60, "lyric": "do"},
            {"position": 480, "duration": 480, "tone": 62, "lyric": "re"}
        ]
    },
    {
        "name": "Harmony",
        "singer": "Kasane Teto",
        "phonemizer": "JA VCV",
        "track_color": "Green",
        "volume": -4.0,
        "pan": 30.0,
        "duration": 1920,
        "notes": [
            {"position": 0, "duration": 480, "tone": 64, "lyric": "mi"},
            {"position": 480, "duration": 480, "tone": 65, "lyric": "fa"}
        ]
    }
]

ustx_data = create_multitrack_ustx("Demo Song", tracks)

yaml = YAML()
with open("multitrack.ustx", "w", encoding="utf-8") as f:
    yaml.dump(ustx_data, f)
```

### 生成多轨 SVP

```python
import json
import uuid

def create_multitrack_svp(name, tracks_config):
    """
    生成多轨 SVP 文件
    
    tracks_config: list of dict with keys:
        - name: 轨道名
        - color: HEX 颜色
        - db_name: 声库名
        - db_lang: 语言
        - gain: 音量 (dB)
        - pan: 声像
        - notes: 音符列表
    """
    library = []
    tracks = []
    
    for i, config in enumerate(tracks_config):
        group_id = str(uuid.uuid4())
        
        # 创建 NoteGroup
        group = {
            "name": config.get("name", f"Track {i+1}"),
            "uuid": group_id,
            "notes": config.get("notes", []),
            "parameters": config.get("parameters", {})
        }
        library.append(group)
        
        # 创建轨道
        track = {
            "displayOrder": i,
            "name": config.get("name", f"Track {i+1}"),
            "color": config.get("color", "#4A90D9"),
            "dbDefaults": {
                "name": config.get("db_name", ""),
                "language": config.get("db_lang", "japanese"),
                "phoneset": "x-sampa"
            },
            "groups": [
                {
                    "groupID": group_id,
                    "timeOffset": 0,
                    "pitchOffset": 0,
                    "voice": {
                        "paramLoudness": config.get("loudness", 0),
                        "paramTension": config.get("tension", 0),
                        "paramBreathiness": config.get("breathiness", 0),
                        "paramGender": config.get("gender", 0),
                        "paramToneShift": config.get("tone_shift", 0)
                    },
                    "isInstrumental": False,
                    "muted": False
                }
            ],
            "mixer": {
                "gain": config.get("gain", 0),
                "pan": config.get("pan", 0),
                "mute": False,
                "solo": False
            }
        }
        tracks.append(track)
    
    project = {
        "version": 2,
        "timeAxis": {
            "tempo": [{"position": 0, "beatPerMinute": 120}],
            "measure": [{"position": 0, "numerator": 4, "denominator": 4}]
        },
        "tracks": tracks,
        "library": library,
        "renderConfig": {},
        "settings": {}
    }
    
    return project

# 使用示例
tracks = [
    {
        "name": "Lead",
        "color": "#4A90D9",
        "db_name": "Saki AI",
        "db_lang": "japanese",
        "gain": 0,
        "pan": 0,
        "notes": [
            {"onset": 0, "duration": 70560000, "lyrics": "do", "pitch": 60},
            {"onset": 70560000, "duration": 70560000, "lyrics": "re", "pitch": 62}
        ]
    },
    {
        "name": "Harmony",
        "color": "#5CB85C",
        "db_name": "Saki AI",
        "db_lang": "japanese",
        "gain": -4,
        "pan": 30,
        "notes": [
            {"onset": 0, "duration": 70560000, "lyrics": "mi", "pitch": 64},
            {"onset": 70560000, "duration": 70560000, "lyrics": "fa", "pitch": 65}
        ]
    }
]

project = create_multitrack_svp("Demo Song", tracks)

with open("multitrack.svp", "w", encoding="utf-8") as f:
    json.dump(project, f, ensure_ascii=False, indent=2)
```

---

## 参考链接

- Synthesizer V Studio 轨道管理: https://svdocs.dreamtonics.com/en/synthv/advanced-usage/arrangement
- OpenUtau 多轨编辑: https://github.com/stakira/OpenUtau/wiki
- VOCALOID 6 多轨功能: https://www.vocaloid.com/en/learn/ln6212
- VOCALOID 编辑器教程 (DTM station): https://www.dtmstation.com/archives/57332.html
- UTAU 和声教程: https://utau.us/
- 声库缺陷与拆轨策略: 参见 [voicebank_defects.md](voicebank_defects.md)

---

*本文档基于歌声合成领域公开资料、官方文档和社区经验整理。*
