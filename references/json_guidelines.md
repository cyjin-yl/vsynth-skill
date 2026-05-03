# JSON 编辑规范

> 适用于 .svp (Synthesizer V), .s5p (Synthesizer V Editor), .ds (DiffSinger), .vpr 内部 JSON 等

---

## 目录

1. [字符串转义](#1-字符串转义)
2. [数值精度](#2-数值精度)
3. [Unicode 处理](#3-unicode-处理)
4. [嵌套层级](#4-嵌套层级)
5. [NaN 值处理](#5-nan-值处理)
6. [常见错误](#6-常见错误)
7. [代码示例](#7-代码示例)

---

## 1. 字符串转义

### JSON 字符串转义规则

| 字符 | 转义序列 | 说明 |
|------|---------|------|
| `"` | `\"` | 双引号 |
| `\` | `\\` | 反斜杠 |
| `/` | `\/` | 斜杠（可选） |
| `\b` | `\b` | 退格 |
| `\f` | `\f` | 换页 |
| `\n` | `\n` | 换行 |
| `\r` | `\r` | 回车 |
| `\t` | `\t` | 制表符 |
| Unicode | `\uXXXX` | Unicode 字符 |

### 歌词中的转义

```json
{
  "lyrics": "Line 1\nLine 2",
  "phonemes": "hh ah \"test\""
}
```

### Python 自动处理

```python
import json

# Python 的 json 模块自动处理转义
data = {"lyrics": "R&B \"test\""}
json_str = json.dumps(data, ensure_ascii=False)
# 结果: {"lyrics": "R&B \"test\""}
```

---

## 2. 数值精度

### 浮点数精度问题

JSON 中浮点数的精度有限，歌声合成工程文件中的参数值需要特别注意：

```json
{
  "detune": 15.5,
  "beatPerMinute": 128.456789
}
```

### 建议

- 保留足够的小数位（通常 2-4 位足够）
- 避免舍入误差累积
- 使用 `round(value, 4)` 控制精度

### Python 数值处理

```python
import json

# 控制浮点数精度
json.dumps({"value": 15.567891234}, ensure_ascii=False)
# 默认保留原始精度

# 自定义 JSON 编码器以控制精度
class PrecisionEncoder(json.JSONEncoder):
    def encode(self, obj):
        if isinstance(obj, dict):
            items = []
            for k, v in obj.items():
                if isinstance(v, float):
                    items.append(f'"{k}": {round(v, 4)}')
                else:
                    items.append(f'"{k}": {super().encode(v)}')
            return "{" + ", ".join(items) + "}"
        return super().encode(obj)
```

---

## 3. Unicode 处理

### JSON Unicode 编码

```python
import json

# ensure_ascii=False: 保留 Unicode 字符（推荐）
data = {"lyrics": "あいうえお"}
json_str = json.dumps(data, ensure_ascii=False)
# 结果: {"lyrics": "あいうえお"}

# ensure_ascii=True: 转义为非 ASCII（不推荐，可读性差）
json_str = json.dumps(data, ensure_ascii=True)
# 结果: {"lyrics": "\u3042\u3044\u3046\u3048\u304a"}
```

### 各格式编码要求

| 格式 | 编码 | ensure_ascii 设置 |
|------|------|------------------|
| .svp | UTF-8 | `False` |
| .s5p | UTF-8 | `False` |
| .ds | UTF-8 | `False` |
| .vpr (内) | UTF-8 | `False` |

> **建议**：始终使用 `ensure_ascii=False` 保存歌声合成工程文件，以保持可读性和正确性。

---

## 4. 嵌套层级

### SVP 嵌套结构

```
Project (顶层)
├── timeAxis
│   ├── tempo[]
│   └── measure[]
├── tracks[]
│   └── Track
│       ├── dbDefaults
│       └── groups[] (NoteGroupReference)
├── library[] (NoteGroup)
│   ├── notes[] (Note)
│   │   └── attributes
│   └── parameters
│       ├── pitchDelta
│       │   └── points[]
│       ├── vibratoEnv
│       └── ...
├── renderConfig
└── settings
```

### 编辑注意事项

- 修改 `library` 中的 NoteGroup 时，确保 `tracks` 中的引用仍然有效
- UUID 引用必须在 library 中存在
- 参数曲线在 NoteGroup 级别定义，不在轨道级别

---

## 5. NaN 值处理

### Synthesizer V 中的 NaN

Synthesizer V 的 JSON 文件中可能出现 JavaScript 风格的 `NaN` 值：

```json
{
  "attributes": {
    "tF0Offset": NaN,
    "dF0Vbr": 1.0
  }
}
```

> **警告**：标准 JSON 解析器不支持 `NaN`！Python 的 `json.load()` 会抛出 `JSONDecodeError`。

### 处理方案

```python
import math
import re

def parse_sv_json(filepath):
    """解析可能包含 NaN 的 Synthesizer V JSON 文件"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 将 NaN 替换为 null
    content = re.sub(r'(?<!"\w)NaN(?!\w")', 'null', content)
    # 注意：此正则可能不够精确，需根据实际文件调整
    
    return json.loads(content)

# 或者使用自定义解码器
import json

class NaNEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, float) and math.isnan(obj):
            return "NaN"
        return super().default(obj)

# 写入时
json.dump(data, f, cls=NaNEncoder)
```

> **建议**：编辑 SVP 文件时，遇到 `NaN` 值应保留其语义含义（表示"使用默认值"），不要随意改为 0 或其他数值。

---

## 6. 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| `JSONDecodeError` | 文件包含 NaN 或非标准 JSON | 预处理 NaN，或使用允许 NaN 的解析器 |
| 中文乱码 | 使用了 `ensure_ascii=True` | 使用 `ensure_ascii=False` |
| 尾随逗号错误 | JSON 不允许尾随逗号 | 移除最后一个元素后的逗号 |
| 键未加引号 | 使用了 Python dict 而非 JSON | 使用 `json.dumps()` 转换 |
| 注释导致解析失败 | JSON 标准不支持注释 | 移除所有 `//` 和 `/* */` 注释 |
| 单引号 | JSON 字符串必须使用双引号 | 将单引号替换为双引号 |
| 数字精度丢失 | 浮点数舍入 | 使用 `Decimal` 类型或字符串存储 |

### 验证 JSON 格式

```python
import json

def validate_json(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        print("JSON is valid")
        return True
    except json.JSONDecodeError as e:
        print(f"JSON error at line {e.lineno}, col {e.colno}: {e.msg}")
        return False
```

---

## 7. 代码示例

### 完整 SVP 编辑示例

```python
import json
import uuid

def edit_svp_lyrics(input_path, output_path, lyric_mapping):
    """
    修改 SVP 文件中的歌词
    
    lyric_mapping: dict, key=old_lyric, value=new_lyric
    """
    with open(input_path, "r", encoding="utf-8") as f:
        project = json.load(f)
    
    modified_count = 0
    for group in project.get("library", []):
        for note in group.get("notes", []):
            old_lyric = note.get("lyrics", "")
            if old_lyric in lyric_mapping:
                note["lyrics"] = lyric_mapping[old_lyric]
                modified_count += 1
    
    # 保存（保留可读性）
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(project, f, ensure_ascii=False, indent=2)
    
    print(f"Modified {modified_count} lyrics")
    return modified_count

# 使用示例
edit_svp_lyrics("input.svp", "output.svp", {
    "old_lyric": "new_lyric",
    "la": "ra"
})
```

### 修改 SVP 参数曲线

```python
def add_pitch_point(svp_path, output_path, group_name, position_blick, value_cents):
    """
    在 SVP 的指定 NoteGroup 中添加音高控制点
    
    position_blick: blick 位置
    value_cents: 音高偏移（音分，100 cents = 1 semitone）
    """
    with open(svp_path, "r", encoding="utf-8") as f:
        project = json.load(f)
    
    for group in project.get("library", []):
        if group.get("name") == group_name:
            params = group.setdefault("parameters", {})
            pitch_delta = params.setdefault("pitchDelta", {
                "mode": "cubic",
                "points": []
            })
            
            # 添加新控制点并排序
            pitch_delta["points"].append([position_blick, value_cents])
            pitch_delta["points"].sort(key=lambda p: p[0])
            
            print(f"Added pitch point at {position_blick}: {value_cents} cents")
            break
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(project, f, ensure_ascii=False, indent=2)
```

### VPR 内部 JSON 处理

```python
import json
import zipfile

def edit_vpr_notes(vpr_path, output_path, note_transform):
    """
    修改 VPR 文件中的音符
    
    note_transform: callable, 接收 note dict 返回修改后的 dict
    """
    with zipfile.ZipFile(vpr_path, "r") as z:
        with z.open("Project/sequence.json") as f:
            data = json.load(f)
    
    # 修改音符
    for track in data.get("tracks", []):
        for part in track.get("parts", []):
            if part.get("type") == "musical":
                for note in part.get("notes", []):
                    note_transform(note)
    
    # 重新打包为 VPR
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as z:
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        z.writestr("Project/sequence.json", json_str.encode("utf-8"))
```

---

*本文档基于 JSON 标准和歌声合成工程文件实际格式编写。*
