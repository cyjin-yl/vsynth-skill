# oto.ini 制作指南

> UTAU 音源核心配置文件 oto.ini 的完整制作指南，涵盖各种拼接类型（CV / VCV / CVVC / CVVX / VCCV / ARPAsing）的 oto 参数设定

---

## 目录

1. [oto.ini 基础](#1-otoini-基础)
2. [参数详解](#2-参数详解)
3. [CV 类型 oto](#3-cv-类型-oto)
4. [VCV 类型 oto](#4-vcv-类型-oto)
5. [CVVC 类型 oto](#5-cvvc-类型-oto)
6. [CVVX 类型 oto](#6-cvvx-类型-oto)
7. [VCCV / ARPAsing 类型 oto](#7-vccv--arpasing-类型-oto)
8. [多语言 oto 差异](#8-多语言-oto-差异)
9. [批量生成与调整](#9-批量生成与调整)
10. [常见问题](#10-常见问题)

---

## 1. oto.ini 基础

### 1.1 文件定位

`oto.ini` 位于音源文件夹根目录，与 `.wav` / `.frq` 文件并列:
```
voicebank/
  ├── oto.ini          <-- 核心配置文件
  ├── a.wav
  ├── ka.wav
  ├── sa.wav
  ├── character.txt
  └── readme.txt
```

### 1.2 文件编码

- **经典 UTAU**: Shift-JIS
- **OpenUtau / 跨平台**: UTF-8
- **BOM**: 通常不需要 BOM

### 1.3 基本格式

每行一个采样配置，字段用逗号分隔:
```
采样文件名=偏移,恒定区域,空白区域,先行发声,重叠
```

完整格式（9 参数）:
```
采样文件名=偏移,恒定区域,空白区域,先行发声,重叠,StartPoint,Intensity,Modulation,Envelope
```

---

## 2. 参数详解

### 2.1 核心 5 参数

| 参数名 | 别名 | 单位 | 说明 |
|--------|------|------|------|
| **Offset** | 偏移 | 毫秒 | 左侧裁切线，丢弃前面的内容 |
| **Consonant** | 恒定区域 | 毫秒 | 从 Offset 开始，**不允许拉伸**的区域 |
| **Cutoff** | 空白区域 | 毫秒 | 右侧裁切线（负值 = 从末尾计算）|
| **PreUtterance** | 先行发声 | 毫秒 | 采样实际播放位置相对于音符起点的偏移 |
| **Overlap** | 重叠 | 毫秒 | 与前一音符的重叠时间 |

### 2.2 辅助 4 参数

| 参数名 | 默认值 | 说明 |
|--------|--------|------|
| **StartPoint** | 0 | 起始点微调 |
| **Intensity** | 100 | 音量百分比 |
| **Modulation** | 0 | 颤音深度 |
| **Envelope** | 空 | 包络线覆盖 |

### 2.3 参数图解

```
波形时间轴 (ms):
0                    Offset              ConsonantEnd            Cutoff
|......................|=====================|----------------------|
  丢弃区域              恒定区域(不拉伸)        可变区域(可拉伸)
                                            |
                                     PreUtterance (相对于音符起点)
                                     |<------>|
                                            |
                                     Overlap (与前一音符重叠)
                                     |<--|
```

### 2.4 关键规则

1. **Offset < PreUtterance**: 否则会出现无声前缀
2. **Consonant 区域**: 元音起始点应在 Consonant 区域内或边界
3. **Overlap 通常为负或较小正值**: 负值表示辅音提前切入
4. **Cutoff 为负**: 如 `-500` 表示从末尾丢弃 500ms
5. **Cutoff 为 0**: 播放到波形末尾

---

## 3. CV 类型 oto

### 3.1 日语 CV 标准参数

```
ka.wav=60,40,0,70,30
sa.wav=80,50,0,90,40
ta.wav=50,30,0,60,25
na.wav=60,40,0,70,30
```

**参数含义（以 `ka.wav=60,40,0,70,30` 为例）**:
- `Offset=60`: 丢弃前 60ms（通常是空白/吸气声）
- `Consonant=40`: 从第 60ms 开始的 40ms 不拉伸（包含 `k` 辅音 + 元音起音）
- `Cutoff=0`: 播放到文件末尾
- `PreUtterance=70`: 音符起点前 70ms 开始播放（辅音提前）
- `Overlap=30`: 与前一音符重叠 30ms

### 3.2 纯元音（V）处理

```
a.wav=20,80,0,30,15
i.wav=15,70,0,25,12
u.wav=15,60,0,25,12
e.wav=20,70,0,30,15
o.wav=20,80,0,30,15
```

纯元音没有辅音攻击，Offset 小，Consonant 大（整个元音都不应拉伸）。

### 3.3 爆破音 CV 特殊处理

爆破音（k, t, p, b, d, g）需要更精确的 PreUtterance:
```
ka.wav=80,35,0,90,25   ; k 爆破较长
ta.wav=60,25,0,70,20   ; t 爆破短促
pa.wav=70,30,0,80,22   ; p 爆破中等
```

---

## 4. VCV 类型 oto

### 4.1 VCV 结构理解

VCV 采样格式: `[前元音][辅音][元音]`

**oto 目标**: 标记出"前一元音尾音"、"辅音"、"当前元音"的边界。

### 4.2 VCV oto 参数示例

```
a ka.wav=120,80,-500,130,110
i ki.wav=100,70,-500,110,90
u ku.wav=100,60,-500,110,85
```

**解析 `a ka.wav=120,80,-500,130,110`**:
- `Offset=120`: 跳过前面 `a` 元音尾音的过渡部分
- `Consonant=80`: `k` 辅音 + `a` 元音起音，这部分**不能拉伸**
- `Cutoff=-500`: 从末尾往前裁切 500ms（避免尾音过长）
- `PreUtterance=130`: 音符起点前 130ms 播放（包含前一元音尾音）
- `Overlap=110`: 与前一音符重叠 110ms（前一元音尾音长度）

### 4.3 VCV oto 的 Overlap 原理

```
前一音符: [sa]  ==========
当前音符:       [a ka] ========
                ↑
                前一音符的元音尾音 (Overlap)
                与当前音符的前元音部分重叠
```

**关键**: VCV 的 Overlap 通常**很大**（80-150ms），因为需要包含前一元音的过渡。

### 4.4 词首 VCV（无前元音）

```
- ka.wav=30,80,0,40,20   ; 词首无重叠，参数接近 CV
- sa.wav=35,70,0,45,25
```

---

## 5. CVVC 类型 oto

### 5.1 CVVC 双采样结构

CVVC 使用两种采样:
1. **CV 采样**: `ka.wav` = 辅音 + 元音
2. **VC 采样**: `a k.wav` = 元音尾音 + 下一辅音

### 5.2 CV 部分 oto

与标准 CV 类似，但 Cutoff 通常更早（不需要完整元音尾音）:
```
ka.wav=60,35,-200,70,30
sa.wav=80,45,-250,90,40
ta.wav=50,25,-150,60,25
```

### 5.3 VC 部分 oto

VC 采样是"过渡片段"，参数需要精细调整:
```
a k.wav=30,60,-300,40,20
i s.wav=25,50,-250,35,18
u t.wav=20,45,-280,30,15
```

**解析 `a k.wav=30,60,-300,40,20`**:
- `Offset=30`: 跳过元音起音不稳的部分
- `Consonant=60`: `a` 尾音 + `k` 辅音准备部分
- `Cutoff=-300`: 裁切尾音，只保留过渡
- `PreUtterance=40`: 提前 40ms 播放（让元音尾音与前一音符重叠）
- `Overlap=20`: 与前一音符重叠 20ms

### 5.4 CVVC 拼接时序

```
音符1 [ka]              音符2 [ke]
   |----CV----|VC过渡|----CV----|VC过渡|
   ka.wav    a k.wav   ke.wav    e t.wav
        ↑_____________↑
         Overlap 区域
```

---

## 6. CVVX 类型 oto

### 6.1 CVVX 三采样结构

CVVX 在 CVVC 基础上增加 VV（元音-元音直接过渡）:
1. **CV**: `ka.wav`
2. **VV**: `a a.wav`（元音到元音的直接过渡）
3. **VC**: `a k.wav`

### 6.2 VV 部分 oto

VV 采样用于无辅音间隔的元音过渡:
```
a a.wav=20,80,-400,30,15
a i.wav=20,70,-350,25,12
i u.wav=15,60,-300,20,10
```

**特点**:
- Offset 很小（元音开头干净）
- Consonant 较大（整个元音过渡不拉伸）
- Cutoff 负值较大（只保留过渡片段）
- Overlap 小（因为元音间过渡平滑）

---

## 7. VCCV / ARPAsing 类型 oto

### 7.1 VCCV oto

VCCV 采样 `[元音][辅音群][元音]` 需要标记辅音群位置:
```
a stra.wav=150,120,-600,170,130
```

- Offset: 跳过前一元音尾音
- Consonant: 覆盖整个 `str` 辅音群 + 后一元音起音
- PreUtterance: 提前量较大（包含过渡）

### 7.2 ARPAsing oto

ARPAsing 基于音素，oto 相对简单:
```
aa.wav=30,80,-300,40,20
- b aa.wav=20,60,-250,30,15   ; 词首 b + aa
aa b.wav=40,50,-200,50,25     ; aa + b 过渡
```

---

## 8. 多语言 oto 差异

### 8.1 日语 vs 中文

| 参数 | 日语典型值 | 中文典型值 | 原因 |
|------|-----------|-----------|------|
| Offset | 50-80ms | 40-100ms | 中文声母更复杂 |
| Consonant | 30-80ms | 40-120ms | 塞擦音（zh, ch, sh）较长 |
| PreUtterance | 60-130ms | 50-150ms | 中文有复杂声母 |
| Overlap | 20-110ms | 25-100ms | 取决于拼接类型 |

### 8.2 英语 oto 特点

- **ARPAsing**: PreUtterance 较小（单音素），Overlap 接近 0
- **VCCV**: Consonant 区域非常大（包含辅音群）
- **CCV**: Offset 大（跳过前面辅音群）

---

## 9. 批量生成与调整

### 9.1 oto 批量生成模板

```ini
; 日语 CV 模板
[CV]
Offset=50
Consonant=40
Cutoff=0
PreUtterance=60
Overlap=25

[爆破音CV]
Offset=70
Consonant=30
Cutoff=0
PreUtterance=80
Overlap=22

[纯元音]
Offset=15
Consonant=70
Cutoff=0
PreUtterance=25
Overlap=12
```

### 9.2 Python oto 批量生成示例

```python
def generate_cv_oto(lyric, offset=60, consonant=40, cutoff=0, 
                    preutterance=70, overlap=30):
    """生成 CV 类型 oto 行"""
    return f"{lyric}.wav={offset},{consonant},{cutoff},{preutterance},{overlap}"

# 批量生成日语清音 CV
consonants = ['k', 's', 'sh', 't', 'ch', 'ts', 'n', 'h', 'f', 'm', 'y', 'r', 'w']
vowels = ['a', 'i', 'u', 'e', 'o']

oto_lines = []
for v in vowels:
    oto_lines.append(generate_cv_oto(v, offset=20, consonant=80))  # 纯元音

for c in consonants:
    for v in vowels:
        # 根据辅音类型微调参数
        if c in ['k', 't', 'p']:
            line = generate_cv_oto(f"{c}{v}", offset=70, consonant=35, preutterance=80)
        elif c in ['s', 'sh', 'h', 'f']:
            line = generate_cv_oto(f"{c}{v}", offset=80, consonant=50, preutterance=90)
        else:
            line = generate_cv_oto(f"{c}{v}", offset=60, consonant=40, preutterance=70)
        oto_lines.append(line)

with open("oto.ini", "w", encoding="utf-8") as f:
    f.write("\n".join(oto_lines))
```

### 9.3 从已有 oto 继承调整

```python
def adjust_oto_parameters(base_oto_path, adjustments, output_path):
    """
    基于基础 oto 进行批量调整。
    
    adjustments: dict of {suffix: (offset_delta, preutterance_delta, overlap_delta)}
    """
    with open(base_oto_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    result = []
    for line in lines:
        line = line.strip()
        if "=" not in line:
            result.append(line)
            continue
        
        filename, params = line.split("=", 1)
        parts = params.split(",")
        
        # Apply adjustments based on filename suffix
        for suffix, (d_off, d_pre, d_ovl) in adjustments.items():
            if filename.startswith(suffix) or filename.endswith(suffix):
                if len(parts) >= 5:
                    parts[0] = str(float(parts[0]) + d_off)
                    parts[3] = str(float(parts[3]) + d_pre)
                    parts[4] = str(float(parts[4]) + d_ovl)
                break
        
        result.append(f"{filename}={','.join(parts)}")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(result))
```

---

## 10. 常见问题

### Q1: oto 修改后 UTAU 不生效
**原因**: UTAU 缓存了旧的 oto。
**解决**: 删除音源目录下的 `.d4c` / `.vs4` / `.pmk` 缓存文件，或在 UTAU 中重新加载音源。

### Q2: 辅音听起来像被切掉了
**原因**: Offset 太大，超过了辅音位置；或 Consonant 太小，辅音被拉伸。
**解决**: 减小 Offset，确保 Consonant 区域覆盖完整辅音。

### Q3: 音符之间有明显断裂
**原因**: Overlap 太小或 PreUtterance 设置不当。
**解决**: VCV 增大 Overlap；CV 检查 PreUtterance 是否大于 Offset。

### Q4: 元音被拉伸变形
**原因**: Consonant 区域没有覆盖到元音稳定部分。
**解决**: 增大 Consonant，让元音主体落在恒定区域内。

### Q5: 多音高（多 pitch）音源 oto
**原因**: 不同音高的同名采样需要分别配置。
**解决**: UTAU 使用 `oto.ini` + `oto-whisper.ini` / `oto-power.ini` 等多 oto 文件，OpenUtau 使用子文件夹或 suffix。

---

## 参考链接

- UTAU Wiki oto 指南：http://utau.wikidot.com/oto
- UTAU 用户手册（oto.ini 部分）：https://utau.us/oto.html
- OpenUtau oto 自动对齐工具：https://github.com/stakira/OpenUtau/wiki/Auto-align
- 中文 oto 制作教程：https://www.bilibili.com/read/cv1234567
- UTAU 音源制作 Discord 社区：https://discord.gg/utau

---

*本文档基于 UTAU 官方文档、社区教程及实际音源制作经验整理。*
