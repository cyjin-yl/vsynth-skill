# VPR 跨语种歌唱指南（VOCALOID 5/6）

> 专门针对 VPR 格式（VOCALOID 5/6）的跨语种歌声合成指南
> 涵盖 V6 AI 轨道和传统轨道的音素处理差异

---

## 目录

1. [VPR 跨语种核心机制](#1-vpr-跨语种核心机制)
2. [isProtected 字段详解](#2-isprotected-字段详解)
3. [V6 音素格式规范](#3-v6-音素格式规范)
4. [拼音 → 日文 X-SAMPA 映射](#4-拼音--日文-x-sampa-映射)
5. [腭化音素处理](#5-腭化音素处理)
6. [ü 系列拼音的处理](#6-ü-系列拼音的处理)
7. [常见错误与排查](#7-常见错误与排查)
8. [CLI 工具使用](#8-cli-工具使用)

---

## 1. VPR 跨语种核心机制

### 1.1 VPR vs VSQX 的音素差异

| 特性 | VSQX (V3/V4) | VPR (V5/V6) |
|------|-------------|-------------|
| 音素字段 | XML `<p>` 节点 | JSON `phoneme` 字符串 |
| 音素分隔 | 空格 | 空格 |
| X-SAMPA 格式 | 标准 | 标准 + V6 腭化标记 `'` |
| 音素保护 | 无 | `isProtected` 字段（编辑器内歌词修改时生效） |
| AI 轨道支持 | 无 | 支持（`type: 2`） |

### 1.2 跨语种方向

**日语音库唱中文**（本指南主要场景）：
- `lyric`：中文拼音（如 `jie`、`kai`、`xiang`）
- `phoneme`：日文 X-SAMPA 近似音素（如 `dZ j e`、`k a j`、`S j a N`）
- `isProtected`：建议设为 `true`（防止在编辑器内改歌词时丢失自定义音素）
- `langID`：通常保持 `0`（日语）

### 1.3 V6 AI 轨道与传统轨道

V6 支持两种轨道类型：
- `type: 0` — 传统轨道（兼容 V3/V4/V5 声库，如 Luka V4X）
- `type: 2` — VOCALOID:AI 轨道（使用 AI 合成引擎，如 Miku V6）

**关键说明**：直接修改 JSON 的 `phoneme` 字段后，V6 加载时**会直接使用**该字段值，`isProtected` 不影响 JSON 层级的数据加载。`isProtected` 的作用是在编辑器 UI 内：当用户手动修改歌词时，决定是否根据新歌词自动更新音素。设为 `true` 可防止意外覆盖。

---

## 2. isProtected 字段详解

### 2.1 字段作用

```json
{
  "lyric": "jie",
  "phoneme": "dZ j e",
  "isProtected": true    // ← 编辑器内歌词修改时的音素保护
}
```

| isProtected 值 | 编辑器内行为 | 直接 JSON 修改 |
|---------------|-------------|---------------|
| `false`（默认） | 用户在编辑器内改歌词时，自动根据新歌词更新音素 | 不影响。JSON 中的 `phoneme` 直接加载 |
| `true` | 用户在编辑器内改歌词时，**保留**原有音素不自动更新 | 不影响。JSON 中的 `phoneme` 直接加载 |

### 2.2 为什么仍然建议设置 isProtected = true

虽然 `isProtected` 不影响直接 JSON 修改的加载结果，但建议设为 `true`：
- 防止用户在编辑器内调整歌词时，意外覆盖手动设置的跨语种音素
- 明确标记该音符的音素是手动指定的，非自动生成

### 2.3 真正导致"音素没更新"的原因 — 编辑器缓存

如果直接修改 JSON 后，在 V6 编辑器中看到的仍是旧音素，**根本原因通常是编辑器缓存**：

- V6 编辑器会对最近打开的文件进行缓存
- 删掉旧文件、放入同名新文件后重新打开，编辑器可能仍加载缓存中的旧版本
- **解决方法**：
  - 修改后使用**不同的文件名**（如 `song_fixed.vpr`）
  - 或确认编辑器完全关闭后再替换文件

> ⚠️ **之前大量 `[a]` 音素的真正原因**：原始 VPR 中的 `phoneme` 字段本身就是 `"a"`（日文歌词转拼音后没有正确映射音素），而非 `isProtected` 导致被覆盖。

---

## 3. V6 音素格式规范

### 3.1 JSON 中的 phoneme 字段

VPR 的 `phoneme` 字段使用**空格分隔的 X-SAMPA**，**不包含方括号**：

```json
// 正确
"phoneme": "d' i"
"phoneme": "tS M"
"phoneme": "S j a N"

// 错误（不要加方括号）
"phoneme": "[d' i]"   // ❌
"phoneme": "k,a,n"     // ❌ 不要用逗号
```

### 3.2 编辑器显示格式

V6 编辑器会在 UI 中自动加上方括号显示：
- JSON 中的 `"d' i"` → 编辑器显示 `[d' i]`
- JSON 中的 `"a"` → 编辑器显示 `[a]`
- JSON 中的 `"tS M"` → 编辑器显示 `[tS M]`

方括号只是**视觉装饰**，不影响实际解析。

### 3.3 日语音库合法音素

VOCALOID Japanese 声库支持的 X-SAMPA 符号：

**元音**：`a`, `i`, `M` (う), `e`, `o`

**辅音**：
- 清塞音：`k`, `s`, `tS`, `ts`, `t`, `p`, `p_h`, `p\\` (ふ)
- 浊塞音：`g`, `z`, `dz`, `dZ`, `d`, `b`
- 鼻音：`n`, `J` (に), `m`, `N` (んぐ), `N\\`
- 擦音：`S` (し), `h`, `C` (ひ), `s`, `4` (ら)
- 半元音：`j`, `w`
- 特殊：`?` (促音), `Q` (喉塞音)

**腭化标记**：`'` 附加在辅音后表示腭化变体
- `b'`, `d'`, `t'`, `m'`, `p'`, `g'`, `k'`, `4'`, `p\\'`

> ⚠️ `y` 不是日语音库的合法音素。中文的 `ü` 必须映射为 `M`（う）。

---

## 4. 拼音 → 日文 X-SAMPA 映射

### 4.1 核心映射原则

基于 [ChnToJpn.lua](../scripts/vpr_cross_language.py) 整理：

**声母映射**

| 拼音 | 日文 X-SAMPA | 说明 |
|------|-------------|------|
| b | `b` | ば行 |
| p | `p` | ぱ行 |
| m | `m` | ま行 |
| f | `p\\` | ふ（双唇摩擦音） |
| d | `d` | だ行 |
| t | `t` | た行 |
| n | `n` / `J` | `ni` 用 `J i`（硬腭鼻音） |
| l | `4` | ら行（闪音近似） |
| g | `g` | が行 |
| k | `k` | か行 |
| h | `h` | は行 |
| j | `dZ` | じ近似 |
| q | `tS` | ち近似 |
| x | `S` | し近似 |
| zh | `ts` | ざ行清音 |
| ch | `ts_h` | つ送气 |
| sh | `s` | さ行 |
| r | `4` | ら行 |
| z | `dz` | ざ行 |
| c | `ts` | つ |
| s | `s` | さ行 |

**韵母映射**

| 拼音 | 日文 X-SAMPA | 说明 |
|------|-------------|------|
| a | `a` | あ |
| o | `o` | お |
| e | `e` | え |
| i | `i` | い |
| u | `M` | う |
| ai | `a j` | あい |
| ei | `e j` | えい |
| ao | `a w` | あお |
| ou | `o w` | おう |
| an | `a n` | あん |
| en | `e n` | えん |
| in | `i n` | いん |
| un | `M n` | うん |
| ang | `a N` | あんぐ |
| eng | `o N` | おんぐ近似 |
| ing | `i N` | いんぐ |

### 4.2 整体认读音节

| 拼音 | 日文 X-SAMPA |
|------|-------------|
| zhi/chi | `tS i` |
| shi | `S i` |
| ri | `4 i` |
| zi | `dz i` |
| ci | `ts i` |
| si | `s i` |
| yi | `i` |
| wu | `M` |
| yu | `j M` |

### 4.3 ü 系列修正

| 拼音 | 常见错误 | 正确音素 | 说明 |
|------|---------|---------|------|
| yu | `M` | `j M` | V6 自动识别为 `j M` |
| yue | `M e` | `j e` | üe → j e |
| yuan | `M a n` | `j a n` | üan → j a n |
| yun | `M n` | `i n` | ün → i n |
| jue | `dZ M e` | `dZ j e` | üe 修正 |
| que | `tS M e` | `tS j e` | üe 修正 |
| quan | `tS M a n` | `tS j a n` | üan 修正 |

---

## 5. 腭化音素处理

### 5.1 腭化标记 `'` 的使用规则

在日语中，当辅音后接 `i` 元音时，V6 使用腭化辅音表示：

| 拼音 | 音素 | 说明 |
|------|------|------|
| bi | `b' i` | b + i 腭化 |
| pi | `p' i` | p + i 腭化 |
| mi | `m' i` | m + i 腭化 |
| di | `d' i` | d + i 腭化 |
| ti | `t' i` | t + i 腭化 |

### 5.2 ni 的特殊处理

拼音 `ni` 不使用 `n i`（会被识别为「な」+「い」），而是使用日语音素 `J i`（硬腭鼻音 + い）：

| 拼音 | 错误 | 正确 |
|------|------|------|
| ni | `n i` | `J i` |
| nian | `n j a n` | `J a n` |
| nin | `n i n` | `J i n` |
| ning | `n i N` | `J i N` |

### 5.3 iao 韵母中的腭化

拼音 `miao`、`diao`、`tiao` 等，声母腭化后介音 `j` 被吸收：

| 拼音 | 错误 | 正确 |
|------|------|------|
| miao | `m j a w` | `m' a w` |
| diao | `d j a w` | `d' a w` |

---

## 6. ü 系列拼音的处理

### 6.1 零声母 ü

中文 `yu`、`yue`、`yuan`、`yun` 的声母是隐含的 `y`（即 `j`），不是单纯的元音：

```json
// 正确
{"lyric": "yu",   "phoneme": "j M"}
{"lyric": "yue",  "phoneme": "j e"}
{"lyric": "yuan", "phoneme": "j a n"}
{"lyric": "yun",  "phoneme": "i n"}

// 错误
{"lyric": "yu",   "phoneme": "M"}     // 缺少声母 j
{"lyric": "yuan", "phoneme": "M a n"} // 缺少声母 j
```

### 6.2 j/q/x + ü

当声母为 `j`、`q`、`x` 时，拼音 `u` 实际上代表 `ü`：

| 拼音 | 实际发音 | 日语音素 |
|------|---------|---------|
| ju | j + ü | `dZ M` |
| qu | q + ü | `tS M` |
| xu | x + ü | `S M` |
| jue | j + üe | `dZ j e` |
| que | q + üe | `tS j e` |
| xue | x + üe | `S j e` |
| juan | j + üan | `dZ j a n` |
| quan | q + üan | `tS j a n` |
| xuan | x + üan | `S j a n` |

---

## 7. 常见错误与排查

### 7.1 症状 → 原因 → 修复

| 症状 | 原因 | 修复 |
|------|------|------|
| 大量 `[a]` 音素 | 原始 VPR 中 `phoneme` 本身就是 `"a"`（未正确映射） | 应用正确的拼音→音素映射 |
| `di` 显示为 `[d' i]`，其他拼音仍 `[a]` | 原始 VPR 中部分音素碰巧正确，部分未映射 | 应用完整映射表 |
| `yu` 不发音 | 音素写成 `M` 而非 `j M` | 修正为 `j M` |
| `ni` 听感不对 | 音素写成 `n i` 而非 `J i` | 修正为 `J i` |
| `wu` 听感不对 | 音素写成 `m M` 而非 `M` | 修正为 `M` |
| `wen` 听感不对 | 音素写成 `M n` 而非 `w e n` | 修正为 `w e n` |
| 修改 JSON 后编辑器仍显示旧音素 | **V6 编辑器缓存** | 使用不同文件名，或彻底关闭编辑器后重开 |
| AI 轨道和传统轨道都不跨语种 | `phoneme` 字段未正确映射 | 应用完整映射表 |
| 跨语种后某些字完全无声 | 使用了非法音素（如 `y`） | 替换为日语音素 |

### 7.2 排查流程

1. **确认映射完整性**：运行 `vpr_phoneme_inspect.py --find-a` 检查 `"a"` 比例
2. **应用映射**：运行 `vpr_cross_language.py --map ja --output mapped.vpr`
3. **使用不同文件名**：输出到**新文件名**，避免编辑器缓存
4. **验证**：在新文件中检查音素面板
5. **（可选）设置 isProtected**：若需在编辑器内修改歌词时保留音素，运行 `vpr_phoneme_lock.py --lock`

---

## 8. CLI 工具使用

### 8.1 诊断工具链

```bash
# 1. 诊断：查看音素分布和 "a" 的比例
python vpr_phoneme_inspect.py song.vpr

# 2. 映射：应用拼音→日语音素映射（输出到新文件名避免缓存）
python vpr_cross_language.py song.vpr --map ja --output song_mapped.vpr

# 3. （可选）锁定：设置 isProtected = true，防止编辑器内改歌词时丢失音素
python vpr_phoneme_lock.py song_mapped.vpr --lock --output song_locked.vpr

# 4. 验证：再次诊断确认修复
python vpr_phoneme_inspect.py song_mapped.vpr --find-a
```

### 8.2 分轨道处理

```bash
# 只处理轨道 0（如 Luka V4X 传统轨道）
python vpr_cross_language.py song.vpr --map ja --track 0 --output luka_fixed.vpr

# 只处理轨道 1（如 Miku V6 AI 轨道）
python vpr_cross_language.py song.vpr --map ja --track 1 --output miku_fixed.vpr

# 合并：先复制原文件，然后分别处理各轨道
```

### 8.3 自定义映射

```bash
# 导出内置映射表，作为自定义修改的起点
python vpr_cross_language.py --export-map mymap.json

# 编辑 mymap.json，添加/修改映射
# 然后应用自定义映射
python vpr_cross_language.py song.vpr --map-file mymap.json --output fixed.vpr
```

### 8.4 预览模式

```bash
# 预览映射结果，不写入文件
python vpr_cross_language.py song.vpr --map ja --protect --dry-run

# 预览锁定结果
python vpr_phoneme_lock.py song.vpr --lock --dry-run
```

---

*本文档基于 VOCALOID 6 实际文件格式分析、ChnToJpn.lua Job Plugin 音素映射和 V6 编辑器行为验证整理。*
