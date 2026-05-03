---
name: vsynth
description: >
  Vocal synthesis project file editing, tuning, and creation skill for AI agents. Enables reading, editing,
  validating, creating, and tuning of singing synthesis project files across VOCALOID (.vsq/.vsqx/.vpr),
  UTAU/OpenUtau (.ust/.ustx), Synthesizer V (.svp/.s5p), CeVIO (.ccs), ACE Studio (.acep),
  DiffSinger (.ds), and other formats. Supports lyric editing, pitch curve generation (PIT/PBS/PBW),
  dynamics (DYN/VEL), vibrato, phoneme splitting, track splitting, cross-format conversion,
  project file validation, empty project creation, and voicebank resource generation (reclist, oto.ini)
  via bundled Python CLI parsers.
compatibility: python>=3.9, requires ruamel.yaml and zstandard
---

# VSynth — Vocal Synthesis Project Editor

## What This Skill Does

Enables AI agents to act as **vocal synthesis tuning assistants** — reading, editing, and validating singing synthesis project files across 15+ software formats.

**Core capabilities:**
- Parse project files (.vsq, .vsqx, .vpr, .ust, .ustx, .svp, .s5p, .ccs, .acep, .ds, .mid)
- Edit lyrics, notes, pitch curves, dynamics, vibrato, and track structures
- Validate edited files via bundled Python CLI parsers
- Create empty project templates (.ust, .ustx, .vsqx, .svp)
- Generate voicebank resources: recording lists (reclist) and oto.ini templates
- Preprocess audio for transcription: vocal separation (UVR5) and audio-to-MIDI (GAME/SOME)
- Generate pitch/dynamic parameter curves programmatically
- Apply tuning techniques (portamento, breath, articulation, release)
- Split phonemes and tracks for advanced vocal arrangements
- Handle special notations (Asp, Sil, br, cl, -, R) across engines
- Identify voicebank defects and apply track-splitting / XSY strategies
- Cross-format conversion with parameter mapping awareness

## Supported Formats

| Software | Extension | Base Format | Encoding | Status |
|----------|-----------|-------------|----------|--------|
| VOCALOID 2 | `.vsq` | SMF + INI | Shift-JIS | Legacy |
| VOCALOID 3/4 | `.vsqx` | XML (vsq3/vsq4) | UTF-8 | Active |
| VOCALOID 5/6 | `.vpr` | ZIP + JSON | UTF-8 | Active |
| UTAU | `.ust` | INI-like text | Shift-JIS/UTF-8 | Active |
| OpenUtau | `.ustx` | YAML 1.2 | UTF-8 with BOM | Active |
| Synthesizer V Studio | `.svp` | JSON (blick time) | UTF-8 | Active |
| Synthesizer V Editor | `.s5p` | JSON (legacy) | UTF-8 | Discontinued |
| CeVIO/VoiSona | `.ccs/.ccst` | XML | Unicode | Active |
| ACE Studio | `.acep` | zstd + JSON | UTF-8 | Active |
| DiffSinger | `.ds` | JSON | UTF-8 | Active |
| Piapro Studio | `.ppsf` | JSON+ZIP / binary | UTF-8 | Active (NT) |
| NEUTRINO | `.musicxml` | MusicXML | UTF-8 | Active |
| DeepVocal | `.dv` | Custom binary | — | Discontinued |
| Standard MIDI | `.mid` | SMF | — | Universal |

## Quick Start

### 1. Read a project file

Determine format by extension, then parse:
- `.vsqx` → XML tree (ElementTree), namespace `vsq3` or `vsq4`
- `.svp` → JSON, time unit is `blick` (1 blick = 1/1470000 beat)
- `.ust` → INI-like sections, detect encoding (Shift-JIS vs UTF-8)
- `.vpr` → ZIP container, extract `Project/sequence.json`
- `.acep` → zstd decompress, then parse JSON

### 2. Edit safely

Before editing any file, check the format-specific guidelines:
- **XML** (.vsqx, .ccs): See [references/xml_guidelines.md](references/xml_guidelines.md)
- **JSON** (.vpr, .svp, .s5p, .acep, .ds): See [references/json_guidelines.md](references/json_guidelines.md)
- **YAML** (.ustx): See [references/yaml_guidelines.md](references/yaml_guidelines.md)
- **INI/Text** (.ust, .vsq): See [references/ini_guidelines.md](references/ini_guidelines.md)

### 3. Validate after editing

```bash
python -m vsynth.scripts.cli validate <file>
python -m vsynth.scripts.cli info <file>
```

## Reference Navigation

### Format Specifications (read when handling specific software)

