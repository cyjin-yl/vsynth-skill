# 扒谱与前处理工作流

> 从音频到歌声合成工程的完整前处理流程：去伴奏、音频转 MIDI、MIDI 转工程

---

## 目录

1. [工作流概览](#1-工作流概览)
2. [第一步：去伴奏 / 人声分离](#2-第一步-去伴奏--人声分离)
3. [第二步：音频转 MIDI](#3-第二步-音频转-midi)
4. [第三步：MIDI 导入歌声合成软件](#4-第三步-midi-导入歌声合成软件)
5. [第四步：歌词与音素调整](#5-第四步-歌词与音素调整)
6. [常见问题与优化](#6-常见问题与优化)

---

## 1. 工作流概览

```
原始音频 (MP3/WAV/FLAC)
    │
    ▼
[去伴奏 / 人声分离] ──→ UVR5-UI / Ultimate Vocal Remover
    │
    ▼
纯净人声 (Vocal Only)
    │
    ▼
[音频转 MIDI] ──→ GAME / SOME / Basic Pitch
    │
    ▼
MIDI 文件 (.mid)
    │
    ▼
[导入歌声合成软件] ──→ VOCALOID / UTAU / OpenUtau / Synthesizer V
    │
    ▼
工程文件 (.vsqx / .ustx / .svp / ...)
    │
    ▼
[调音与后期] ──→ 歌词、音素、音高、参数调整
```

---

## 2. 第一步：去伴奏 / 人声分离

### 2.1 推荐工具

| 工具 | 类型 | 特点 | 适用场景 |
|------|------|------|----------|
| **UVR5-UI** | GUI (Gradio) | 多模型支持、批量处理、跨平台 | 本地图形界面操作 |
| **UVR5-NO-UI** | CLI / Colab | 命令行、云端运行、免安装 | 服务器 / Google Colab |
| **Ultimate Vocal Remover** | GUI | 原版软件、模型最全 | Windows / Mac |

### 2.2 UVR5-UI 使用要点

**项目地址**: https://github.com/Eddycrack864/UVR5-UI

**支持的分离模型类别**:
- **VR Arch Models**: 传统声源分离模型
- **MDX-NET Models**: 基于深度学习的分离模型
- **Demucs v4 Models**: Meta 开源分离模型
- **MDX23C Models**: 最新一代 MDX 模型
- **Mel-Band Roformer / BS Roformer**: 基于 Transformer 的先进模型
- **VIP Models**: 付费增强模型（部分版本支持）

**推荐模型选择**:
```
去伴奏留人声: 使用 "MDX23C" 或 "Mel-Band Roformer"
高质量人声: 选择 "2 stems (Vocals + Instrumental)" 输出
批量处理: 开启 "Batch Separation" 处理整个文件夹
```

**命令行快速使用 (UVR5-NO-UI)**:
```bash
# Colab / 云端环境
!git clone https://github.com/Eddycrack864/UVR5-NO-UI.git
# 按 notebook 步骤运行，选择输入音频路径和输出路径
```

### 2.3 分离后检查

- **残留伴奏**: 如果高频仍有吉他/钢琴残留，尝试叠加使用不同模型二次分离
- **人声损伤**: 过度分离可能导致人声高频损失，可在 DAW 中用 EQ 补偿
- **混响处理**: 分离后人声通常带房间混响，如需更干声，选择带 "De-Reverb" 功能的模型

---

## 3. 第二步：音频转 MIDI

### 3.1 推荐工具对比

| 工具 | 项目地址 | 速度 | 精度 | 特点 |
|------|---------|------|------|------|
| **GAME** | openvpi/GAME | 中等 | 高 | 支持边界自适应、多语言、可训练 |
| **SOME** | openvpi/SOME | 快 | 高 | 支持浮点音高、DiffSinger 数据集兼容 |
| **Basic Pitch** | spotify/basic-pitch | 快 | 中 | Spotify 开源、通用乐器 |
| **Melodyne** | 商业软件 | - | 极高 | 行业标准、可手动精调 |

### 3.2 GAME (Generative Adaptive MIDI Extractor)

**项目地址**: https://github.com/openvpi/GAME

**GAME 是 SOME 的升级版**，核心优势：
1. **生成式边界提取**: 使用 D3PM (离散扩散模型) 权衡质量与速度
2. **自适应架构**: 音符和音高可对齐到已知边界
3. **鲁棒性**: 支持含噪声、混响甚至带伴奏的脏音频
4. **多语言**: 选择正确语言可提升分割效果
5. **可调节阈值**: 边界和音符存在性阈值可调

**安装要求**:
- Python 3.12, PyTorch 2.8.0, CUDA 12.9, Lightning 2.6.1
- 下载预训练模型（从 Releases 或 Discussions）

**推理命令**:
```bash
# 单文件转 MIDI
python infer.py extract audio.wav -m model.pt --output-formats mid,txt,csv

# 批量处理目录
python infer.py extract /path/to/audio/dir/ -m model.pt --glob *.wav --output-formats mid,txt,csv

# DiffSinger 数据集对齐（含音素边界）
python infer.py align transcriptions.csv -m model.pt --save-path output.csv
```

**输出格式说明**:
- `.mid`: 标准 MIDI 文件，可直接导入 DAW / 歌声合成软件
- `.txt`: 文本格式的音符序列
- `.csv`: 含详细时间信息的表格数据

### 3.3 SOME (Singing-Oriented MIDI Extractor)

**项目地址**: https://github.com/openvpi/SOME

**SOME 特点**:
- **速度**: CPU 上 9x 实时，GPU 上 300x 实时
- **低资源依赖**: 仅需 3 小时训练数据即可定制
- **浮点音高**: 输出非整数 MIDI 值（支持人类化微调）
- **RMVPE 音高提取**: 搭配 RMVPE 模型效果更佳

**推理命令**:
```bash
# CLI 推理
python infer.py --model model.pt --wav audio.wav

# Web UI
python webui.py --work_dir ./models

# DiffSinger 批量处理
python batch_infer.py --model model.pt --dataset ./dataset --overwrite
```

### 3.4 音频转 MIDI 的注意事项

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 音符切分过碎 | 颤音/转音被识别为多个音符 | 在歌声合成软件中合并音符 |
| 音高偏移 | 歌手跑调或转音 | 使用软件的音高吸附功能 |
| 节拍错位 | 自由节奏或 Rubato | 手动调整音符位置对齐拍号 |
| 缺失歌词 | MIDI 不含歌词信息 | 后续手动输入或导入文本 |
| 速度变化丢失 | MIDI 单速度轨 | 检查原始 BPM 变化，手动添加 |

---

## 4. 第三步：MIDI 导入歌声合成软件

### 4.1 VOCALOID 导入

**支持格式**: 标准 MIDI (.mid / .smf)

**导入路径**: File → Import → MIDI File

**VOCALOID 6 特有选项**:
- **歌词编码**: 可选择 Shift-JIS 或 UTF-8
- **音轨选择**: 可导入指定 MIDI Track
- **速度/拍号**: 自动识别 MIDI 中的 Tempo Meta Event

**导入后处理**:
```
1. 检查 preMeasure 是否包含前置空白小节
2. 检查 resolution 是否与 MIDI 一致（通常为 480）
3. 合并过短的碎音符（GAME 可能输出颤音碎片）
4. 调整音符力度 (Velocity) 到合理范围 (64-100)
```

### 4.2 OpenUtau 导入

**支持格式**: MIDI (.mid) + 直接歌词粘贴

**导入路径**: File → Import → MIDI / VSQX / UST

**OpenUtau 特有功能**:
- **音素器自动匹配**: 导入后选择正确的 Phonemizer (`JA CVVC` / `EN ARPAsing` / `ZH CVVC`)
- **多轨支持**: MIDI 多 Track 自动映射为 USTX 多轨

### 4.3 Synthesizer V 导入

**支持格式**: MIDI (.mid)

**导入路径**: File → Import → MIDI

**SV 注意事项**:
- MIDI 时间单位自动转换为 blick (1 blick = 1/1470000 beat)
- 歌词需手动输入或使用 `歌词批量粘贴` 功能
- 导入后建议清理 `pitchDelta` 参数，重新绘制音高曲线

---

## 5. 第四步：歌词与音素调整

### 5.1 歌词批量输入

**VOCALOID**:
- 使用 `Job Plugin` → `Lyric Entry` 批量输入
- 或使用外部工具编辑 VSQX XML 的 `<y>` 节点

**OpenUtau**:
- 选中所有音符 → 右键 `Edit Lyrics` → 批量粘贴
- 歌词格式: 每行一个音符歌词

**Synthesizer V**:
- 选中音符 → `Note Properties` → Lyrics 栏
- 或使用 `Script` → `Batch Lyrics Input`

### 5.2 音素微调

导入 MIDI 后，音素通常由软件自动分配。如需调整：
- **VOCALOID**: 双击音符 → Phoneme Editor → 修改 X-SAMPA
- **OpenUtau**: `phoneme_overrides` 或切换 Phonemizer
- **Synthesizer V**: Phoneme Timing 面板手动调整

详见 [xsampa.md](xsampa.md) 和 [phoneme_splitting.md](phoneme_splitting.md)。

---

## 6. 常见问题与优化

### 6.1 去伴奏后音频质量差

**原因**: 原始音频码率低、压缩严重、或伴奏与人声音域重叠
**解决**:
1. 使用更高质量的原始音源（FLAC / WAV > 320kbps MP3）
2. 尝试不同分离模型组合（先用 Demucs 再用 MDX23C）
3. 对极端情况，手动在 DAW 中切除伴奏频段

### 6.2 转 MIDI 后音符过于密集

**原因**: 歌手使用了大量装饰音、颤音或转音
**解决**:
1. 在导入歌声合成软件后，合并 1/32 或更短的碎音符
2. 删除明显的颤音碎片（保留主干音符）
3. 使用歌声合成软件的量化功能（Snap to Grid）

### 6.3 转 MIDI 后拍号/速度不对

**原因**: 原曲使用了变速 (Tempo Change) 或 Rubato
**解决**:
1. 在 DAW 中先对齐节拍，再导出 MIDI
2. 或导入后在歌声合成软件中手动调整 tempo 节点
3. VOCALOID: `<masterTrack>` 中添加多个 `<tempo>` 节点
4. OpenUtau: `tempos` 列表中添加多个 BPM 变化点

### 6.4 歌词与音符不同步

**原因**: MIDI 只含音符信息，不含歌词时间戳
**解决**:
1. 使用 `LRC` / `SRT` 歌词文件辅助对齐
2. 或使用 `aegisub` 等字幕软件打轴后导入
3. 手动逐句对齐（最精确但耗时）

---

## 参考链接

- **UVR5-UI**: https://github.com/Eddycrack864/UVR5-UI
- **UVR5-NO-UI**: https://github.com/Eddycrack864/UVR5-NO-UI
- **GAME**: https://github.com/openvpi/GAME
- **SOME**: https://github.com/openvpi/SOME
- **Basic Pitch**: https://github.com/spotify/basic-pitch
- **OpenVPI 社区**: https://github.com/openvpi

---

*本文档基于 OpenVPI 社区项目文档、UVR5 官方资料及歌声合成社区实践整理。*
