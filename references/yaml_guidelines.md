# YAML 编辑规范

> 适用于 .ustx (OpenUtau) 工程文件

---

## 目录

1. [缩进规则](#1-缩进规则)
2. [引号使用](#2-引号使用)
3. [多行字符串](#3-多行字符串)
4. [锚点和别名](#4-锚点和别名)
5. [常见错误](#5-常见错误)
6. [代码示例](#6-代码示例)

---

## 1. 缩进规则

### 绝对不能用 Tab！

> **警告**：YAML 标准禁止使用 Tab 字符缩进。制表符 (Tab) 会导致 YAML 解析错误。

### 空格缩进数量

- 使用 **2 个空格** 或 **4 个空格** 缩进
- 同一文件中缩进数量必须一致
- OpenUtau 的 .ustx 文件通常使用 **2 个空格** 缩进

### 正确示例

```yaml
# 正确：使用 2 个空格缩进
tracks:
  - singer: "voicebank"
    phonemizer: "JA VCV"
    track_name: "Main"

# 正确：使用 4 个空格缩进
tracks:
    - singer: "voicebank"
      phonemizer: "JA VCV"
      track_name: "Main"
```

### 错误示例

```yaml
# 错误：混用 Tab 和空格
tracks:
	- singer: "voicebank"    # ← Tab!
    phonemizer: "JA VCV"     # ← 空格
```

### Python 检测 Tab

```python
def check_tabs(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if "\t" in line:
                print(f"Line {i}: Found TAB character!")
                return False
    print("No TAB characters found")
    return True
```

---

## 2. 引号使用

### 何时需要引号

| 情况 | 示例 | 是否需要引号 |
|------|------|------------|
| 普通字符串 | `lyric: hello` | 不需要 |
| 含特殊字符 | `lyric: "hello world"` | 需要 |
| 含冒号 | `text: "key: value"` | 需要 |
| 数字字符串 | `version: "0.6"` | 需要（避免解析为数字） |
| 空字符串 | `comment: ""` | 需要 |
| 布尔值 | `mute: true` | 不需要 |

### USTX 中的引号要求

```yaml
# 推荐：版本号使用引号（避免被解析为数字）
ustx_version: "0.6"

# 推荐：可能含空格的字符串使用引号
name: "My Song Title"

# 可选：简单字符串不需要引号
lyric: do
abbr: dyn
```

---

## 3. 多行字符串

### 两种风格

```yaml
# 保留换行符 (Literal block scalar)
comment: |
  This is line 1
  This is line 2

# 折叠换行符 (Folded block scalar)
description: >
  This is all
  one line when parsed
```

### USTX 中的应用

```yaml
# 歌词可能有多行时使用
notes:
  - lyric: |
      第一行歌词
      第二行歌词
```

---

## 4. 锚点和别名

### YAML 锚点语法

```yaml
# 定义锚点
defaults: &defaults
  volume: 0.0
  pan: 0.0
  mute: false

# 引用锚点
tracks:
  - <<: *defaults
    track_name: "Lead"
  - <<: *defaults
    track_name: "Harmony"
```

### 在 USTX 中的使用

虽然 USTX 格式理论上支持锚点，但 OpenUtau 可能不完全支持 YAML 的高级特性。建议：
- 避免在 USTX 中使用锚点和别名
- 保持文件扁平化，便于 OpenUtau 解析

---

## 5. 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| `Block sequence entries are not allowed in this context` | 歌词包含 Tab 或缩进错误 | 移除所有 Tab，统一空格缩进 |
| `found character '\t' that cannot start any token` | 文件包含 Tab 字符 | 将 Tab 替换为空格 |
| `mapping values are not allowed here` | `:` 后面缺少空格 | `key: value`（冒号后必须有空格） |
| `did not find expected key` | 缩进不一致 | 检查所有行的缩进空格数 |
| `unexpected end of stream` | 文件不完整 | 检查文件是否被截断 |
| `while scanning a quoted scalar` | 引号不匹配 | 检查 `"` 或 `'` 是否成对 |

### USTX 特定错误

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| OpenUtau 崩溃 | USTX 包含 Tab | 移除所有制表符 |
| YAML 解析错误 | 从 UST/VSQX/MIDI 导入时引入不可见字符 | 清理不可见字符 |
| 歌词显示异常 | YAML 字符串解析问题 | 使用引号包裹含特殊字符的歌词 |

---

## 6. 代码示例

### 使用 ruamel.yaml 处理 USTX

```python
from ruamel.yaml import YAML

def load_ustx(filepath):
    """加载 USTX 文件（支持 YAML 1.2）"""
    yaml = YAML()
    yaml.preserve_quotes = True  # 保留引号
    with open(filepath, "r", encoding="utf-8-sig") as f:
        data = yaml.load(f)
    return data

def save_ustx(data, filepath):
    """保存 USTX 文件"""
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.indent(mapping=2, sequence=4, offset=2)
    
    with open(filepath, "w", encoding="utf-8") as f:
        yaml.dump(data, f)

def edit_ustx_lyrics(filepath, output_path, lyric_mapping):
    """
    修改 USTX 文件中的歌词
    
    lyric_mapping: dict, key=old_lyric, value=new_lyric
    """
    data = load_ustx(filepath)
    
    for part in data.get("voice_parts", []):
        for note in part.get("notes", []):
            old = note.get("lyric", "")
            if old in lyric_mapping:
                note["lyric"] = lyric_mapping[old]
    
    save_ustx(data, output_path)
```

### 清理 USTX 中的 Tab

```python
def clean_ustx_tabs(input_path, output_path):
    """移除 USTX 文件中的所有 Tab 字符"""
    with open(input_path, "r", encoding="utf-8-sig") as f:
        content = f.read()
    
    # 替换 Tab 为 2 个空格
    content = content.replace("\t", "  ")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Cleaned file saved to {output_path}")
```

### 验证 YAML 格式

```python
from ruamel.yaml import YAML

def validate_yaml(filepath):
    yaml = YAML()
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            yaml.load(f)
        print("YAML is valid")
        return True
    except Exception as e:
        print(f"YAML error: {e}")
        return False
```

### 添加 USTX 曲线控制点

```python
def add_curve_point(data, part_index, abbr, tick, value):
    """
    在 USTX 的指定片段中添加曲线控制点
    
    data: USTX 数据对象
    part_index: voice_parts 的索引
    abbr: 曲线缩写 ("pitd", "dyn", "brec", 等)
    tick: tick 位置
    value: 数值
    """
    voice_parts = data.get("voice_parts", [])
    if part_index >= len(voice_parts):
        raise IndexError(f"Part index {part_index} out of range")
    
    part = voice_parts[part_index]
    curves = part.setdefault("curves", [])
    
    # 查找或创建指定类型的曲线
    curve = None
    for c in curves:
        if c.get("abbr") == abbr:
            curve = c
            break
    
    if curve is None:
        curve = {"xs": [], "ys": [], "abbr": abbr}
        curves.append(curve)
    
    # 添加控制点并排序
    curve["xs"].append(tick)
    curve["ys"].append(value)
    
    # 按 xs 排序
    pairs = sorted(zip(curve["xs"], curve["ys"]), key=lambda p: p[0])
    curve["xs"] = [p[0] for p in pairs]
    curve["ys"] = [p[1] for p in pairs]
    
    return curve
```

---

> **关键提示**：Python 开发者处理 USTX 时应使用 `ruamel.yaml`（支持 YAML 1.2），不要使用 `pyyaml`。ruamel.yaml 正确编码为 `utf-8-sig`（带 BOM）。

---

*本文档基于 YAML 1.2 标准和 OpenUtau USTX 文件格式编写。*