| File | Covers | Read when working with |
|------|--------|------------------------|
| [references/vocaloid.md](references/vocaloid.md) | `.vsq`, `.vsqx`, `.vpr` | VOCALOID 2/3/4/5/6 files |
| [references/utau.md](references/utau.md) | `.ust`, `.ustx` | UTAU / OpenUtau files |
| [references/synthv.md](references/synthv.md) | `.svp`, `.s5p` | Synthesizer V files |
| [references/others.md](references/others.md) | `.ccs`, `.acep`, `.ds`, `.musicxml` | CeVIO, ACE, DiffSinger, NEUTRINO |
| [references/xsampa.md](references/xsampa.md) | X-SAMPA phonemes | Editing phonemes in VOCALOID / SV / DiffSinger |
| [references/cross_language.md](references/cross_language.md) | Chinese↔Japanese cross-language phonemes | Cross-language singing (general) |
| [references/vpr_cross_language.md](references/vpr_cross_language.md) | VPR cross-language, V6 phoneme format, isProtected | VOCALOID 5/6 cross-language projects |
| [references/utau_voicebank.md](references/utau_voicebank.md) | Reclist design, CV/VCV/CVVC/CVVX/VCCV | Creating or editing UTAU voicebanks |
| [references/oto_ini.md](references/oto_ini.md) | oto.ini parameters and generation | Configuring UTAU voicebank oto.ini |
| [references/preprocessing.md](references/preprocessing.md) | Audio-to-MIDI pipeline (UVR5, GAME, SOME) | Converting audio to singing project |

### Editing Guidelines (read before editing files)

| File | Covers | Read when |
|------|--------|-----------|
| [references/xml_guidelines.md](references/xml_guidelines.md) | Namespaces, escaping, CDATA | Editing `.vsqx`, `.ccs` |
| [references/json_guidelines.md](references/json_guidelines.md) | Escaping, precision, NaN | Editing `.svp`, `.s5p`, `.vpr`, `.acep`, `.ds` |
| [references/yaml_guidelines.md](references/yaml_guidelines.md) | Indentation, anchors, BOM | Editing `.ustx` |
| [references/ini_guidelines.md](references/ini_guidelines.md) | Sections, encoding, CRLF | Editing `.ust`, `.vsq` |

### Tuning & Notation (read when tuning vocals)

| File | Covers | Read when |
|------|--------|-----------|
| [references/tuning.md](references/tuning.md) | Parameter glossary, vibrato, portamento, breath | Adjusting pitch/dynamics |
| [references/phoneme_splitting.md](references/phoneme_splitting.md) | Phoneme splitting techniques | Improving articulation |
| [references/cross_language.md](references/cross_language.md) | Chinese↔Japanese cross-language singing | Tuning cross-language vocals with harmony |
| [references/vpr_cross_language.md](references/vpr_cross_language.md) | VPR format cross-language specifics, V6 AI track | Tuning V5/V6 cross-language projects |
| [references/notations.md](references/notations.md) | Asp, Sil, br, cl, -, R, breath symbols | Editing special lyric/phoneme notations |
| [references/track_splitting.md](references/track_splitting.md) | Harmony tracks, doubling, whisper tracks | Multi-track arrangements |
| [references/voicebank_defects.md](references/voicebank_defects.md) | Optimum Range, defects, XSY, register switch | Fixing voicebank quality issues or out-of-range notes |

## Parameter Glossary

| Param | Full Name | Meaning | Range | Used In |
|-------|-----------|---------|-------|---------|
| PIT | Pitch Bend | Pitch deviation from note | -8191~+8191 | VOCALOID |
| PBS | Pitch Bend Sensitivity | PIT scaling factor (semitones) | 1~24 | VOCALOID/UTAU |
| PBW | Pitch Bend Width | Control point widths (ms) | — | UTAU Mode2 |
| PBY | Pitch Bend Y | Control point offsets (10 cents) | — | UTAU Mode2 |
| DYN | Dynamics | Loudness/intensity | 0~127 | VOCALOID |
| VEL | Velocity | Attack speed / consonant strength | 0~127 | VOCALOID/UTAU |
| BRE | Breathiness | Breath noise amount | 0~127 | VOCALOID |
| BRI | Brightness | Harmonic brightness | 0~127 | VOCALOID |
| GEN | Gender Factor | Voice gender shift | -64~+63 | VOCALOID/UTAU |
| GWL | Growl | Growl intensity | 0~127 | VOCALOID5+ |
| XSY | Cross-Synthesis | Blend between two singers | 0~127 | VOCALOID4+ |
| pitchDelta | Pitch Deviation | Cent-based pitch curve | — | Synthesizer V |
| loudness | Loudness | Volume in dB | -∞~+24 | Synthesizer V |
| tension | Tension | Voice tension/relax | -2~+2 | Synthesizer V |
| breathiness | Breathiness | Breath amount | 0~100% | Synthesizer V |
| voicing | Voicing | Full voice to whisper | 0~100% | Synthesizer V |

## Common Operations

