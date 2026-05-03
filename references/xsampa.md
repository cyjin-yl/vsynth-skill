# X-SAMPA 音素参考

> 歌声合成领域（VOCALOID、Synthesizer V、DiffSinger 等）使用的 X-SAMPA 音标系统参考

---

## 目录

1. [什么是 X-SAMPA](#1-什么是-x-sampa)
2. [日语 X-SAMPA 映射](#2-日语-x-sampa-映射)
3. [英语 X-SAMPA 映射](#3-英语-x-sampa-映射)
4. [跨引擎 X-SAMPA 差异](#4-跨引擎-x-sampa-差异)
5. [VOCALOID 音素编辑实践](#5-vocaloid-音素编辑实践)
6. [音素表速查](#6-音素表速查)

---

## 1. 什么是 X-SAMPA

**X-SAMPA** (Extended Speech Assessment Methods Phonetic Alphabet) 是 SAMPA 的扩展版本，用 ASCII 字符表示 IPA (国际音标) 符号。

**在歌声合成中的用途**:
- VOCALOID：`.vsqx` 的 `<p>` 节点存储音素（空格分隔）
- Synthesizer V：`.svp` 的 `phonemes` 字段
- DiffSinger：`ph_seq` 字段
- OpenUtau：音素覆盖时作为中间表示

**与 IPA 的关系**:
```
IPA:  [k a]  →  X-SAMPA: k a
IPA:  [tɕ i] →  X-SAMPA: tS i
IPA:  [ɸ ɯ]  →  X-SAMPA: p\ u
```

---

## 2. 日语 X-SAMPA 映射

### 2.1 清音 (清音・せいおん)

| 假名 | 罗马音 | X-SAMPA | 说明 |
|------|--------|---------|------|
| あ   | a      | `a`     | 开前不圆唇元音 |
| い   | i      | `i`     | 闭前不圆唇元音 |
| う   | u      | `M`     | 闭后圆唇元音（实际为不圆唇 [ɯ]） |
| え   | e      | `e`     | 半闭前不圆唇元音 |
| お   | o      | `o`     | 半闭后圆唇元音 |
| か   | ka     | `k a`   | 软腭塞音 + a |
| き   | ki     | `k i`   | |
| く   | ku     | `k M`   | |
| け   | ke     | `k e`   | |
| こ   | ko     | `k o`   | |
| さ   | sa     | `s a`   | 齿龈摩擦音 |
| し   | shi    | `S i`   | 龈后摩擦音 [ɕ] |
| す   | su     | `s M`   | |
| せ   | se     | `s e`   | |
| そ   | so     | `s o`   | |
| た   | ta     | `t a`   | 齿龈塞音 |
| ち   | chi    | `tS i`  | 龈后塞擦音 [tɕ] |
| つ   | tsu    | `ts M`  | 齿龈塞擦音 [tsɯ] |
| て   | te     | `t e`   | |
| と   | to     | `t o`   | |
| な   | na     | `n a`   | 齿龈鼻音 |
| に   | ni     | `J i`   | 龈后鼻音 [ɲ] |
| ぬ   | nu     | `n M`   | |
| ね   | ne     | `n e`   | |
| の   | no     | `n o`   | |
| は   | ha     | `h a`   | 声门摩擦音 |
| ひ   | hi     | `C i`   | 龈后摩擦音 [ç] |
| ふ   | fu     | `p\ M`  | 双唇摩擦音 [ɸ] |
| へ   | he     | `h e`   | |
| ほ   | ho     | `h o`   | |
| ま   | ma     | `m a`   | 双唇鼻音 |
| み   | mi     | `m i`   | |
| む   | mu     | `m M`   | |
| め   | me     | `m e`   | |
| も   | mo     | `m o`   | |
| や   | ya     | `j a`   | 硬腭近音 |
| ゆ   | yu     | `j M`   | |
| よ   | yo     | `j o`   | |
| ら   | ra     | `4 a`   | 齿龈闪音 [ɾ] |
| り   | ri     | `4 i`   | |
| る   | ru     | `4 M`   | |
| れ   | re     | `4 e`   | |
| ろ   | ro     | `4 o`   | |
| わ   | wa     | `w a`   | 圆唇软腭近音 |
| を   | wo     | `w o`   | |

### 2.2 浊音 (濁音・だくおん)

| 假名 | 罗马音 | X-SAMPA |
|------|--------|---------|
| が   | ga     | `g a`   |
| ぎ   | gi     | `g i`   |
| ぐ   | gu     | `g u`   |
| げ   | ge     | `g e`   |
| ご   | go     | `g o`   |
| ざ   | za     | `dz a`  |
| じ   | ji     | `dZ i`  |
| ず   | zu     | `dz u`  |
| ぜ   | ze     | `dz e`  |
| ぞ   | zo     | `dz o`  |
| だ   | da     | `d a`   |
| ぢ   | di     | `d i`   |
| づ   | du     | `d u`   |
| で   | de     | `d e`   |
| ど   | do     | `d o`   |
| ば   | ba     | `b a`   |
| び   | bi     | `b i`   |
| ぶ   | bu     | `b u`   |
| べ   | be     | `b e`   |
| ぼ   | bo     | `b o`   |
| ぱ   | pa     | `p a`   |
| ぴ   | pi     | `p i`   |
| ぷ   | pu     | `p u`   |
| ぺ   | pe     | `p e`   |
| ぽ   | po     | `p o`   |

### 2.3 特殊音素

| 假名 | X-SAMPA | 说明 |
|------|---------|------|
| ん   | `n` `N` `J` `m` `N\` | 拨音，上下文相关 |
| っ   | `Q` | 促音（无声除阻） |
| ー   | （元音延长，无独立音素）| |
| きゃ | `k j a` | 拗音 |
| しゃ | `S j a` | |
| ちゃ | `tS j a` | |
| にゃ | `J j a` | |
| ひゃ | `C j a` | |
| みゃ | `m j a` | |
| りゃ | `4 j a` | |
| ぎゃ | `g j a` | |
| じゃ | `dZ j a` | |
| びゃ | `b j a` | |
| ぴゃ | `p j a` | |

---

## 3. 英语 X-SAMPA 映射

### 3.1 元音

| 符号 | 示例词 | IPA | 说明 |
|------|--------|-----|------|
| `i`  | see    | [iː] | 闭前不圆唇长元音 |
| `I`  | sit    | [ɪ]  | 次闭前不圆唇 |
| `e`  | bed    | [e]  | 半闭前不圆唇 |
| `{`  | cat    | [æ]  | 近开前不圆唇 |
| `a`  | father | [ɑː] | 开后不圆唇 |
| `A`  | cut    | [ʌ]  | 开后不圆唇（短） |
| `O`  | bought | [ɔː] | 半开后圆唇 |
| `o`  | boat   | [oʊ] | 双元音 |
| `U`  | put    | [ʊ]  | 次闭后圆唇 |
| `u`  | food   | [uː] | 闭后圆唇长元音 |
| `@`  | about  | [ə]  | 中央元音 |
| `3`  | bird   | [ɜː] | 中央长元音 |
| `V`  | run    | [ʌ]  | 开后不圆唇（另一种表示） |
| `E`  | bet    | [ɛ]  | 半开前不圆唇 |
| `Q`  | hot    | [ɒ]  | 开后圆唇 |

### 3.2 辅音

| 符号 | 示例词 | IPA | 说明 |
|------|--------|-----|------|
| `p`  | pen    | [p]  | 双唇清塞音 |
| `b`  | bed    | [b]  | 双唇浊塞音 |
| `t`  | ten    | [t]  | 齿龈清塞音 |
| `d`  | dog    | [d]  | 齿龈浊塞音 |
| `k`  | cat    | [k]  | 软腭清塞音 |
| `g`  | go     | [g]  | 软腭浊塞音 |
| `f`  | fine   | [f]  | 唇齿清擦音 |
| `v`  | voice  | [v]  | 唇齿浊擦音 |
| `T`  | thin   | [θ]  | 齿间清擦音 |
| `D`  | then   | [ð]  | 齿间浊擦音 |
| `s`  | see    | [s]  | 齿龈清擦音 |
| `z`  | zoo    | [z]  | 齿龈浊擦音 |
| `S`  | she    | [ʃ]  | 龈后清擦音 |
| `Z`  | measure| [ʒ]  | 龈后浊擦音 |
| `tS` | chair  | [tʃ] | 龈后清塞擦音 |
| `dZ` | jump   | [dʒ] | 龈后浊塞擦音 |
| `h`  | hat    | [h]  | 声门清擦音 |
| `m`  | man    | [m]  | 双唇鼻音 |
| `n`  | no     | [n]  | 齿龈鼻音 |
| `N`  | sing   | [ŋ]  | 软腭鼻音 |
| `l`  | leg    | [l]  | 齿龈边音 |
| `r`  | red    | [r]  | 齿龈近音 [ɹ] |
| `j`  | yes    | [j]  | 硬腭近音 |
| `w`  | we     | [w]  | 圆唇软腭近音 |

---

## 4. 跨引擎 X-SAMPA 差异

### VOCALOID vs Synthesizer V vs DiffSinger

| 场景 | VOCALOID | Synthesizer V | DiffSinger |
|------|----------|---------------|------------|
| 日语 ん | `n` / `N` / `m` / `J` | `N` | `N` |
| 日语 っ | `Q` | `cl` | `cl` |
| 日语 し | `S i` | `sh` i` | `sh` i` |
| 英语 th | `T` / `D` | `th` | `th` |
| 空格分隔 | 是 | 是 | 是 |
| 双元音 | `aI`, `aU`, `oI` | `ay`, `aw`, `oy` | `ay`, `aw`, `oy` |

> **注意**: 不同引擎的英语音素集差异较大。VOCALOID 使用标准 X-SAMPA；SV 和 DiffSinger 使用简化标记。

---

## 5. VOCALOID 音素编辑实践

### 5.1 VSQX 音素节点

```xml
<note>
  <t>7680</t>
  <dur>480</dur>
  <n>60</n>
  <v>64</v>
  <y>test</y>
  <p>k a t</p>    <!-- X-SAMPA，空格分隔 -->
</note>
```

### 5.2 音素覆盖规则

1. **歌词与音素分离**: `<y>` 存储显示歌词，`<p>` 存储实际发音音素
2. **空格分隔**: 每个音素之间必须有空格
3. **大小写敏感**: `S` ≠ `s`，`N` ≠ `n`
4. **特殊音素**: `N\` (软腭鼻音), `J` (龈后鼻音), `4` (闪音)

### 5.3 常见音素编辑场景

| 目的 | 原始 | 修改后 | 效果 |
|------|------|--------|------|
| 日语拨音细化 | `n` | `N` | 后接软腭音时用软腭鼻音 |
| 英语 th 纠正 | `t` | `T` | 将 /t/ 改为 /θ/ |
| 删除辅音 | `k a` | `a` | 省略无声除阻 |
| 添加喉塞音 | `a` | `Q a` | 声门爆破开头 |

---

## 6. 音素表速查

### 6.1 X-SAMPA 元音表

```
        前 --------- 央 --------- 后
高      i · y        1 · }        u · M
次高    I · Y                        U
半高    e · 2        @ · 8        7 · o
中      E            3              O
半低    {            6              V · Q
次低                        5
低      a · &        A              A · Q
```

### 6.2 X-SAMPA 辅音修饰符

| 修饰符 | 含义 | 示例 |
|--------|------|------|
| `\`  | 成音节 | `n\` = [n̩] |
| `'`  | 主重音 | `"` 次重音 |
| `:`  | 长音 | `a:` = [aː] |
| `_h` | 送气 | `t_h` = [tʰ] |
| `_o` | 圆唇化 | `s_o` = [sʷ] |
| `~`  | 鼻化 | `a~` = [ã] |

### 6.3 日语速查表（罗马音 → X-SAMPA）

```python
ROMAJI_TO_XSAMPA = {
    'a': 'a', 'i': 'i', 'u': 'u', 'e': 'e', 'o': 'o',
    'ka': 'k a', 'ki': 'k i', 'ku': 'k u', 'ke': 'k e', 'ko': 'k o',
    'sa': 's a', 'shi': 'S i', 'su': 's u', 'se': 's e', 'so': 's o',
    'ta': 't a', 'chi': 'tS i', 'tsu': 'ts u', 'te': 't e', 'to': 't o',
    'na': 'n a', 'ni': 'J i', 'nu': 'n u', 'ne': 'n e', 'no': 'n o',
    'ha': 'h a', 'hi': 'C i', 'fu': 'p\\ u', 'he': 'h e', 'ho': 'h o',
    'ma': 'm a', 'mi': 'm i', 'mu': 'm u', 'me': 'm e', 'mo': 'm o',
    'ya': 'j a', 'yu': 'j u', 'yo': 'j o',
    'ra': '4 a', 'ri': '4 i', 'ru': '4 u', 're': '4 e', 'ro': '4 o',
    'wa': 'w a', 'wo': 'w o', 'n': 'n',
    'ga': 'g a', 'gi': 'g i', 'gu': 'g u', 'ge': 'g e', 'go': 'g o',
    'za': 'dz a', 'ji': 'dZ i', 'zu': 'dz u', 'ze': 'dz e', 'zo': 'dz o',
    'da': 'd a', 'di': 'd i', 'du': 'd u', 'de': 'd e', 'do': 'd o',
    'ba': 'b a', 'bi': 'b i', 'bu': 'b u', 'be': 'b e', 'bo': 'b o',
    'pa': 'p a', 'pi': 'p i', 'pu': 'p u', 'pe': 'p e', 'po': 'p o',
    'kya': 'k j a', 'kyu': 'k j u', 'kyo': 'k j o',
    'sha': 'S j a', 'shu': 'S j u', 'sho': 'S j o',
    'cha': 'tS j a', 'chu': 'tS j u', 'cho': 'tS j o',
    'nya': 'J j a', 'nyu': 'J j u', 'nyo': 'J j o',
    'hya': 'C j a', 'hyu': 'C j u', 'hyo': 'C j o',
    'mya': 'm j a', 'myu': 'm j u', 'myo': 'm j o',
    'rya': '4 j a', 'ryu': '4 j u', 'ryo': '4 j o',
    'gya': 'g j a', 'gyu': 'g j u', 'gyo': 'g j o',
    'ja': 'dZ j a', 'ju': 'dZ j u', 'jo': 'dZ j o',
    'bya': 'b j a', 'byu': 'b j u', 'byo': 'b j o',
    'pya': 'p j a', 'pyu': 'p j u', 'pyo': 'p j o',
}
```

---

## 参考链接

- X-SAMPA 完整规范：https://www.phon.ucl.ac.uk/home/sampa/
- IPA 图表：https://www.internationalphoneticassociation.org/content/ipa-chart
- VOCALOID 音素编辑 Wiki：https://vocaloid.fandom.com/wiki/Phoneme
- VOCALOID Phoneme List (官方)：https://vocaloid.fandom.com/wiki/Phoneme_List
- Synthesizer V 音素参考：https://svdocs.dreamtonics.com/en/synthv/phoneme
- 跨语种歌唱参考：[cross_language.md](cross_language.md) — 中文↔日文跨语种音素映射与和声处理

---

*本文档基于 IPA、X-SAMPA 标准和各歌声合成引擎官方文档整理。*
