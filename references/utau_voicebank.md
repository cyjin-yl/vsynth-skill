# UTAU 音源录音表与拼接类型

> UTAU 音源制作涉及的录音表设计、拼接类型（CV / VCV / CVVC / CVVX / VCCV / ARPAsing 等）及各语言实现

---

## 目录

1. [拼接类型概览](#1-拼接类型概览)
2. [日语录音表](#2-日语录音表)
3. [英语录音表](#3-英语录音表)
4. [中文录音表](#4-中文录音表)
5. [韩语录音表](#5-韩语录音表)
6. [其他语言](#6-其他语言)
7. [录音表格式规范](#7-录音表格式规范)

---

## 1. 拼接类型概览

### 1.1 常见拼接类型对比

| 类型 | 全称 | 拼接单位 | 优点 | 缺点 | 适用场景 |
|------|------|----------|------|------|----------|
| **CV** | Consonant-Vowel | 辅音+元音 | 录音量少，易于制作 | 连贯性差，机械感 | 初学者、效果音 |
| **VCV** | Vowel-Consonant-Vowel | 元音+辅音+元音 | 连贯自然，音质好 | 录音量大，oto复杂 | 高质量日语音源 |
| **CVVC** | CV + VC | 辅音+元音 + 元音+辅音 | 平衡自然度和工作量 | 需要 VC 部分 | OpenUtau 主流 |
| **CVVX** | CV + VV + VX | CV + 元音过渡 + 尾音 | 更平滑的元音过渡 | 录音量更大 | 高品质音源 |
| **VCCV** | Vowel-CC-Vowel | 元音+辅音群+元音 | 英语等多辅音语言 | 录音量极大 | 英语音源 |
| **ARPAsing** | ARPAbet + Singing | 英语音素 | 英语自然度高 | 仅适用于英语 | 英语 UTAU |
| **CCV / CC-CV** | - | 辅音群+元音 | 处理复杂辅音开头 | 录音量大 | 俄语等 |
| **CV-VC** | - | 单独录制 CV 和 VC | 灵活组合 | 需要精密对齐 | 多语言音源 |

### 1.2 拼接方式图解

**CV (单一拼接)**:
```
[ka] [ra] [o] [ke] [ta]
  |    |    |    |    |
 独立采样，无重叠过渡
```

**VCV (前后元音拼接)**:
```
  a    i    o    e
   \  / \  / \  /
    ka  ro  ke
```
每个采样包含前一元音的尾音 + 当前音节

**CVVC (CV + VC 拼接)**:
```
[ka] [a k] [ke] [e t] [ta]
  CV   VC   CV   VC   CV
```
CV 提供辅音攻击，VC 提供元音到下一辅音的过渡

**CVVX (CV + VV + 尾音)**:
```
[ka] [a a] [a k] [ke] [e e] [e t] [ta]
```
增加元音到元音的直接过渡采样

---

## 2. 日语录音表

### 2.1 日语 CV 录音表

日语 CV 是最基础的录音表，覆盖所有清音、浊音、半浊音和拗音。

**基础 CV 列表（清音 + 元音）**:
```
a, i, u, e, o,
ka, ki, ku, ke, ko,
sa, shi, su, se, so,
ta, chi, tsu, te, to,
na, ni, nu, ne, no,
ha, hi, fu, he, ho,
ma, mi, mu, me, mo,
ya, yu, yo,
ra, ri, ru, re, ro,
wa, wo, n
```

**浊音**:
```
ga, gi, gu, ge, go,
za, ji, zu, ze, zo,
da, di, du, de, do,
ba, bi, bu, be, bo
```

**半浊音**:
```
pa, pi, pu, pe, po
```

**拗音**:
```
kya, kyu, kyo, gya, gyu, gyo,
sha, shu, sho, ja, ju, jo,
cha, chu, cho, nya, nyu, nyo,
hya, hyu, hyo, bya, byu, byo,
mya, myu, myo, pya, pyu, pyo,
rya, ryu, ryo
```

### 2.2 日语 VCV 录音表

VCV 录音表中，每个音节以元音开头，格式为 `[前元音][辅音][元音]`。

**基本格式**:
- あ行开头: `a ka`, `a ki`, `a ku`, `a ke`, `a ko`, `a sa`, ...
- い行开头: `i ka`, `i ki`, `i ku`, `i ke`, `i ko`, `i sa`, ...
- う行开头: `u ka`, `u ki`, ...
- え行开头: `e ka`, `e ki`, ...
- お行开头: `o ka`, `o ki`, ...

**特殊规则**:
- 词首（无前元音）: 使用 `-` 代替前元音，如 `- ka`, `- ki`
- 促音 `っ`: 录制为 `a Q`, `i Q`, `u Q`, `e Q`, `o Q`
- 拨音 `ん`: 录制为 `a n`, `i n`, `u n`, `e n`, `o n`
- 长音 `ー`: 使用元音延长标记，如 `a -`, `i -`

**完整 VCV 录音表示例片段**:
```
- あ, a ka, a ki, a ku, a ke, a ko,
a sa, a shi, a su, a se, a so,
a ta, a chi, a tsu, a te, a to,
a na, a ni, a nu, a ne, a no,
a ha, a hi, a fu, a he, a ho,
a ma, a mi, a mu, a me, a mo,
a ya, a yu, a yo,
a ra, a ri, a ru, a re, a ro,
a wa, a wo, a n, a Q,
- い, i ka, i ki, ... (同上结构)
```

### 2.3 日语 CVVC 录音表

CVVC 需要录制 CV + VC（或 VV）两种类型。

**CV 部分**: 同 2.1 日语 CV 录音表

**VC / VV 过渡部分**:
```
a k, a s, a sh, a t, a ch, a ts, a n, a h, a m, a y, a r, a w, a g, a z, a j, a d, a b, a p,
i k, i s, i sh, i t, i ch, i ts, i n, i h, i m, i y, i r, i w, i g, i z, i j, i d, i b, i p,
u k, u s, u sh, u t, u ch, u ts, u n, u h, u m, u y, u r, u w, u g, u z, u j, u d, u b, u p,
e k, e s, e sh, e t, e ch, e ts, e n, e h, e m, e y, e r, e w, e g, e z, e j, e d, e b, e p,
o k, o s, o sh, o t, o ch, o ts, o n, o h, o m, o y, o r, o w, o g, o z, o j, o d, o b, o p,
```

**VV 元音过渡（CVVX 用）**:
```
a a, a i, a u, a e, a o,
i a, i i, i u, i e, i o,
u a, u i, u u, u e, u o,
e a, e i, e u, e e, e o,
o a, o i, o u, o e, o o
```

---

## 3. 英语录音表

### 3.1 ARPAsing 录音表

ARPAsing 基于 ARPAbet 音素，使用单音素或双音素拼接。

**ARPAbet 音素集**:
```
AA, AE, AH, AO, AW, AY, EH, ER, EY, IH, IY, OW, OY, UH, UW,
B, CH, D, DH, F, G, HH, JH, K, L, M, N, NG, P, R, S, SH, T, TH, V, W, Y, Z, ZH
```

**ARPAsing 双音素（Diphone）录音表**:
```
- AA, AA B, AA D, AA F, AA G, AA K, AA L, AA M, AA N, AA P, AA R, AA S, AA T, AA V, AA W, AA Y, AA Z,
- AE, AE B, AE D, ...
(每个元音与所有辅音组合)
```

### 3.2 英语 VCCV 录音表

VCCV 适用于英语等多辅音语言，格式为 `[元音][辅音群][元音]`。

**示例**:
```
a b a, a b e, a b i, a b o, a b u,
a b r a, a b r e, a b r i, a b r o, a b r u,
a s t a, a s t e, a s t i, a s t o, a s t u,
a s k a, a s k e, ...
e b a, e b e, ...
```

### 3.3 英语 CCV 录音表

针对以辅音群开头的音节:
```
stra, stre, stri, stro, stru,
shra, shre, shri, shro, shru,
spla, spl e, ...
```

---

## 4. 中文录音表

### 4.1 中文 CVVC（普通话）

中文 UTAU 通常基于拼音，采用 CVVC 或 CV 结构。

**声母（Initials）CV**:
```
ba, bi, bu, bo,
pa, pi, pu, po,
ma, mi, mu, mo, me,
fa, fu, fo,
da, di, du, de,
ta, ti, tu, te,
na, ni, nu, ne, nv,
la, li, lu, le, lv,
ga, ge, gu,
ka, ke, ku,
ha, he, hu,
ji, ju, jie, jue,
qi, qu, qie, que,
xi, xu, xie, xue,
zhi, zha, zhe, zhu,
chi, cha, che, chu,
shi, sha, she, shu,
ri, re, ru,
zi, ze, zu,
ci, ce, cu,
si, se, su,
ya, ye, yi, yo, yu,
wa, wo, wu, wai, wei
```

**韵母 VC / VV 过渡**:
```
a b, a p, a m, a f, a d, a t, a n, a l, a g, a k, a h, a j, a q, a x, a zh, a ch, a sh, a r, a z, a c, a s, a y, a w,
o b, o p, ... (所有韵母 × 所有声母)
```

**特殊处理**:
- 儿化音: 韵母 + `r` 尾音，如 `ar`, `ir`, `ur`
- 零声母: 纯韵母采样，如 `a`, `o`, `e`, `ai`, `ei`, `ao`, `ou`, `an`, `en`, `ang`, `eng`

### 4.2 粤语 / 方言录音表

粤语需要覆盖九声六调，录音表基于粤拼:
```
baa, bai, baau, ban, bang, bat, bak,
paa, paai, paau, ...
(包含入声韵尾: -p, -t, -k, -m, -n, -ng)
```

---

## 5. 韩语录音表

### 5.1 韩语 CVVC

基于韩文字母（Hangul）发音:

**基本 CV（终声不包括）**:
```
ga, gya, geo, gyeo, go, gyo, gu, gyu, ge, gyae, gi,
na, nya, neo, nyeo, no, nyo, nu, nyu, ne, nyae, ni,
da, dya, deo, dyeo, do, dyo, du, dyu, de, dyae, di,
ra, rya, reo, ryeo, ro, ryo, ru, ryu, re, ryae, ri,
ma, mya, meo, myeo, mo, myo, mu, myu, me, myae, mi,
ba, bya, beo, byeo, bo, byo, bu, byu, be, byae, bi,
sa, sya, seo, syeo, so, syo, su, syu, se, syae, si,
a, ya, eo, yeo, o, yo, u, yu, ae, yae, i,
ja, jya, jeo, jyeo, jo, jyo, ju, jyu, je, jyae, ji,
cha, chya, cheo, chyeo, cho, chyo, chu, chyu, che, chyae, chi,
ka, kya, keo, kyeo, ko, kyo, ku, kyu, ke, kyae, ki,
ta, tya, teo, tyeo, to, tyo, tu, tyu, te, tyae, ti,
pa, pya, peo, pyeo, po, pyo, pu, pyu, pe, pyae, pi,
ha, hya, heo, hyeo, ho, hyo, hu, hyu, he, hyae, hi
```

**韵尾过渡（VC）**:
```
a g, a n, a d, a l, a m, a b, a s, a ng, a j, a ch, a k, a t, a p, a h,
... (每个元音 × 每个韵尾辅音)
```

---

## 6. 其他语言

### 6.1 西班牙语 CV

```
a, e, i, o, u,
ba, be, bi, bo, bu,
ca, ce, ci, co, cu,
da, de, di, do, du,
... (rr 需单独录制颤音)
```

### 6.2 俄语 CVC / CCV

俄语辅音群复杂，常用 CC-CV 结构:
```
stra, stre, stri, stro, stru,
zkra, zdra, ...
```

### 6.3 德语 / 法语录音表要点

- **德语**: 需覆盖小舌音 `r`, 元音变音 `ä`, `ö`, `ü`
- **法语**: 需覆盖鼻化元音，`on`, `an`, `in`, `un`

---

## 7. 录音表格式规范

### 7.1 标准格式

录音表通常为纯文本文件（`.txt`），每行一个采样名:
```
a
ka
sa
ta
...
```

### 7.2 带发音提示的录音表

部分录音表包含发音提示（假名/注音）:
```
a [あ]
ka [か]
sa [さ]
```

### 7.3 BPM 标记录音表（UTAU 辅助）

用于配合 UTAU 自动播放的录音表，包含 BPM 和间隔:
```
#BPM 120
#OFFSET 1.5
a
ka
sa
...
```

### 7.4 Reclist 生成原则

1. **穷尽性**: 覆盖目标语言所有必要音素组合
2. **最小化**: 去除可通过 oto 调整省略的冗余采样
3. **一致性**: 使用统一的命名规范（小写、无空格、标准罗马音）
4. **可扩展性**: 预留扩展位置（如呼吸音、呼气音、特效音）

---

## 参考链接

- UTAU Wiki 录音表指南：http://utau.wikidot.com/recording
- OpenUtau 音素器文档：https://github.com/stakira/OpenUtau/wiki/Phonemizer
- ARPAsing 项目：https://github.com/Arpasing/Arpasing
- 中文 UTAU 录音表参考：https://zh.wikipedia.org/wiki/UTAU
- 韩语 UTAU 录音表社区资源（搜索 "한국어 UTAU reclist"）

---

*本文档基于 UTAU 社区公开的录音表规范、各语言音系学特征及 OpenUtau 音素器实现整理。*