### Edit lyrics
- **VOCALOID .vsqx**: Modify `note > lyric` text nodes. Escape XML entities (`&`, `<`, `>`).
- **Synthesizer V .svp**: Modify `library[].notes[].lyrics`. Japanese lyrics may need phoneme override in `phonemes`.
- **UTAU .ust**: Modify `Lyric=` in note sections. Shift-JIS encoding — verify after save.

### Edit pitch curves
- **VOCALOID**: `PIT` array + `PBS` scaling. PIT range -8191 to +8191. Pitch change (semitones) = `PIT * PBS / 8191`.
- **Synthesizer V**: `parameters.pitchDelta.points` — array of `[tick, value]` pairs. Value in cents.
- **UTAU Mode2**: `PBS` (start position), `PBW` (widths in ms), `PBY` (offsets in 10 cents), `PBM` (curve types: `s`, `j`, `r`, or empty).

### Edit dynamics
- **VOCALOID**: `DYN` parameter array (0-127), same tick-based structure as PIT.
- **Synthesizer V**: `parameters.loudness.points` in dB, or `parameters.tension.points` for timbre.
- **UTAU**: `Intensity` per note (0-200), or `Flags` string for resampler effects.

### Add vibrato
- **VOCALOID**: `vibrato` attributes on note (length, depth, rate).
- **Synthesizer V**: Built-in vibrato via `note.attributes.dF0Vbr` (depth), `fF0Vbr` (frequency), `tF0VbrStart` (delay). Or `parameters.vibratoEnv` for envelope.
- **UTAU**: `VBR` field with format `length,period,depth,easeIn,easeOut,phase,shift`.

## Cross-Format Conversion

Use bundled CLI for format detection and validation. For actual conversion, understand these mappings:
- **Time**: VOCALOID tick (480/quarter) ↔ SV blick (1/1470000 beat) ↔ CeVIO clock (1/2 tick)
- **Pitch**: VOCALOID PIT×PBS/8191 ↔ SV cents/100 ↔ UTAU PBY×10 cents
- **Dynamics**: VOCALOID DYN (0-127) ↔ SV loudness (dB) — non-linear, needs curve mapping
- **Lyrics**: Japanese/Chinese phoneme systems differ; may need phoneme override after conversion

## CLI Tool Reference

```bash
# Install dependencies
pip install ruamel.yaml zstandard

# Validate any project file
python -m vsynth.scripts.cli validate project.vsqx [--verbose]

# Extract project info (notes, tracks, tempo, parameters)
python -m vsynth.scripts.cli info project.svp

# Detect file format automatically
python -m vsynth.scripts.cli detect unknown_file

# Extract container contents (vpr → ZIP, acep → zstd JSON)
python -m vsynth.scripts.cli extract project.vpr --output ./extracted

# List all supported formats
python -m vsynth.scripts.cli list-formats

# Create empty project template
python -m vsynth.scripts.cli create --format ustx --output new_project.ustx

# Generate voicebank recording list (reclist)
python -m vsynth.scripts.cli generate reclist --type cvvc --lang ja --output reclist.txt

# Generate oto.ini template
python -m vsynth.scripts.cli generate oto --type cv --lang ja --output oto.ini
```

Parsers return JSON output. Validation returns `{success, valid, errors[]}`. Info returns full project metadata. Create and generate commands return `{success, file, type}`.

## Important Warnings

- **UTAU .ust encoding**: Classic UTAU uses Shift-JIS; OpenUtau prefers UTF-8 with BOM. Wrong encoding = corrupted Japanese lyrics.
- **XML namespace**: VOCALOID .vsqx uses `vsq3` (V3) or `vsq4` (V4) namespace. Always include namespace in XPath/ElementTree queries.
- **JSON NaN**: Synthesizer V .svp may use `NaN` for default parameter values. Standard JSON parsers may fail — handle with `allow_nan=True` (Python) or use `json5`.
- **VPR ZIP structure**: VOCALOID .vpr is a ZIP with `Project/sequence.json` inside. Extract, edit JSON, then re-ZIP preserving structure.
- **ACEP zstd**: ACE Studio .acep uses zstandard compression (no encryption in v1.7.8+). Decompress with `zstandard` library before JSON parsing.

## Sources and References

Key external resources (full URLs in reference files):
- **kimi.secret.jp/wiki/dtm.php?vsqx** — VOCALOID .vsqx structure reference (Japanese)
- **github.com/sdercolin/utaformatix3** — Open-source format converter with 15+ format parsers
- **svdocs.dreamtonics.com** — Synthesizer V official script API docs
- **github.com/stakira/OpenUtau** — OpenUtau source (USTX format implementation)
- **w.atwiki.jp/boare** — cadencii VSQ/VPR reverse engineering docs (Japanese)
- **github.com/InuInu2022/LibSasara** — CeVIO .ccs parsing library
