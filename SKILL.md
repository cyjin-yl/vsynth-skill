---
name: vsynth
description: >
  Vocal synthesis project file editing, tuning, and creation skill for AI agents. Enables reading, editing,
  validating, creating, and tuning of singing synthesis project files across VOCALOID (.vsq/.vsqx/.vpr),
  UTAU/OpenUtau (.ust/.ustx), Synthesizer V (.svp/.s5p), CeVIO (.ccs), ACE Studio (.acep),
  DiffSinger (.ds), and other formats. Supports lyric editing, pitch curve generation (PIT/PBS/PBW),
  dynamics, vibrato, phoneme editing, track splitting, cross-format conversion,
  project file validation, empty project creation, and voicebank resource generation (reclist, oto.ini)
  via bundled Python CLI parsers.
compatibility: python>=3.9, requires ruamel.yaml and zstandard
---

# VSynth — Vocal Synthesis Project Editor

## What This Skill Does

Enables AI agents to act as vocal synthesis tuning assistants: reading, editing, and validating singing synthesis projects across 15+ software formats.

Core capabilities include project parsing, lyric and phoneme editing, pitch curves, dynamics, vibrato, track structures, empty templates, recording lists, oto.ini templates, audio preprocessing, and cross-format conversion.

## Read First: Project-Based Adaptation and Evidence

Before adapting lyrics, converting a tuned project, or creating timed subtitles/PV replacements, read:

- [Project-first workflow and delivery checks](references/project_first_workflow.md): source/version manifests, actual attacks versus morae, rhythm/word boundaries, tuning transfer, subtitle timing, PV motion, and layered validation.
- [Japanese V4 → Mandarin](references/japanese_v4_mandarin.md): engine-specific phoneme limitations, explicit locks, pronunciation A/B tests, and reference-informed—not magically recovered—BRI/BRE.

Do not automatically truncate lyrics, append filler, repeat the last word, split notes, or occupy rests to make character counts match. Do not treat every kana as a new syllable or every nasal/long-looking spelling as a disposable note. Inspect the actual project and listen when an engine is available. Preserve user-confirmed wording and timing in later exports.

The older cross-language references contain experimental mappings and historical recipes. Where they suggest automatic filler/truncation, imply that pinyin is a Japanese dictionary input, or equate generic X-SAMPA with a bank's supported inventory, use the constraints in the two references above instead. A mapping candidate is not a proven native pronunciation.

Report separately: structural validation, editor loading, voicebank rendering, listening, and media synchronization. Never claim an unperformed render, RMVPE run, subagent review, or independent approval.

## Supported Formats

| Software | Extension | Base Format | Encoding | Notes |
|----------|-----------|-------------|----------|-------|
| VOCALOID 2 | `.vsq` | SMF + INI | Shift-JIS | Legacy |
| VOCALOID 3/4 | `.vsqx` | XML (vsq3/vsq4) | UTF-8 | Namespace matters |
| VOCALOID 5/6 | `.vpr` | ZIP + JSON | UTF-8 | Engine/track type matters |
| UTAU | `.ust` | INI-like text | Shift-JIS/UTF-8 | Resolve event tempo overrides |
| OpenUtau | `.ustx` | YAML 1.2 | UTF-8 with BOM | Validate with the target version |
| Synthesizer V Studio | `.svp` | JSON, blick time | UTF-8 | 705600000 blick per quarter |
| Synthesizer V Editor | `.s5p` | JSON, legacy | UTF-8 | Distinct from SVP |
| CeVIO/VoiSona | `.ccs/.ccst` | XML | Unicode | Read format reference |
| ACE Studio | `.acep` | zstd + JSON | UTF-8 | Version-dependent |
| DiffSinger | `.ds` | JSON | UTF-8 | Phonemizer/model-dependent |
| Piapro Studio | `.ppsf` | JSON+ZIP / binary | UTF-8 | Version-dependent |
| NEUTRINO | `.musicxml` | MusicXML | UTF-8 | Score-based |
| DeepVocal | `.dv` | Custom binary | — | Read format reference |
| Standard MIDI | `.mid` | SMF | — | Read PPQ and tempo events |

This table is a navigation aid, not a guarantee that every field or engine behavior transfers losslessly.

## Quick Start

### 1. Read the project

Determine the actual format and version, then parse:

- `.vsqx`: XML tree with the correct `vsq3` or `vsq4` namespace.
- `.svp`: JSON. A quarter note is **705600000 blick**. At 480 PPQ, one VOCALOID tick is **1470000 blick**, not one beat.
- `.ust`: INI-like sections; inspect encoding, source aliases, rests, and effective tempo changes.
- `.vpr`: ZIP container, including `Project/sequence.json` where applicable.
- `.acep`: decompress according to the observed format version, then parse JSON.

