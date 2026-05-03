# 歌词与音素特殊记号

> 歌声合成软件中常见的特殊记号、辅助音素与功能符号参考

---

## 目录

1. [VOCALOID 特殊记号](#1-vocaloid-特殊记号)
2. [Synthesizer V 特殊记号](#2-synthesizer-v-特殊记号)
3. [UTAU / OpenUtau 特殊记号](#3-utau--openutau-特殊记号)
4. [通用拆音与衔接记号](#4-通用拆音与衔接记号)
5. [跨引擎对照表](#5-跨引擎对照表)
6. [使用场景速查](#6-使用场景速查)

---

## 1. VOCALOID 特殊记号

### 1.1 辅助音素 (Auxiliary Phonemes)

VOCALOID 提供一组以方括号 `[ ]` 包裹的特殊音素，用于控制发音行为。

| 记号 | 全称 | 功能 | 典型用法 |
|------|------|------|----------|
| `[Asp]` | Aspiration (送气) | 元音对之间产生去声/混合效果，打破连贯过渡 | 修正日语声库中破碎的元音连接；模拟 /æ/ 等音 |
| `[Sil]` | Silence (静默) | 打断两个音素之间的双音过渡 (diaphonic transition) | 高 BPM 时保持短音符独立；生成断奏 (staccato) |
| `[br1]` ~ `[br5]` | Breath (呼吸) | 插入呼吸/吸气音效 | 乐句间添加自然呼吸；`[br1]` 最短，`[br5]` 最长 |
| `[*in]` / `[*out]` | Inhale / Exhale | VOCALOID 原始吸气/呼气音素 (V1/V2 时代) | 早期声库呼吸标记，现多被 `[brX]` 取代 |
| `[h]` | 喉音/气声 | 类似声门摩擦音的辅助音素 | 某些英语声库中使用 |

#### `[Asp]` 详解

`[Asp]` 是 VOCALOID 音素系统中遗留的"空槽"音素，但会影响渲染：

- **元音间去声**: 放在元音对之间时，使第二个元音产生去声和混合效果
- **混合音素**: 用于修正日语声库中"破碎"的音素组合（choppy combinations）
- **模拟新音**: 组合 `[e]` + `[Asp]` + `[a]` 可模拟类似 /æ/ 的效果

**注意**: 英语声库通常不需要 `[Asp]`，因为英语本身已有足够的过渡采样；相反英语更常用 `[Sil]` 来**阻止**不需要的连音。

#### `[Sil]` 详解

`[Sil]` 插入一个静默过渡，功能类似"音素截止阀"：

- **打断过渡**: 阻止前一个音素向后一个音素的自然双音过渡
- **断奏效果**: 在高 BPM 下保持小音符的独立性
- **休止模拟**: 可在音符内部创建短暂的静默间隙

```xml
<!-- 示例：在 ka 和 sa 之间插入完全断开 -->
<note><y>ka</y><p>k a</p></note>
<note><y>[Sil]</y><p>Sil</p></note>  <!-- 打断衔接 -->
<note><y>sa</y><p>s a</p></note>
```

#### `[br1]` ~ `[br5]` 详解

呼吸音素的长度分级：

| 记号 | 长度 | 使用场景 |
|------|------|----------|
| `[br1]` | 最短呼吸 | 快速乐句间的轻微换气 |
| `[br2]` | 短呼吸 | 正常乐句间隔 |
| `[br3]` | 中等呼吸 | 长乐句后的换气 |
| `[br4]` | 长呼吸 | 段落结束后的深呼吸 |
| `[br5]` | 最长呼吸 | 戏剧性的吸气/停顿 |

**已知问题**: 在 VOCALOID2 中，连续放置多个 `[brX]` 且不间隔时，部分呼吸可能不会被播放（取决于音符长度）。建议在呼吸音符前后留出适当空隙。

### 1.2 英语 VOCALOID 特殊音素

| 记号 | 说明 |
|------|------|
| `[R]` | 颤音 R（大舌音/卷舌音），日语声库需连续叠加闪音 `4` 模拟 |
| `[L]` | 音节化 L（Dark L），可独立使用并延长 |
| `[w]` / `[j]` | 滑音/半元音，用于双元音过渡 |

---

## 2. Synthesizer V 特殊记号

Synthesizer V 使用纯文本标记（无方括号），直接在歌词中输入。

| 记号 | 功能 | 说明 |
|------|------|------|
| `br` | 呼吸音 (Breath) | AI 歌手专用。作为独立音符的 lyrics 使用，或插入音素序列 |
| `cl` | 喉塞音 (Glottal Stop) | 在音符 lyrics 前加单引号 `'` 或使用 `cl` 音素创建硬起音 |
| `sil` | 静默 (Silence) | 强制静默，限制相邻音素时长。比 `cl` 更"人工" |
| `'` | 喉塞前缀 | 在歌词前加 `'` 如 `'apple`，在当前音符前插入喉塞音 |

### 2.1 `cl` (Glottal Stop / 硬起音)

**两种使用方式**:
1. **歌词前缀**: `'apple` → 在 `ae` 前插入 `cl` 音素，创建硬起音
2. **独立音符**: 创建一个仅含 `'` 的音符，在当前位置插入喉塞

**应用场景**:
- 英语中以元音开头的单词硬起音 (`'orange`)
- 乐句开头强调感
- 日语中模仿「っ」的停顿效果

### 2.2 `sil` vs `cl`

| | `sil` | `cl` |
|--|-------|------|
| 本质 | 绝对静默 | 模拟人类突然停止/恢复气流 |
| 听感 | 更人工、切割感强 | 更自然、符合人类习惯 |
| 使用场景 | 需要精确切断过渡 | 需要自然停顿或硬起音 |
| 对邻居音素影响 | 强制缩短相邻音素时长 | 允许引擎保留微小过渡 |

### 2.3 `br` (Breath)

- **AI 歌手专用**: Standard 歌手不支持 `br`
- **使用方式**: 独立音符 lyrics = `br`，或音素序列中插入 `br`
- **长度控制**: 通过音符时长控制呼吸长度
- **推荐做法**: 呼吸作为独立音符，而非音素的一部分

---

## 3. UTAU / OpenUtau 特殊记号

### 3.1 UTAU 歌词记号

| 记号 | 名称 | 功能 |
|------|------|------|
| `R` | 休止符 (Rest) | 静音休止，不播放任何采样 |
| `-` | 连音/延长 (Hold) | 延续前一音符的元音（VCV/CVVC 中的过渡）|
| `+` | 滑音/连接 (Slur) | 在某些音素器中用于标记连音或特殊过渡 |
| `br` | 呼吸 (Breath) | 部分音素器/声库支持的呼吸采样 |
| `bre` | 呼吸延长 | 延长型呼吸标记 |
| `息` | 呼吸 (日语) | 部分日语声库使用的呼吸记号 |
| `・` / `･` | 空拍/停顿 | 日语声库中类似 `[Sil]` 的短暂静默 |

#### `R` (休止符)

UTAU 中最基础的静默记号：
- 完全不播放任何音频
- 可用于强制切断前一音符尾音
- OpenUtau 中 `R` 音符不需要音源中存在 `R.wav`

#### `-` (连音/延长)

UTAU 中最常用但也最容易混淆的记号：

**在 CV 音源中**:
- `-` 通常被映射为纯元音延长，或声库作者自定义的行为
- 常见用法: `ka` → `a` (拆音) → `-` (延长元音)

**在 VCV 音源中**:
- `-` 表示"前一音符尾音过渡到当前音符"
- 如 `a ka` 结构中的前导元音

**在 OpenUtau 中**:
- 音素器 (Phonemizer) 自动处理 `-`，用户通常不需要手动输入
- 手动输入 `-` 可能触发音素器的特殊行为，取决于具体 phonemizer 实现

#### `br` / `bre` / `息` (呼吸)

- 不是所有声库都支持呼吸采样
- 支持情况取决于声库录制时是否包含呼吸音
- 在 OpenUtau 中，呼吸通常作为独立音符处理

### 3.2 OpenUtau 音素器特殊标记

OpenUtau 音素器 (Phonemizer) 定义了一些内部符号类型：

| 类型 | 符号示例 | 说明 |
|------|----------|------|
| `vowel` | `a`, `i`, `aa`, `eh` | 元音，过渡的基础 |
| `stop` | `p`, `t`, `k`, `cl` | 爆破音/停顿音 |
| `affricate` | `ch`, `jh`, `ts` | 塞擦音，优先发声 |
| `fricative` | `s`, `sh`, `f`, `h` | 摩擦音 |
| `aspirate` | `hh`, `h` | 送气音 |
| `liquid` | `l`, `r`, `4` | 流音 |
| `nasal` | `m`, `n`, `ng` | 鼻音 |
| `semivowel` | `w`, `y`, `j` | 半元音/滑音 |
| `tail` | `-` | 尾音标记，用于 trailing tail note |
| `diphthong` | `ay`, `aw`, `oy` | 双元音 |

**配置方式** (在声库的 `phonemes.yaml` 中):
```yaml
symbols:
  - {symbol: a, type: vowel}
  - {symbol: cl, type: stop}
  - {symbol: hh, type: aspirate}
  - {symbol: '-', type: tail}
  - {symbol: "'@r", type: vowel}  # 特殊符号需用引号包裹
```

### 3.3 ARPAsing 中的特殊记号

ARPAsing (英语 UTAU) 使用一些特殊过渡记号：

| 记号 | 说明 |
|------|------|
| `- V` | 词首元音，从静默过渡到元音 (如 `- ay` for "eye") |
| `C -` | 词尾辅音到静默 (如 `t -` for "cat") |
| `- C` | 词首辅音群过渡 (如 `- s` → `s t` → `t r` → `r ae`) |

---

## 4. 通用拆音与衔接记号

### 4.1 歌词层面的衔接控制

| 记号/写法 | 引擎 | 效果 |
|-----------|------|------|
| `ー` (长音) | 日语全引擎 | 元音延长 |
| `~` / `～` | 部分 UTAU 声库 | 元音延长 (非标准) |
| `ん` → `N` / `n` / `m` / `J` | 全引擎 | 拨音，根据上下文选择不同鼻音 |
| `っ` → `Q` / `cl` | VOCALOID / SV | 促音，无声除阻 |

### 4.2 工程层面的休止与呼吸

不同引擎表示休止和呼吸的方式：

| 概念 | VOCALOID | Synthesizer V | UTAU | OpenUtau |
|------|----------|---------------|------|----------|
| 休止 | 空音符 / `[Sil]` | `sil` 音符 | `R` | `R` |
| 呼吸 | `[br1]`~`[br5]` | `br` 音符 | `br` / `息` | `br` |
| 短休止 | 1/64 音符 | 短 `sil` | 短 `R` | 短 `R` |
| 硬起音 | `[Sil]` + 音符 | `'` 前缀 / `cl` | `Q` / `cl` | `cl` |

---

## 5. 跨引擎对照表

### 5.1 相同概念的不同表示

| 概念 | VOCALOID | Synthesizer V | UTAU | OpenUtau |
|------|----------|---------------|------|----------|
| 送气/过渡混合 | `[Asp]` | (无直接等价) | (依赖 oto) | (依赖 phonemizer) |
| 静默打断 | `[Sil]` | `sil` | `R` / `・` | `R` / `sil` |
| 喉塞音 | (用 `[Sil]` 近似) | `cl` / `'` | `Q` | `cl` / `Q` |
| 呼吸 | `[br1]`~`[br5]` | `br` | `br` / `bre` / `息` | `br` |
| 延长 | `ー` / 音符时值 | 音符时值 | `-` / 音符时值 | 音符时值 |
| 促音 | `Q` / 双写辅音 | `cl` | `Q` / 小音符 | `Q` / `cl` |

### 5.2 推荐对照使用

```
需求：在乐句间加入自然呼吸
  VOCALOID: 新建音符，lyric=[br2]，调整长度约 1/8 ~ 1/4 拍
  Synthesizer V: 新建音符，lyrics=br，AI歌手自动处理
  UTAU: 新建音符，Lyric=br 或 息（需声库支持）
  OpenUtau: 新建音符，lyric=br，或音素覆盖插入 br

需求：阻止元音间不必要的滑动
  VOCALOID: 插入 [Sil] 音符
  Synthesizer V: 使用 sil 音符（不推荐，优先调整音素边界）
  UTAU: 插入 R 或减小 Overlap
  OpenUtau: 使用 sil 音素覆盖或调整音符间隙
```

---

## 6. 使用场景速查

### 场景 1：日语声库元音连接太"碎"

```
VOCALOID: 在元音间插入 [Asp]，如 "a [Asp] i"
UTAU VCV: 确保使用 VCV 音源，前一元音尾音自动过渡
UTAU CV: 拆音后手动调整 Overlap 和 PreUtterance
```

### 场景 2：英语声库发音过于"黏连"

```
VOCALOID: 在不需要连音的音素间插入 [Sil]
Synthesizer V: 使用 ' 前缀或 cl 音素创建硬边界
ARPAsing: 词尾使用 "C -" 结构过渡到静默
```

### 场景 3：高 BPM 下短音符糊在一起

```
VOCALOID: 短音符间插入 [Sil] 音符，或降低 Overlap
UTAU: 减小短音符的 VoiceOverlap，或使用 Mode2 精确控制
Synthesizer V: 使用 sil 强制分隔，或缩小音符间距
```

### 场景 4：句尾气息不自然

```
VOCALOID: 句尾添加 [br3] ~ [br5] 呼吸音符
Synthesizer V: 句尾添加 br 音符，长度 1/4 ~ 1/2 拍
UTAU: 句尾添加 br / 息 / R (根据声库支持)
```

### 场景 5：需要突然的停顿效果

```
VOCALOID: 插入 1/64 音符 + [Sil]，或调整 CC 参数
Synthesizer V: 插入 sil 音符，长度 1/32 ~ 1/16 拍
UTAU: 插入 R 休止符，或减小音符间距到负值
```

---

## 参考链接

- VOCALOID Misc Phonetics: https://vocaloid.fandom.com/wiki/Misc_Phonetics
- VOCALOID Phoneme List: https://vocaloid.fandom.com/wiki/Phoneme_List
- Synthesizer V Phoneme Editing: https://manual.synthv.info/note-properties/editing-phonemes/
- OpenUtau Phonemizers: https://github.com/stakira/OpenUtau/wiki/Phonemizers
- ARPAsing UST Tutorial: http://utau.wikidot.com/tutorials:arpasing-ust-tutorial
- UTAU Special Characters: https://studio-ogien.com/tag/tutorial/

---

*本文档基于各歌声合成引擎官方文档、Fandom Wiki 社区资料及实际调音经验整理。*
