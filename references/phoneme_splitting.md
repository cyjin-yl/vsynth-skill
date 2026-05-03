# 拆音技法

> 将音符拆分为辅音和元音的技术，用于更精细的歌声音素控制

---

## 目录

1. [为什么拆音](#1-为什么拆音)
2. [拆音的基本原理](#2-拆音的基本原理)
3. [不同软件的拆音方法](#3-不同软件的拆音方法)
4. [辅音和元音分离技巧](#4-辅音和元音分离技巧)
5. [最佳实践](#5-最佳实践)
6. [代码示例](#6-代码示例)

---

## 1. 为什么拆音

### 拆音的目的

拆音（Phoneme Splitting）是将一个完整音符拆分为多个发音片段的技术，目的是：

1. **精细控制辅音长度**：单独调整辅音的时长和音量
2. **优化音符衔接**：让辅音提前发声，元音准时切入
3. **改善发音清晰度**：避免辅音被吞掉或过快
4. **实现特殊效果**：如颤音从元音部分开始、省略某些辅音等
5. **跨引擎兼容**：不同声库对同一音符的发音特性不同，拆音可针对性调整

### 拆音的典型应用场景

| 场景 | 拆音方案 | 效果 |
|------|---------|------|
| 快速歌词 | 分离辅音和元音 | 每个音素独立控制 |
| 抒情长音 | 辅音极短 + 元音长音 | 柔美过渡 |
| 爆破音强调 | 辅音独立音符 + 高 VEL | 冲击力 |
| 气息声效果 | 省略辅音或弱化 | 耳语感 |
| 连音优化 | 辅音与前一音符重叠 | 流畅过渡 |

---

## 2. 拆音的基本原理

### 日语音节结构

日语音节通常为 CV 结构（辅音 + 元音）：

| 假名 | 辅音 | 元音 |
|------|------|------|
| か (ka) | k | a |
| さ (sa) | s | a |
| た (ta) | t | a |
| な (na) | n | a |
| は (ha) | h | a |
| ま (ma) | m | a |
| ら (ra) | r | a |

**特殊情况**：
- 元音开头：あ (a)、い (i)、う (u)、え (e)、お (o) —— 只有元音，无辅音
- 拗音：きゃ (kya)、しゃ (sha) —— 辅音 + 半元音 + 元音
- 拨音：ん (n) —— 鼻音辅音
- 促音：っ —— 停顿或双重辅音

### 英语音节结构

英语音节更复杂，可能为 CCVCC 等结构：

| 单词 | 音素序列 |
|------|---------|
| cat | k ae t |
| strength | s t r eh ng k th |
| hello | hh ah l ow |

---

## 3. 不同软件的拆音方法

### VOCALOID 拆音

VOCALOID 的拆音通过**创建多个音符**实现：

**方法 1：Note 级别拆分**
```
原音符: [か] (四分音符)
拆音后: [k] (16分音符) + [a] (剩余时值)
```

**方法 2：Note Expression**
- 使用 Note Expression 面板中的音素调整功能
- 修改单个音符内辅音和元音的比例

**VOCALOID 音素格式**：使用 X-SAMPA 格式，详见 [xsampa.md](xsampa.md)
```xml
<note>
  <y>cat</y>
  <p>k ae t</p>    <!-- X-SAMPA 音素，空格分隔 -->
</note>
```

**VOCALOID 拆音最佳实践**:
- 日语：爆破音 (k,t,p,b,d,g) 拆音比例 10-15%，摩擦音 20-30%，鼻音 15-20%
- 英语：复杂辅音群 (str, spl) 可拆分为多个音符，每个音符一个音素
- 跨语言时，使用 X-SAMPA 统一标记确保音素准确性

### UTAU / OpenUtau 拆音

UTAU 拆音方式最灵活，需结合音源拼接类型理解：

**方法 1：音符拆分（UTAU，依赖音源类型）**
```
原音符: [か] (Length=480)
拆音后: 
  [k] (Length=60, Lyric=k) + [a] (Length=420, Lyric=a)
```

拆音效果受音源拼接类型影响：
- **CV 音源**: 拆音后每个音符调用独立采样，可能不自然
- **VCV 音源**: 前一音符尾音自动过渡，拆音更自然
- **CVVC 音源**: OpenUtau 自动处理 CV 和 VC 采样衔接
- **CVVX 音源**: 元音间可使用 VV 采样实现平滑过渡

**方法 2：自动拆音（OpenUtau）**
- OpenUtau 使用**音素器 (Phonemizer)** 自动拆分
- 不同音素器使用不同的 CV/VC/VCV 拆分策略
- 常见的音素器：`JA CVVC`、`JA VCV`、`EN ARPAsing`、`ZH CVVC` 等
- 音素器选择取决于音源录音表类型，详见 [utau_voicebank.md](utau_voicebank.md)

**方法 3：音素覆盖（OpenUtau）**
```yaml
notes:
  - lyric: "ka"
    phoneme_overrides:
      - {index: 0, phoneme: "k"}      # 强制使用 k
      - {index: 1, phoneme: "a", offset: 65}  # 调整元音位置
```

### Synthesizer V 拆音

Synthesizer V 提供**音素时序面板**：

**方法 1：音素时长调整**
```json
{
  "attributes": {
    "dur": [0.5, 1.0, 0.8]    // 音素时长缩放（0.2-1.8）
  }
}
```

**方法 2：音素级偏移**
```json
{
  "attributes": {
    "phonemes": [
      {"leftOffset": 0, "position": 0, "activity": 1.0, "strength": 1.0},
      {"leftOffset": 0, "position": 0.4, "activity": 1.0, "strength": 1.0}
    ]
  }
}
```

**方法 3：自定义音素序列**
```json
{
  "lyrics": "cat",
  "phonemes": "k ae t"    // 空格分隔的 X-SAMPA 音素
}
```

### DiffSinger / NEUTRINO 拆音

这些 AI 引擎使用音素序列而非音符拆分：

**DiffSinger .ds 格式**：
```json
{
  "text": "试 着 掬 一 把",
  "ph_seq": "sh ir zh e j v y i b a",
  "ph_dur": "0.209 0.2554 0.1509 0.5921 0.1045 ...",
  "ph_num": "2 2 1 2 2"    // 每个音符的音素数量
}
```

---

## 4. 辅音和元音分离技巧

### 辅音处理原则

| 辅音类型 | 处理建议 | 示例 |
|---------|---------|------|
| 爆破音 (k, t, p, b, d, g) | 缩短辅音音符，提高 VEL | か → k(短) + a |
| 摩擦音 (s, sh, f, h) | 辅音音符较长，流畅过渡 | さ → s(适中) + a |
| 鼻音 (m, n) | 可与前一音符重叠 | な → n(重叠) + a |
| 流音 (r, l) | 辅音较短，快速过渡 | ら → r(短) + a |
| 拨音 (ん) | 独立音符或融入前一音符 | ん → n(单独) |

### 元音处理原则

1. **元音是音色的主体**：保持元音的时值和音高稳定
2. **长音的元音**：可以使用颤音或音高波动增加自然感
3. **短音的元音**：确保发音清晰，不要过短
4. **尾音处理**：句尾元音可以适度渐弱

### 拆音比例参考

| 音节类型 | 辅音比例 | 元音比例 | 说明 |
|---------|---------|---------|------|
| 标准 CV | 15-25% | 75-85% | 如 か、さ、た |
| 爆破音开头 | 10-15% | 85-90% | 如 か、た、ぱ |
| 摩擦音开头 | 20-30% | 70-80% | 如 さ、し、ふ |
| 鼻音开头 | 15-20% | 80-85% | 如 な、ま |
| 元音开头 | 0% | 100% | 如 あ、い、う |

### 重叠拆音（OpenUtau / 高级技巧）

```
音符 1: [か] ────────────────
音符 2:     [し] ─────────────
音符 3:         [て] ─────────

拆音后: 
  k ─┬─ a ───┐
     │       │
     s ─┬─ i─┘
        │
        t ─┬─ e
           │
           ...
```

---

## 5. 最佳实践

### 拆音工作流程

```
1. 分析歌词 → 识别每个音节的 CV 结构
2. 确定拆音点 → 在辅音和元音之间分割
3. 调整辅音时长 → 根据辅音类型设定比例
4. 调整辅音力度 → 确保清晰但不过度
5. 微调衔接 → 使用 Overlap/VEL 优化过渡
6. 试听检查 → 确保自然流畅
```

### 避免常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 辅音过短听不清 | 拆音比例不当 | 增加辅音比例到 20-30% |
| 辅音过长拖沓 | 拆音比例过大 | 缩短辅音到 10-15% |
| 音节断裂感 | 衔接不自然 | 增加 Overlap，使用滑音 |
| 元音被吞掉 | 辅音过于强势 | 降低辅音力度，使用 VEL |
| 机械感 | 所有音符拆音一致 | 根据上下文变化拆音比例 |

### 不同风格的拆音策略

| 歌曲风格 | 拆音策略 |
|---------|---------|
| 流行/快节奏 | 辅音短促，元音饱满 |
| 抒情/慢歌 | 辅音柔和，元音拉长 |
| 摇滚/力量 | 辅音强调，VEL 较高 |
| ACG/动漫 | 标准拆音，适当修饰 |
| 古典/严肃 | 精细拆音，注意呼吸 |

---

## 6. 代码示例

### 自动拆音辅助函数

```python
def split_cv_note(lyric, consonant_duration_ratio=0.2):
    """
    将 CV 结构的音符拆分为辅音和元音
    
    lyric: 假名歌词（如 'ka', 'sa', 'a'）
    consonant_duration_ratio: 辅音占总时长的比例
    
    返回: [(consonant_lyric, ratio), (vowel_lyric, ratio)]
    """
    # 日语 CV 映射
    cv_map = {
        'ka': ('k', 'a'), 'ki': ('k', 'i'), 'ku': ('k', 'u'), 'ke': ('k', 'e'), 'ko': ('k', 'o'),
        'sa': ('s', 'a'), 'shi': ('sh', 'i'), 'su': ('s', 'u'), 'se': ('s', 'e'), 'so': ('s', 'o'),
        'ta': ('t', 'a'), 'chi': ('ch', 'i'), 'tsu': ('ts', 'u'), 'te': ('t', 'e'), 'to': ('t', 'o'),
        'na': ('n', 'a'), 'ni': ('n', 'i'), 'nu': ('n', 'u'), 'ne': ('n', 'e'), 'no': ('n', 'o'),
        'ha': ('h', 'a'), 'hi': ('h', 'i'), 'fu': ('f', 'u'), 'he': ('h', 'e'), 'ho': ('h', 'o'),
        'ma': ('m', 'a'), 'mi': ('m', 'i'), 'mu': ('m', 'u'), 'me': ('m', 'e'), 'mo': ('m', 'o'),
        'ya': ('y', 'a'), 'yu': ('y', 'u'), 'yo': ('y', 'o'),
        'ra': ('r', 'a'), 'ri': ('r', 'i'), 'ru': ('r', 'u'), 're': ('r', 'e'), 'ro': ('r', 'o'),
        'wa': ('w', 'a'), 'wo': ('w', 'o'),
        'ga': ('g', 'a'), 'gi': ('g', 'i'), 'gu': ('g', 'u'), 'ge': ('g', 'e'), 'go': ('g', 'o'),
        'za': ('z', 'a'), 'ji': ('j', 'i'), 'zu': ('z', 'u'), 'ze': ('z', 'e'), 'zo': ('z', 'o'),
        'da': ('d', 'a'), 'di': ('d', 'i'), 'du': ('d', 'u'), 'de': ('d', 'e'), 'do': ('d', 'o'),
        'ba': ('b', 'a'), 'bi': ('b', 'i'), 'bu': ('b', 'u'), 'be': ('b', 'e'), 'bo': ('b', 'o'),
        'pa': ('p', 'a'), 'pi': ('p', 'i'), 'pu': ('p', 'u'), 'pe': ('p', 'e'), 'po': ('p', 'o'),
        'a': ('', 'a'), 'i': ('', 'i'), 'u': ('', 'u'), 'e': ('', 'e'), 'o': ('', 'o'),
        'n': ('n', ''), 'm': ('m', ''),
    }
    
    lyric_lower = lyric.lower()
    
    if lyric_lower in cv_map:
        c, v = cv_map[lyric_lower]
        if not c:  # 纯元音
            return [(v, 1.0)]
        if not v:  # 纯辅音
            return [(c, 1.0)]
        return [(c, consonant_duration_ratio), (v, 1.0 - consonant_duration_ratio)]
    
    # 未知歌词，不拆音
    return [(lyric, 1.0)]

# 使用示例
result = split_cv_note("ka", 0.2)
print(result)  # [('k', 0.2), ('a', 0.8)]

result = split_cv_note("a", 0.2)
print(result)  # [('a', 1.0)]
```

### 为 UTAU 生成拆音音符

```python
def generate_split_notes(notes, consonant_ratio=0.2):
    """
    为 UTAU 音符列表生成拆音后的音符
    
    notes: list of dict with 'lyric' and 'duration' keys
    返回: 拆音后的音符列表
    """
    result = []
    
    for note in notes:
        lyric = note['lyric']
        duration = note['duration']
        
        parts = split_cv_note(lyric, consonant_ratio)
        
        if len(parts) == 1:
            # 不拆音
            result.append(note)
        else:
            # 拆音
            current_pos = note.get('position', 0)
            for phoneme, ratio in parts:
                sub_duration = int(duration * ratio)
                if sub_duration < 1:
                    sub_duration = 1
                
                sub_note = {
                    'lyric': phoneme,
                    'duration': sub_duration,
                    'position': current_pos,
                    'notenum': note.get('notenum', 60),
                    'intensity': note.get('intensity', 100),
                    'modulation': note.get('modulation', 0),
                }
                result.append(sub_note)
                current_pos += sub_duration
    
    return result
```

### VOCALOID 音素格式生成

```python
def generate_xsampa_phonemes(lyric, language="japanese"):
    """
    生成 X-SAMPA 音素序列
    
    简单示例，实际应使用完整的音素映射表
    """
    # 日语假名到 X-SAMPA 映射（简化）
    phoneme_map = {
        'a': 'a', 'i': 'i', 'u': 'u', 'e': 'e', 'o': 'o',
        'ka': 'k a', 'ki': 'k i', 'ku': 'k u', 'ke': 'k e', 'ko': 'k o',
        'sa': 's a', 'shi': 'S i', 'su': 's u', 'se': 's e', 'so': 's o',
        'ta': 't a', 'chi': 'tS i', 'tsu': 'ts u', 'te': 't e', 'to': 't o',
        'na': 'n a', 'ni': 'J i', 'nu': 'n u', 'ne': 'n e', 'no': 'n o',
        'ha': 'h a', 'hi': 'C i', 'fu': 'p\ u', 'he': 'h e', 'ho': 'h o',
        'ma': 'm a', 'mi': 'm i', 'mu': 'm u', 'me': 'm e', 'mo': 'm o',
        'ya': 'j a', 'yu': 'j u', 'yo': 'j o',
        'ra': '4 a', 'ri': '4 i', 'ru': '4 u', 're': '4 e', 'ro': '4 o',
        'wa': 'w a', 'wo': 'w o',
        'ga': 'g a', 'gi': 'g i', 'gu': 'g u', 'ge': 'g e', 'go': 'g o',
        'za': 'dz a', 'ji': 'dZ i', 'zu': 'dz u', 'ze': 'dz e', 'zo': 'dz o',
        'da': 'd a', 'di': 'd i', 'du': 'd u', 'de': 'd e', 'do': 'd o',
        'ba': 'b a', 'bi': 'b i', 'bu': 'b u', 'be': 'b e', 'bo': 'b o',
        'pa': 'p a', 'pi': 'p i', 'pu': 'p u', 'pe': 'p e', 'po': 'p o',
        'n': 'n', 'm': 'm',
    }
    
    lyric_lower = lyric.lower()
    return phoneme_map.get(lyric_lower, lyric)

# 使用示例
print(generate_xsampa_phonemes("ka"))   # "k a"
print(generate_xsampa_phonemes("shi")) # "S i"
```

---

## 参考链接

- VOCALOID 音素编辑器: https://vocaloid.fandom.com/wiki/Phoneme
- X-SAMPA 完整参考: 参见 [xsampa.md](xsampa.md)
- OpenUtau 音素器 Wiki: https://github.com/stakira/OpenUtau/wiki/Phonemizer
- UTAU 拆音教程 (cmusic.work): https://cmusic.work/vocaloid-455/
- Synthesizer V 音素时序面板: https://svdocs.dreamtonics.com/en/synthv/advanced-usage/timing
- UTAU 音源拼接类型: 参见 [utau_voicebank.md](utau_voicebank.md)
- oto.ini 参数与拆音配合: 参见 [oto_ini.md](oto_ini.md)

---

*本文档基于歌声合成领域公开资料、社区经验和实际调音实践整理。*