A filename or MIME type is not proof of content. Keep original inputs immutable and record hashes before editing.

### 2. Edit safely

- XML: [references/xml_guidelines.md](references/xml_guidelines.md)
- JSON: [references/json_guidelines.md](references/json_guidelines.md)
- YAML: [references/yaml_guidelines.md](references/yaml_guidelines.md)
- INI/text: [references/ini_guidelines.md](references/ini_guidelines.md)

Preserve unmodified fields. Do not erase original pitch/vibrato while claiming only to change lyrics. Lyrics, phonemes, bank selection, timing, and parameter migration must each be verified.

### 3. Validate after editing

```bash
python -m vsynth.scripts.cli validate project.vsqx
python -m vsynth.scripts.cli info project.vsqx

# Standalone structural guard; standard library only.
python scripts/audit_vsqx4.py edited.vsqx --baseline original.vsqx --require-phoneme-lock
python -m unittest discover -s tests -p 'test_audit_vsqx4.py' -v
```

The standalone auditor checks note geometry, part overlaps, missing phonemes, explicit locks, orphan continuations, controller ordering, and basic ranges. Its synthetic tests contain no third-party song data. It is not an XSD validator, pronunciation recognizer, or audio-quality test; geometry comparison assumes corresponding track/part order. The lock option is for projects intentionally using explicit phonemes, not a universal requirement for all native projects.

## Reference Navigation

### Format Specifications

| File | Read when working with |
|------|------------------------|
| [references/vocaloid.md](references/vocaloid.md) | VOCALOID `.vsq`, `.vsqx`, `.vpr` |
| [references/utau.md](references/utau.md) | UTAU `.ust`, OpenUtau `.ustx` |
| [references/synthv.md](references/synthv.md) | Synthesizer V `.svp`, `.s5p` |
| [references/others.md](references/others.md) | CeVIO, ACE, DiffSinger, NEUTRINO |
| [references/xsampa.md](references/xsampa.md) | Phonetic symbols; verify against the actual bank |
| [references/cross_language.md](references/cross_language.md) | Historical Chinese/Japanese experiments; apply the constraints above |
| [references/vpr_cross_language.md](references/vpr_cross_language.md) | VPR-specific track/phoneme fields; do not apply to legacy V4 indiscriminately |
| [references/utau_voicebank.md](references/utau_voicebank.md) | Reclist and UTAU bank design |
| [references/oto_ini.md](references/oto_ini.md) | oto.ini parameters |
| [references/preprocessing.md](references/preprocessing.md) | Audio preprocessing and transcription |

### Tuning & Notation

| File | Read when |
|------|-----------|
| [references/tuning.md](references/tuning.md) | Adjusting pitch, vibrato, dynamics, breath and release |
| [references/phoneme_splitting.md](references/phoneme_splitting.md) | Considering articulation edits; splitting requires the user's applicable permission |
| [references/notations.md](references/notations.md) | Handling Asp, Sil, br, cl, -, R and source-specific aliases |
| [references/track_splitting.md](references/track_splitting.md) | Multi-track arrangements and bank separation |
| [references/voicebank_defects.md](references/voicebank_defects.md) | Bank range, register and synthesis limitations |
| [references/project_first_workflow.md](references/project_first_workflow.md) | End-to-end lyric, tuning, subtitle and PV delivery |
| [references/japanese_v4_mandarin.md](references/japanese_v4_mandarin.md) | Mandarin approximation with a Japanese V4 bank |

## Parameter and Unit Reminders

| Field | Meaning | Important distinction |
|-------|---------|-----------------------|
| VOCALOID PIT | Signed pitch-bend controller, -8192…8191 | Decode with PBS and the engine's baseline pitch |
| VOCALOID PBS | Pitch-bend sensitivity in semitones | Not the same as UST PBS |
| UST PBS | Mode2 curve's initial position/offset | Time coordinate is milliseconds |
| UST PBW/PBY/PBM | Segment widths, pitch offsets, curve shapes | PBY units are 10 cents; do not confuse shapes or units |
| VOCALOID VEL | Consonant timing/attack behavior | Not MIDI-style note volume; UTAU's same name is not a direct numeric mapping |
| DYN | Dynamics | Not an exact inverse of waveform RMS |
| BRI/BRE | Brightness/breathiness controls | Not directly obtainable from F0, HNR or spectral ratio |
| VOCALOID GEN | Gender/formant-related controller | Serialized scale and signed UI conventions are different |
| GWL/XSY | Growl/cross-synthesis, available in V4 with compatible banks | Availability is bank/engine-specific |
| SV pitchDelta | Pitch deviation in cents | Add to the correct SV baseline, not blindly to MIDI key |
| SV loudness/tension/breathiness | Engine-specific expression | Do not confuse raw parameter values with displayed percentages |

