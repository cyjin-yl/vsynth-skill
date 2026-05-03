# INI/文本编辑规范

> 适用于 .ust (UTAU), .vsq 内部 INI 数据等 INI-like 格式

---

## 目录

1. [Section 语法](#1-section-语法)
2. [键值对格式](#2-键值对格式)
3. [编码问题](#3-编码问题)
4. [换行符](#4-换行符)
5. [常见错误](#5-常见错误)
6. [代码示例](#6-代码示例)

---

## 1. Section 语法

### UST Section 格式

UST 文件使用方括号包裹的 Section 名：

```ini
[#VERSION]
UST Version2.0

[#SETTING]
Tempo=120.00

[#0000]
Length=480
Lyric=do

[#TRACKEND]
```

### 标准 Section 名称

| Section | 说明 |
|---------|------|
| `[#VERSION]` | 版本声明 |
| `[#SETTING]` | 全局设置 |
| `[#PREV]` | 前一个音符（用于插件） |
| `[#0000]` ~ `[#NNNN]` | 音符段（按顺序编号） |
| `[#NEXT]` | 后一个音符（用于插件） |
| `[#TRACKEND]` | 音轨结束标记 |

### VSQ 内部 INI Section

VSQ 的 INI 数据使用类似但略有不同的格式：

```ini
[Common]
Version=DSB301
Name=Track1

[EventList]
0=ID#0000
768=ID#0001

[ID#0000]
Type=Singer
IconHandle=h#0000

[h#0000]
IconID=$00010001
IDS=Miku
```

---

## 2. 键值对格式

### 基本语法

```ini
Key=Value
```

### 特殊规则

| 规则 | 示例 | 说明 |
|------|------|------|
| 等号分隔 | `Tempo=120.00` | 键和值用 `=` 分隔 |
| 空值保留等号 | `Comment=` | 值为空时保留 `=` |
| 无引号 | `Lyric=hello` | 不支持 `"` 引号包裹 |
| 逗号分隔列表 | `PBW=80,100,120` | 列表使用 `,` 分隔 |
| 无嵌套 | - | INI 不支持嵌套结构 |

### UST 音符段字段

| 字段 | 格式示例 |
|------|---------|
| `Length` | `Length=480` |
| `Lyric` | `Lyric=ka` |
| `NoteNum` | `NoteNum=60` |
| `Intensity` | `Intensity=100` |
| `PBS` | `PBS=-45` 或 `PBS=-40;0` |
| `PBW` | `PBW=89,100,120` |
| `PBY` | `PBY=0,10,-5` |
| `PBM` | `PBM=s,j,r` |
| `Envelope` | `Envelope=0,5,35,0,100,100,0,%,0` |
| `VBR` | `VBR=65,160,35,20,20,0,0,0,0` |

---

## 3. 编码问题

### Shift-JIS 编码

> **警告**：经典 UTAU 使用 Shift-JIS 编码。错误的编码会导致 **Mojibake**（文字化け/乱码）。

| 软件 | 编码 |
|------|------|
| 经典 UTAU | Shift-JIS |
| UTAU-Synth | UTF-8 |
| OpenUtau (导入 UST) | 自动检测 |

### Python 编码处理

```python
import codecs

def read_ust_auto_encoding(filepath):
    """自动检测并读取 UST 文件"""
    encodings = ["utf-8", "shift_jis", "shift_jisx0213", "cp932"]
    
    for encoding in encodings:
        try:
            with open(filepath, "r", encoding=encoding) as f:
                content = f.read()
            print(f"Successfully decoded with {encoding}")
            return content, encoding
        except UnicodeDecodeError:
            continue
    
    raise ValueError(f"Could not decode {filepath} with any known encoding")

def convert_ust_encoding(input_path, output_path, input_encoding, output_encoding="utf-8"):
    """转换 UST 文件编码"""
    with open(input_path, "r", encoding=input_encoding) as f:
        content = f.read()
    
    with open(output_path, "w", encoding=output_encoding) as f:
        f.write(content)
```

### 检测编码的工具

```bash
# 使用 nkf (Unix/Linux)
nkf -g file.ust    # 检测编码
nkf -w file.ust > file_utf8.ust    # 转换为 UTF-8

# 使用 file 命令
file -i file.ust
```

---

## 4. 换行符

### CRLF vs LF

| 平台 | 换行符 | 表示 |
|------|--------|------|
| Windows | CRLF | `\r\n` |
| Unix/Linux/macOS | LF | `\n` |

### UST 换行符处理

- UTAU 通常接受两种格式，但插件可能敏感
- 建议保持 CRLF（Windows 传统）以最大化兼容性

### Python 换行符处理

```python
def normalize_line_endings(content, newline="\r\n"):
    """统一换行符"""
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    if newline != "\n":
        content = content.replace("\n", newline)
    return content

# 保存时指定换行符
with open("output.ust", "w", encoding="shift-jis", newline="\r\n") as f:
    f.write(content)
```

---

## 5. 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| 乱码 / Mojibake | 编码不匹配 | 转换为 Shift-JIS 或 UTF-8 |
| 插件无法读取 UST | 版本格式不匹配 | 确保使用插件支持的版本格式 |
| 音符解析错误 | Section 格式错误 | 检查 `[#XXXX]` 格式 |
| 包络线异常 | 值超出范围或格式错误 | 重置为默认包络 |
| 音源找不到 | `VoiceDir` 路径错误 | 检查路径格式，使用 `%VOICE%` 前缀 |
| 音高不生效 | Mode2=False | 设置 `Mode2=True` |
| 数值解析错误 | 数字含非 ASCII 字符 | 检查小数点是否为 `.` |

### VSQ INI 特定错误

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| DM 前缀数字溢出 | 超过 9999 段 | 编号变为 DM:00010000 |
| INI 拼接失败 | 段顺序错误 | 按 DM:NNNN 前缀数字排序 |
| Text Event 长度超限 | 单段超过 127 字节 | 分割为更小的段 |

---

## 6. 代码示例

### 完整 UST 解析器

```python
def parse_ust(filepath):
    """
    解析 UST 文件为结构化数据
    
    返回: {
        'version': str,
        'setting': dict,
        'notes': list[dict],
        'prev': dict or None,
        'next': dict or None
    }
    """
    # 自动检测编码
    content, encoding = read_ust_auto_encoding(filepath)
    lines = content.splitlines()
    
    result = {
        'version': {},
        'setting': {},
        'notes': [],
        'prev': None,
        'next': None,
        'encoding': encoding
    }
    
    current_section = None
    current_data = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 检测 Section
        if line.startswith("[#") and line.endswith("]"):
            section_name = line[2:-1]
            
            if section_name == "VERSION":
                current_section = "version"
                current_data = result['version']
            elif section_name == "SETTING":
                current_section = "setting"
                current_data = result['setting']
            elif section_name == "PREV":
                current_section = "prev"
                current_data = {}
                result['prev'] = current_data
            elif section_name == "NEXT":
                current_section = "next"
                current_data = {}
                result['next'] = current_data
            elif section_name == "TRACKEND":
                current_section = None
                current_data = None
            elif section_name.isdigit():
                current_section = "note"
                current_data = {}
                result['notes'].append(current_data)
            else:
                current_section = None
                current_data = None
        
        # 解析键值对
        elif current_data is not None and "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            
            # 类型转换
            if value == "":
                converted = ""
            elif value.lower() == "true":
                converted = True
            elif value.lower() == "false":
                converted = False
            else:
                try:
                    if "." in value:
                        converted = float(value)
                    else:
                        converted = int(value)
                except ValueError:
                    converted = value
            
            current_data[key] = converted
    
    return result


def write_ust(data, filepath, encoding="shift-jis"):
    """将结构化数据写回 UST 文件"""
    lines = []
    
    # VERSION
    if data.get('version'):
        lines.append("[#VERSION]")
        for key, value in data['version'].items():
            lines.append(f"{key}={value}")
    
    # SETTING
    if data.get('setting'):
        lines.append("[#SETTING]")
        for key, value in data['setting'].items():
            if isinstance(value, bool):
                value = "True" if value else "False"
            lines.append(f"{key}={value}")
    
    # PREV
    if data.get('prev'):
        lines.append("[#PREV]")
        for key, value in data['prev'].items():
            lines.append(f"{key}={value}")
    
    # NOTES
    for i, note in enumerate(data['notes']):
        lines.append(f"[#{i:04d}]")
        for key, value in note.items():
            if isinstance(value, bool):
                value = "True" if value else "False"
            elif isinstance(value, (list, tuple)):
                value = ",".join(str(v) for v in value)
            lines.append(f"{key}={value}")
    
    # NEXT
    if data.get('next'):
        lines.append("[#NEXT]")
        for key, value in data['next'].items():
            lines.append(f"{key}={value}")
    
    # TRACKEND
    lines.append("[#TRACKEND]")
    
    content = "\r\n".join(lines)
    with open(filepath, "w", encoding=encoding, newline="\r\n") as f:
        f.write(content)
```

### 修改 UST Mode2 音高参数

```python
def edit_mode2_pitch(note, pbs_start, pbw_list, pby_list, pbm_list=None):
    """
    修改 UST 音符的 Mode2 音高参数
    
    pbs_start: 音高弯折起点（毫秒）
    pbw_list: 控制点宽度列表（毫秒）
    pby_list: 控制点偏移列表（音分）
    pbm_list: 曲线类型列表（可选）
    """
    note['PBS'] = str(pbs_start)
    note['PBW'] = ",".join(str(w) for w in pbw_list)
    note['PBY'] = ",".join(str(y) for y in pby_list)
    if pbm_list:
        note['PBM'] = ",".join(pbm_list)
    
    return note

# 使用示例
data = parse_ust("input.ust")
for note in data['notes']:
    if note.get('Lyric') == 'ka':
        edit_mode2_pitch(note, -40, [80, 100], [0, 10], ['s', 'j'])

write_ust(data, "output.ust")
```

### 使用 utaupy 库

```python
import utaupy

# 加载 UST
ust = utaupy.ust.load("song.ust")

# 访问全局设置
print(f"Tempo: {ust.tempo}")

# 遍历音符
for note in ust.notes:
    print(f"Lyric: {note.lyric}, NoteNum: {note.notenum}, Length: {note.length}")
    
    # 修改属性
    note.intensity = 100
    note.modulation = 0
    
    # 修改 Mode2 音高
    if note.pbs is not None:
        note.pbs.start = -40
        note.pbw = [80, 100]
        note.pby = [0, 10]

# 保存
ust.write("song_modified.ust")
```

### VSQ INI 数据提取

```python
def extract_vsq_ini(vsq_filepath):
    """
    从 VSQ 文件中提取 INI 数据
    
    返回拼接后的完整 INI 字符串
    """
    import struct
    
    with open(vsq_filepath, "rb") as f:
        data = f.read()
    
    # 解析 MIDI 文件结构（简化版）
    # 实际实现需要使用 MIDI 解析库（如 mido）
    parts = []
    i = 0
    
    while i < len(data):
        # 查找 Text Meta Event (0xFF 0x01)
        if data[i:i+2] == b'\xFF\x01':
            length = data[i+2]
            text = data[i+3:i+3+length].decode("shift-jis", errors="ignore")
            if text.startswith("DM:"):
                # 提取 DM:NNNN: 前缀后的内容
                parts.append(text)
        i += 1
    
    # 按编号排序并拼接
    parts.sort(key=lambda x: x.split(":")[1])
    ini_content = ""
    for part in parts:
        # 去除 DM:NNNN: 前缀
        prefix_end = part.find(":", 3) + 1
        ini_content += part[prefix_end:]
    
    return ini_content
```

> **注意**：上述 VSQ 解析是简化示例。实际生产环境建议使用专业 MIDI 库（如 `mido`）解析 SMF 结构。

---

*本文档基于 INI 格式标准和 UTAU/VSQ 工程文件实际格式编写。*
