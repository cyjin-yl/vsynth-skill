"""Structural VSQX4 audit. Passing this audit does not validate synthesized audio."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

NS = "http://www.yamaha.co.jp/vocaloid/schema/vsq4/"
Q = lambda tag: "{" + NS + "}" + tag


def ticks_to_seconds(tick: int, tempos: list[tuple[int, float]], ppq: int) -> float:
    """Integrate an effective tempo map. Resolve format-specific overrides first."""
    if ppq <= 0 or tick < 0 or not tempos or tempos[0][0] != 0:
        raise ValueError("Require nonnegative tick, positive PPQ, tempo at tick zero")
    if any(not math.isfinite(bpm) or bpm <= 0 for _, bpm in tempos):
        raise ValueError("Tempo must be finite and positive")
    if any(b[0] <= a[0] for a, b in zip(tempos, tempos[1:])):
        raise ValueError("Tempo positions must be strictly increasing")
    result = 0.0
    for i, (start, bpm) in enumerate(tempos):
        if start >= tick:
            break
        end = min(tick, tempos[i + 1][0]) if i + 1 < len(tempos) else tick
        result += (end - start) * 60.0 / (bpm * ppq)
    return result


def audit(path: str | Path, *, require_phoneme_lock: bool = False) -> dict:
    data = Path(path).read_bytes()
    if b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
        raise ValueError("DTD/entity declarations are not accepted")
    root = ET.fromstring(data)
    if root.tag != Q("vsq4"):
        raise ValueError("Expected VSQX4 namespace/root, not VSQX3")
    errors, warnings, geometry = [], [], []
    def number(node, tag):
        value = node.findtext(Q(tag))
        if value is None:
            raise ValueError("Missing required element: " + tag)
        return int(value)
    for tr_index, track in enumerate(root.findall(Q("vsTrack"))):
        track_events = []
        for part_index, part in enumerate(track.findall(Q("vsPart"))):
            offset = number(part, "t")
            if offset < 0:
                errors.append(f"track {tr_index}: negative part offset")
            previous = None
            for note_index, note in enumerate(part.findall(Q("note"))):
                t, length, pitch = (number(note, key) for key in ("t", "dur", "n"))
                tag = f"track {tr_index} part {part_index} note {note_index}"
                if t < 0 or length <= 0 or not 0 <= pitch <= 127:
                    errors.append(tag + ": invalid note geometry")
                phoneme = note.find(Q("p"))
                lyric = note.findtext(Q("y"), "")
                if phoneme is None or not (phoneme.text or "").strip():
                    errors.append(tag + ": missing phonemes")
                elif require_phoneme_lock and phoneme.get("lock") != "1":
                    errors.append(tag + ": phoneme not explicitly locked")
                if previous is not None and t < previous[0] + previous[1]:
                    errors.append(tag + ": overlapping or unsorted notes")
                if lyric == "-" and phoneme is not None and phoneme.text == "-":
                    if previous is None or t != previous[0] + previous[1] or previous[2] == "Sil":
                        errors.append(tag + ": continuation has no adjacent previous note")
                if lyric == "-" and phoneme is not None and phoneme.text not in ("-", "Sil"):
                    warnings.append(tag + ": explicit vowel/coda on continuation; audition")
                if length < 60:
                    warnings.append(tag + ": short tick duration; inspect real milliseconds")
                previous = (t, length, phoneme.text if phoneme is not None else None)
                geometry.append((tr_index, part_index, offset + t, length, pitch))
                track_events.append((offset + t, offset + t + length, tag))
            last_cc = {}
            for control in part.findall(Q("cc")):
                t = number(control, "t")
                element = control.find(Q("v"))
                if element is None:
                    errors.append("missing controller value")
                    continue
                name, value = element.get("id"), int(element.text)
                if t < 0 or t <= last_cc.get(name, -1):
                    errors.append(f"track {tr_index}: unsorted/duplicate {name} controller")
                last_cc[name] = t
                bounds = (-8192, 8191) if name == "P" else (1, 24) if name == "S" else (0, 127)
                if not bounds[0] <= value <= bounds[1]:
                    errors.append(f"track {tr_index}: {name} outside {bounds}")
        track_events.sort()
        prior_end = -1
        for start, end, tag in track_events:
            if start < prior_end:
                errors.append(tag + ": overlapping parts/notes in absolute track time")
            prior_end = max(prior_end, end)
    return {"valid": not errors, "errors": errors, "warnings": warnings,
            "note_count": len(geometry), "geometry": geometry,
            "rendered_audio_validated": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--require-phoneme-lock", action="store_true")
    args = parser.parse_args()
    result = audit(args.project, require_phoneme_lock=args.require_phoneme_lock)
    if args.baseline:
        baseline = audit(args.baseline)
        same = result["geometry"] == baseline["geometry"]
        result["geometry_matches_baseline"] = same
        if not same:
            result["errors"].append("note/part geometry differs from baseline")
            result["valid"] = False
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