For signed PIT conversion, preserve the asymmetric negative/positive endpoints. Cross-engine portamento compensation is a model unless the target output has actually been rendered and measured.

## Common Operations

### Lyrics and phonemes

- VSQX4 uses short tags such as `note > y` and `note > p`; VSQX3 uses different names. Respect the namespace/version rather than searching only for `lyric`.
- A pinyin label does not give a Japanese bank Mandarin support. Store target Chinese, pinyin, and actual bank-native phonemes separately; lock intentional phoneme overrides and read them back.
- SVP notes may be in `mainGroup` and/or referenced groups. Inspect actual placement and group offsets before editing.
- UST `Lyric=` can be an audio alias, including VCV prefixes or a bank-specific release/breath name. A hyphen inside an alias is not necessarily a continuation.

### Pitch and vibrato

- VOCALOID: PIT plus PBS; retain note/part coordinates and avoid duplicate native vibrato if vibrato is baked into PIT.
- Synthesizer V: inspect `pitchDelta`, note transitions/vibrato and other pitch layers present in the actual version.
- UST: distinguish Mode1 from Mode2; read PBS/PBW/PBY/PBM and VBR instead of exporting a flat note grid.

Do not pretend source oto.ini, overlap, preutterance, envelope, or resampler flags have a universal one-to-one target mapping. List unsupported migrations.

### Dynamics and reference audio

Measure reference features only when audio was actually available and the analysis ran. Preserve raw results, confidence and the time map. Octave mistakes, harmonies, processing and unvoiced consonants can contaminate estimates. RMVPE is an F0 estimator, not a BRI/BRE recovery tool. Provide neutral-control comparisons for uncalibrated expression candidates.

## Cross-Format Conversion

Read PPQ, tempo changes, group/part offsets and preroll. Convert every timestamp from its original coordinate; avoid cumulative rounded timing drift.

- VOCALOID ticks ↔ SV blick: at 480 PPQ, multiply/divide by 1470000.
- UST PBY × 10 gives cents; VOCALOID pitch also depends on PBS and its baseline.
- Loudness, brightness and breathiness controls are not generally interchangeable between engines.
- Phoneme support is specific to the engine and voicebank, not merely to a shared-looking symbol spelling.

## CLI Tool Reference

```bash
pip install ruamel.yaml zstandard
python -m vsynth.scripts.cli validate project.vsqx --verbose
python -m vsynth.scripts.cli info project.svp
python -m vsynth.scripts.cli detect unknown_file
python -m vsynth.scripts.cli extract project.vpr --output ./extracted
python -m vsynth.scripts.cli list-formats
python -m vsynth.scripts.cli create --format ustx --output new_project.ustx
python -m vsynth.scripts.cli generate reclist --type cvvc --lang ja --output reclist.txt
python -m vsynth.scripts.cli generate oto --type cv --lang ja --output oto.ini
```

The bundled CLI and parsers are separate from the new standalone auditor. Consult their returned errors; do not claim conversion or editor compatibility solely because a file was written.

## Important Warnings

- UST encoding mistakes corrupt aliases. Keep source encoding evidence and test any converted text.
- Do not silently normalize unexpected JSON values or strip fields without a format-specific reason. Some real-world files may contain nonstandard values; report how they were handled.
- XML parsing is not synthesis validation. Treat external entities/DTDs defensively.
- VPR/ACEP/container structure is version-dependent; preserve original members and metadata where required.
- Source UST readmes, song assets, voicebanks and fonts can restrict redistribution. Public contributions should contain methods and synthetic fixtures, not private materials or full copyrighted songs.
- Download links must refer to files that exist. For media, check full decoding, sample rate/length, encoding delay and synchronization before claiming a usable result.

## Sources and References

- https://resource.dreamtonics.com/scripting/SV.html — official blick/quarter definitions
- https://github.com/sdercolin/utaformatix3 — open-source format conversion
- https://github.com/openutau/OpenUtau — UST and USTX implementation
- https://github.com/SoulMelody/LibreSVIP — format schemas and conversion models
- https://github.com/Dream-High/RMVPE — F0 estimation
- https://www.vocaloid.com/products/show/v4l_kaai_yuki_natural — bank language/features
- https://github.com/InuInu2022/LibSasara — CeVIO parsing

Additional historical resources remain in the format-specific references. Interpret tutorial examples within their stated voicebank and software version.
