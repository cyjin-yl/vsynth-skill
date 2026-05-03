# 调音技法指南

> 歌声合成参数系统与调音实践

---

## 目录

1. [参数术语表](#1-参数术语表)
2. [各软件参数对照表](#2-各软件参数对照表)
3. [颤音技巧](#3-颤音技巧)
4. [滑音技巧](#4-滑音技巧)
5. [呼吸音技巧](#5-呼吸音技巧)
6. [音符衔接处理](#6-音符衔接处理)
7. [参数曲线编辑方法](#7-参数曲线编辑方法)

---

## 1. 参数术语表

### 核心参数中英对照

| 缩写 | 英文全称 | 中文名称 | 含义 | 通用范围 | 对应软件 |
|------|---------|---------|------|---------|---------|
| **PIT** | Pitch Bend | 音高弯曲 | 音高偏移控制 | -8192~+8191 | VOCALOID |
| **PBS** | Pitch Bend Sensitivity | 音高弯曲敏感度 | PIT 的最大影响范围（半音） | 1~24 | VOCALOID |
| **DYN** | Dynamics | 动态/响度 | 音量精细控制 | 0~127 | VOCALOID/UTAU |
| **VEL** | Velocity | 速度/辅音速度 | 控制辅音长度 | 0~127 | VOCALOID/UTAU |
| **BRE** | Breathiness | 呼吸度/气声 | 气息效果强度 | 0~127 | VOCALOID/UTAU |
| **BRI** | Brightness | 明亮度 | 高频内容调整 | 0~127 | VOCALOID |
| **CLE** | Clearness | 清晰度 | 声音锐利度 | 0~127 | VOCALOID |
| **OPE** | Opening | 开口度 | 口腔开合模拟 | 0~127 | VOCALOID |
| **GEN** | Gender Factor | 性别因子 | 共振峰偏移（性别倾向） | 0~127/-64~+63 | VOCALOID |
| **GWL** | Growl | 咆哮声 | 硬颤音/喉音效果 | 0~127 | VOCALOID4+ |
| **POR** | Portamento Timing | 滑音时机 | 连音偏移时刻 | 0~127 | VOCALOID |
| **VOL** | Volume | 音量 | 整体音量 | 0~200 | UTAU |
| **MOD** | Modulation | 调制 | 音高抖动保留度 | 0~100 | UTAU |
| **PITD** | Pitch Deviation | 音高偏差 | 音高曲线偏移 | -1200~+1200 cents | SynthV/OpenUtau |
| **LOU** | Loudness | 响度 | 音量精细控制 | -∞~+24 dB | SynthV |
| **TEN** | Tension | 张力 | 声音紧张/放松 | -2~+2 | SynthV |
| **VOI** | Voicing | 发声/虚实 | 真声到耳语渐变 | 0~100% | SynthV |
| **TON** | Tone Shift | 音区偏移 | 不改变音高改变音区 | -800~+800 cents | SynthV Pro |

### VOCALOID 扩展参数（V3+）

| 参数 | 全称 | 含义 | 范围 |
|------|------|------|------|
| XSY | Cross Synthesis | 交叉合成 | 0~127 |

### UTAU Flags 速查

| Flag | 含义 | 参数范围 | 说明 |
|------|------|---------|------|
| g | Gender | -100~100 | 正=女性向，负=男性向 |
| B | Breathiness | 0~100 | 气息强度 |
| H | Lowpass | 0~100 | 低通滤波器 |
| t | 音域微调 | 0~100 | 默认 50 |

### OpenUtau 表情参数

| 缩写 | 名称 | 类型 | 范围 | Flag |
|------|------|------|------|------|
| dyn | dynamics | Curve | -240~120 | - |
| pitd | pitch deviation | Curve | -1200~1200 | - |
| clr | voice color | Options | 0~-1 | - |
| vel | velocity | Numerical | 0~200 | - |
| vol | volume | Numerical | 0~200 | - |
| gen | gender | Numerical | -100~100 | `g` |
| bre | breath | Numerical | 0~100 | `B` |
| lpf | lowpass | Numerical | 0~100 | `H` |
| mod | modulation | Numerical | 0~100 | - |

---

## 2. 各软件参数对照表

### 参数功能映射

| 功能 | VOCALOID | UTAU | OpenUtau | Synthesizer V |
|------|---------|------|---------|--------------|
| 音高控制 | PIT (0~127) | PBS/PBW/PBY | pitd curve | pitchDelta |
| 音量/动态 | DYN (0~127) | Intensity | dyn curve | loudness |
| 辅音速度 | VEL (0~127) | Velocity | vel | - |
| 气息 | BRE (0~127) | - | bre | breathiness |
| 明亮度 | BRI (0~127) | - | - | - |
| 性别倾向 | GEN (0~127) | g Flag | gen | gender |
| 开口度 | OPE (0~127) | - | - | mouthOpening (V2) |
| 清晰度 | CLE (0~127) | - | - | - |
| 颤音 | Note Expression | VBR | vibrato | vibratoEnv |
| 连音/滑音 | POR | PBS/PBW | pitch curve | pitchDelta |
| 响度微调 | - | - | - | loudness (dB) |
| 张力 | - | - | - | tension |
| 浊度 | - | - | - | voicing |
| 音区偏移 | - | - | - | toneShift |

---

## 3. 颤音技巧

### 颤音参数体系

| 软件 | 参数 | 控制方式 |
|------|------|---------|
| VOCALOID | Note Expression | 音符属性面板 |
| UTAU | VBR | 逗号分隔数值 |
| OpenUtau | vibrato 对象 | 结构化参数 |
| SynthV | dF0Vbr, fF0Vbr, tF0VbrStart | 音符属性 + 参数面板 |

### 推荐颤音设置

| 参数 | 建议值 | 说明 |
|------|--------|------|
| 延迟 (Delay) | 120~300ms | 避免影响主音稳定性 |
| 深度 (Depth) | 从低开始逐步增加 | 控制颤音幅度 |
| 速率 (Rate) | 5~8 Hz | 歌手风格相关 |
| 频率 (Frequency) | 5.5 Hz 左右 | 通用推荐值 |
| 淡入 (Fade In) | 10~20% | 平滑开始 |
| 淡出 (Fade Out) | 10~20% | 平滑结束 |

### VOCALOID 颤音

VOCALOID 通过 Note Expression 或 PIT 手绘实现颤音。

```xml
<!-- VOCALOID 音符中的颤音属性 (nStyle) -->
<nStyle>
  <seq id="vibDep">
    <p>0</p><v>0</v>
    <p>65536</p><v>20</v>
  </seq>
  <seq id="vibRate">
    <p>0</p><v>65</v>
    <p>65536</p><v>65</v>
  </seq>
</nStyle>
```

### UTAU 颤音 (VBR)

```ini
# 颤音参数：长度,周期,深度,淡入,淡出,相位,偏移,强度,周期变化
VBR=65,160,35,20,20,0,0,0,0
```

### OpenUtau 颤音

```yaml
vibrato:
  length: 65       # 覆盖音符的百分比
  period: 175      # 周期（毫秒）
  depth: 25        # 深度（音分）
  in: 10           # 淡入（百分比）
  out: 10          # 淡出（百分比）
  shift: 0         # 相位偏移
  drift: 0         # 音高漂移
  vol_link: 0      # 音量关联
```

### SynthV 颤音

SynthV 使用 Vibrato Envelope（颤音包络线）控制颤音：

```json
{
  "vibratoEnv": {
    "mode": "linear",
    "points": [
      [0, 0],         # 起始无颤音
      [35280000, 1],  # 中段最大
      [70560000, 0.5] # 结束渐弱
    ]
  }
}
```

**音符级颤音属性**：

| 属性 | 含义 | 单位 |
|------|------|------|
| `tF0VbrStart` | 颤音开始时间 | 秒 |
| `tF0VbrLeft` | 左淡入时间 | 秒 |
| `tF0VbrRight` | 右淡出时间 | 秒 |
| `dF0Vbr` | 颤音深度 | 半音 |
| `fF0Vbr` | 颤音频率 | Hz |
| `pF0Vbr` | 颤音相位 | 弧度 (-π ~ π) |
| `dF0VbrMod` | 颤音调制深度 (V2) | - |

---

## 4. 滑音技巧

### 滑音类型

| 类型 | 说明 | 实现方式 |
|------|------|---------|
| 上升滑音 (Rise Portamento) | 从低滑入目标音 | VOCALOID: risePort / UTAU: PBY 负值 |
| 下降滑音 (Fall Portamento) | 从目标音滑出 | VOCALOID: fallPort / UTAU: PBY 正值 |
| 连音滑音 | 两个音符间的过渡 | POR / PBS 控制 |

### VOCALOID 滑音

```xml
<!-- VOCALOID Note Expression -->
<nStyle>
  <seq id="risePort">
    <p>0</p><v>0</v>
    <p>65536</p><v>30</v>
  </seq>
  <seq id="fallPort">
    <p>0</p><v>0</v>
  </seq>
</nStyle>
```

### UTAU Mode2 滑音

```ini
# 音符从下方滑入（PBY 负值起始）
PBS=-40
PBW=80,100
PBY=-30,0       # 起始偏移 -30 音分，回到 0
PBM=s,s
```

### OpenUtau 滑音

```yaml
pitch:
  data:
    - {x: -40.0, y: -30, shape: "io"}   # 起始偏移 -30 音分
    - {x: 40.0, y: 0, shape: "io"}         # 回到标准音高
  snap_first: true
```

### SynthV 滑音

使用 pitchDelta 参数曲线绘制滑音：

```json
{
  "pitchDelta": {
    "mode": "cubic",
    "points": [
      [0, -30],        # 起始偏移 -30 cents
      [35280000, 0],   # 中段标准
      [70560000, 0]    # 结束标准
    ]
  }
}
```

---

## 5. 呼吸音技巧

### 各软件呼吸音参数

| 软件 | 参数 | 范围 | 说明 |
|------|------|------|------|
| VOCALOID | BRE | 0~127 | 气息效果 |
| UTAU | B Flag | 0~100 | 气息强度 |
| OpenUtau | bre | 0~100 | 气息 |
| SynthV | breathiness | -1~+1 | 气声 |

### 调音建议

| 歌曲风格 | BRE/Breathiness | 说明 |
|---------|----------------|------|
| 抒情/柔和 | 较高 (+10~+30) | 增加温柔感 |
| 力量/爆发 | 较低 (0) | 增加力量感 |
| 耳语效果 | 极高 + voicing 低 | SynthV 中使用 |

### 呼吸音应用时机

- **音符开头**：自然气息的进入
- **休止符前**：气息的自然流出
- **情感句尾**：渐弱时的气息点缀
- **爆发音前**：通过降低 BRE 增加冲击感

---

## 6. 音符衔接处理

### 辅音速度 (VEL / Velocity)

| 软件 | 参数 | 效果 |
|------|------|------|
| VOCALOID | VEL (0~127) | 高 = 辅音短促、强调爆发；低 = 辅音柔和 |
| UTAU | Velocity (0~200%) | 百分比控制 |
| OpenUtau | vel (0~200) | 辅音速度 |

**调音建议**：
- 快速爆发音（如 k, t, p）：VEL 较高（100-127）
- 柔和过渡音（如 m, n, s）：VEL 适中（60-100）
- 长辅音（如 sh, f）：VEL 较低（40-80）

### 音符重叠与过渡

| 参数 | 说明 | 应用场景 |
|------|------|---------|
| PreUtterance | 先行发声 | 调整音符提前量 |
| Overlap | 重叠量 | 控制音符间重叠 |
| POR (VOCALOID) | 滑音时机 | 连音偏移时刻 |

---

## 7. 参数曲线编辑方法

### 通用原则

1. **不要过度调整**：保持自然，避免机械化
2. **从全局到局部**：先调整全局参数，再微调细节
3. **参考真人演唱**：听真人版本获取参数灵感
4. **保持参数一致性**：同一句内 PBS 保持统一
5. **使用平滑曲线**：避免参数突变

### VOCALOID 参数曲线 (CC)

```xml
<!-- 添加 DYN 控制事件 -->
<cc>
  <id>DYN</id>
  <posTick>0</posTick>
  <value>64</value>
</cc>
<cc>
  <id>DYN</id>
  <posTick>480</posTick>
  <value>80</value>
</cc>
```

### UTAU 曲线 (OpenUtau)

```yaml
curves:
  - xs: [0, 120, 240, 360, 480]    # tick 位置
    ys: [0, 10, 5, -5, 0]          # 音高偏移值
    abbr: "pitd"                    # pitch deviation
  - xs: [0, 480, 960, 1440, 1920]
    ys: [100, 100, 80, 90, 100]
    abbr: "dyn"                     # dynamics
```

### SynthV 参数曲线

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

### 参数曲线插值方式

| 方式 | 说明 | 适用场景 |
|------|------|---------|
| Linear | 线性插值 | 快速变化、明确转折 |
| Cosine | 余弦插值 | 平滑过渡 |
| Cubic | 三次样条 | 最自然的曲线 |

---

## 参考链接

- Expression Control of Singing Voice Synthesis (UPC): https://www.tdx.cat/bitstream/handle/10803/361103/tmum.pdf
- VOCALOID 参数详解 (cmusic.work): https://cmusic.work/vocaloid-455/
- VOCALOID 调音教程 (WikiVocaloid): https://wikivocaloid.com/zh-tw/tutorials/vocaloid-parameters/
- UTAU 参数解释 (ch.nicovideo.jp): https://ch.nicovideo.jp/utau/blomaga/ar1036303
- Synthesizer V 参数面板: https://svdocs.dreamtonics.com/en/synthv/advanced-usage/parameters
- OpenUtau 表情参数: https://github.com/stakira/OpenUtau/wiki/USTX-file-format
- 声库缺陷与拆轨策略: 参见 [voicebank_defects.md](voicebank_defects.md)
- 拆音技法: 参见 [phoneme_splitting.md](phoneme_splitting.md)

---

*本文档基于歌声合成领域公开资料、技术论文和社区经验整理。*
