"""
歌声合成工程文件验证和解析工具包。

支持格式:
- VOCALOID: .vsq, .vsqx, .vpr
- UTAU: .ust, .ustx (OpenUtau)
- Synthesizer V: .svp, .s5p
- CeVIO: .ccs
- ACE Studio: .acep
- 标准 MIDI: .mid
"""

from .base_parser import BaseParser
from .vsqx_parser import VsqxParser
from .vsq_parser import VsqParser
from .vpr_parser import VprParser
from .ust_parser import UstParser
from .ustx_parser import UstxParser
from .svp_parser import SvpParser
from .s5p_parser import S5pParser
from .ccs_parser import CcsParser
from .acep_parser import AcepParser
from .midi_parser import MidiParser

__version__ = "1.0.0"
__all__ = [
    "BaseParser",
    "VsqxParser",
    "VsqParser",
    "VprParser",
    "UstParser",
    "UstxParser",
    "SvpParser",
    "S5pParser",
    "CcsParser",
    "AcepParser",
    "MidiParser",
]
