# XML 编辑规范

> 适用于 .vsqx (VOCALOID 3/4), .ccs (CeVIO) 等 XML 格式工程文件

---

## 目录

1. [命名空间处理](#1-命名空间处理)
2. [转义规则](#2-转义规则)
3. [CDATA 使用](#3-cdata-使用)
4. [编码声明](#4-编码声明)
5. [常见错误](#5-常见错误)
6. [代码示例](#6-代码示例)

---

## 1. 命名空间处理

### VOCALOID VSQX 命名空间

| 版本 | 根元素 | 默认命名空间 | Schema 文件 |
|------|--------|-------------|------------|
| VOCALOID 3 | `<vsq3>` | `http://www.yamaha.co.jp/vocaloid/schema/vsq3/` | `vsq3.xsd` |
| VOCALOID 4 | `<vsq4>` | `http://www.yamaha.co.jp/vocaloid/schema/vsq4/` | `vsq4.xsd` |

**示例（VOCALOID 4）**:
```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<vsq4 xmlns="http://www.yamaha.co.jp/vocaloid/schema/vsq4/"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.yamaha.co.jp/vocaloid/schema/vsq4/ vsq4.xsd">
```

### 命名空间注意事项

> **警告**：命名空间必须正确匹配根元素名
> - V3 编辑器无法打开 `vsq4` 根元素的文件（报错：`no declaration found for element 'vsq4'`）
> - V4 编辑器可以打开 `vsq3` 和 `vsq4` 两种文件
> - 根元素名和命名空间必须一致（`vsq3` ↔ vsq3 schema, `vsq4` ↔ vsq4 schema）

### Python 命名空间处理

```python
import xml.etree.ElementTree as ET

tree = ET.parse("input.vsqx")
root = tree.getroot()

# 方法1：检测根元素名判断版本
ns = root.tag.split('}')[0].strip('{') if '}' in root.tag else ''
is_vsq4 = 'vsq4' in ns

# 方法2：使用 lxml（推荐）
from lxml import etree
tree = etree.parse("input.vsqx")
root = tree.getroot()
nsmap = {"ns": "http://www.yamaha.co.jp/vocaloid/schema/vsq4/"}
notes = root.findall(".//ns:note", namespaces=nsmap)
```

---

## 2. 转义规则

### 必须转义的字符

| 字符 | 转义序列 | 说明 |
|------|---------|------|
| `&` | `&amp;` | 与号 |
| `<` | `&lt;` | 小于号 |
| `>` | `&gt;` | 大于号 |
| `"` | `&quot;` | 双引号 |
| `'` | `&apos;` | 单引号 |

### 歌词中的转义

歌词文本可能包含需要转义的字符：

```xml
<!-- 错误：未转义 & -->
<y>R&B</y>

<!-- 正确：& 转义为 &amp; -->
<y>R&amp;B</y>
```

### Python 自动转义

```python
from xml.sax.saxutils import escape

lyric = "R&B <demo>"
escaped = escape(lyric)
# 结果: "R&amp;B &lt;demo&gt;"
```

---

## 3. CDATA 使用

### 何时使用 CDATA

CDATA 区块用于包含大量不需要 XML 解析器处理的文本内容：

```xml
<!-- 使用 CDATA 包含歌词（避免转义） -->
<y><![CDATA[R&B <demo> "test"]]></y>
```

### VSQX 中的 CDATA

VSQX 文件中，歌词和音素通常使用普通文本节点（非 CDATA）：

```xml
<!-- 标准写法（普通文本） -->
<y>あ</y>
<p>a</p>

<!-- 需要时使用 CDATA -->
<y><![CDATA[特殊&符号<歌词>]]></y>
```

### 注意事项

> **警告**：CDATA 不能嵌套。如果需要包含 `]]>` 字符串，必须分割为多个 CDATA 区块或使用转义。

---

## 4. 编码声明

### XML 声明格式

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
```

### 各格式编码要求

| 格式 | 编码 | BOM |
|------|------|-----|
| VSQX (V3/V4) | UTF-8 | **无** |
| CCS (CeVIO) | Unicode | - |
| MusicXML | UTF-8 | 通常无 |

> **警告**：VSQX 使用 UTF-8 **无 BOM**。添加 BOM 可能导致部分解析器出错。

### Python 保存 XML

```python
import xml.etree.ElementTree as ET

# 保存时指定编码为 UTF-8，不包含 BOM
tree.write("output.vsqx", encoding="UTF-8", xml_declaration=True)

# 使用 lxml 可以更精细控制
from lxml import etree
tree.write("output.vsqx", encoding="UTF-8", xml_declaration=True, standalone=None)
```

---

## 5. 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| `no declaration found for element 'vsq4'` | V3 编辑器打开 V4 文件 | 在 V4 编辑器中打开，或转换回 V3 |
| 乱码/ Mojibake | 编码不匹配 | 确保使用 UTF-8 无 BOM |
| XML 解析失败 | 特殊字符未转义 | 对 `&<>` 进行转义或使用 CDATA |
| 命名空间错误 | 命名空间与根元素不匹配 | 检查 `xmlns` 和根元素名 |
| 缩进丢失 | 保存时未保留空白 | 使用 `pretty_print=True` (lxml) |
| 文件头丢失 | 未写入 XML 声明 | 保存时添加 `xml_declaration=True` |

### 验证 XML 格式

```python
from lxml import etree

def validate_xml(file_path):
    try:
        tree = etree.parse(file_path)
        print("XML is well-formed")
        return True
    except etree.XMLSyntaxError as e:
        print(f"XML syntax error: {e}")
        return False
```

---

## 6. 代码示例

### 完整 VSQX 编辑示例

```python
from lxml import etree

def edit_vsqx_lyrics(input_path, output_path, lyric_mapping):
    """
    修改 VSQX 文件中的歌词
    
    lyric_mapping: dict, key=old_lyric, value=new_lyric
    """
    parser = etree.XMLParser(strip_cdata=False)
    tree = etree.parse(input_path, parser)
    root = tree.getroot()
    
    # 检测版本
    ns = root.tag.split('}')[0].strip('{') if '}' in root.tag else ''
    is_vsq4 = 'vsq4' in ns
    
    # 构建命名空间映射
    tag_prefix = "{http://www.yamaha.co.jp/vocaloid/schema/vsq4/}" if is_vsq4 else ""
    nsmap = {"ns": "http://www.yamaha.co.jp/vocaloid/schema/vsq4/"} if is_vsq4 else {}
    
    # 查找所有音符
    for note in root.iter(f"{tag_prefix}note"):
        lyric_node = note.find(f"{tag_prefix}y")
        if lyric_node is not None and lyric_node.text in lyric_mapping:
            new_lyric = lyric_mapping[lyric_node.text]
            # 处理特殊字符
            lyric_node.text = new_lyric
    
    # 保存（保留格式）
    tree.write(output_path, encoding="UTF-8", xml_declaration=True,
               pretty_print=True, standalone="no")
    print(f"Saved to {output_path}")

# 使用示例
edit_vsqx_lyrics("input.vsqx", "output.vsqx", {
    "old_lyric": "new_lyric",
    "do": "ra"
})
```

### 修改 VSQX 控制参数

```python
from lxml import etree

def add_dyn_event(vsqx_path, output_path, pos_tick, value):
    """在 VSQX 中添加 DYN 控制事件"""
    tree = etree.parse(vsqx_path)
    root = tree.getroot()
    
    ns = {"ns": "http://www.yamaha.co.jp/vocaloid/schema/vsq4/"}
    
    # 找到第一个 vsTrack
    track = root.find(".//ns:vsTrack", namespaces=ns)
    
    # 创建新的 cc 元素
    cc = etree.SubElement(track, "{http://www.yamaha.co.jp/vocaloid/schema/vsq4/}cc")
    
    id_elem = etree.SubElement(cc, "{http://www.yamaha.co.jp/vocaloid/schema/vsq4/}id")
    id_elem.text = "DYN"
    
    pos_elem = etree.SubElement(cc, "{http://www.yamaha.co.jp/vocaloid/schema/vsq4/}posTick")
    pos_elem.text = str(pos_tick)
    
    val_elem = etree.SubElement(cc, "{http://www.yamaha.co.jp/vocaloid/schema/vsq4/}value")
    val_elem.text = str(value)
    
    tree.write(output_path, encoding="UTF-8", xml_declaration=True,
               pretty_print=True, standalone="no")
```

---

*本文档基于 XML 标准和歌声合成工程文件实际格式编写。*
