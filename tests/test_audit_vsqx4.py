"""Synthetic fixtures only; no third-party scores, audio, or lyrics."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

P = Path(__file__).resolve().parents[1] / "scripts" / "audit_vsqx4.py"
spec = importlib.util.spec_from_file_location("audit_vsqx4", P)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def fixture(notes, cc="", part_offset=1920):
    body = "".join(f'<note><t>{t}</t><dur>{d}</dur><n>{k}</n><y>{y}</y><p lock="{lock}">{p}</p></note>'
                   for t, d, k, y, p, lock in notes)
    return f'<vsq4 xmlns="{m.NS}"><vsTrack><vsPart><t>{part_offset}</t>{cc}{body}</vsPart></vsTrack></vsq4>'


class AuditTest(unittest.TestCase):
    def run_audit(self, text, **options):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / "test.vsqx"
            p.write_text(text, encoding="utf-8")
            return m.audit(p, **options)

    def test_adjacent_hold(self):
        r = self.run_audit(fixture([(0,240,60,"x","S i",1),(240,120,62,"-","-",1)]), require_phoneme_lock=True)
        self.assertTrue(r["valid"])
        self.assertEqual(r["geometry"][1], (0,0,2160,120,62))
        self.assertFalse(r["rendered_audio_validated"])

    def test_hold_over_rest(self):
        r = self.run_audit(fixture([(0,240,60,"x","a",1),(300,120,60,"-","-",1)]))
        self.assertFalse(r["valid"])

    def test_first_hold(self):
        self.assertFalse(self.run_audit(fixture([(0,240,60,"-","-",1)]))["valid"])

    def test_silent_release_is_not_orphan_hold(self):
        self.assertTrue(self.run_audit(fixture([(0,30,60,"-","Sil",1)]))["valid"])

    def test_overlap(self):
        self.assertFalse(self.run_audit(fixture([(0,240,60,"x","a",1),(100,120,62,"y","i",1)]))["valid"])

    def test_lock(self):
        self.assertFalse(self.run_audit(fixture([(0,240,60,"x","a",0)]), require_phoneme_lock=True)["valid"])

    def test_pit_negative_endpoint(self):
        cc = '<cc><t>0</t><v id="P">-8192</v></cc>'
        self.assertTrue(self.run_audit(fixture([(0,240,60,"x","a",1)], cc))["valid"])

    def test_pit_positive_out_of_range(self):
        cc = '<cc><t>0</t><v id="P">8192</v></cc>'
        self.assertFalse(self.run_audit(fixture([(0,240,60,"x","a",1)], cc))["valid"])

    def test_duplicate_controller(self):
        cc = '<cc><t>0</t><v id="R">60</v></cc><cc><t>0</t><v id="R">61</v></cc>'
        self.assertFalse(self.run_audit(fixture([(0,240,60,"x","a",1)], cc))["valid"])

    def test_tempo_integration(self):
        self.assertAlmostEqual(m.ticks_to_seconds(1440, [(0,120),(960,60)], 480), 2.)

    def test_duplicate_tempo_needs_resolution(self):
        with self.assertRaises(ValueError):
            m.ticks_to_seconds(480, [(0,500000),(0,144)], 480)

    def test_nonfinite_tempo(self):
        for bad in (float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                m.ticks_to_seconds(480, [(0, bad)], 480)

    def test_hold_after_silence(self):
        self.assertFalse(self.run_audit(fixture([(0,60,60,"br","Sil",1),(60,120,60,"-","-",1)]))["valid"])

    def test_absolute_part_overlap(self):
        text = fixture([(0,240,60,"x","a",1)])
        second = "<vsPart><t>2000</t><note><t>0</t><dur>120</dur><n>60</n><y>x</y><p>a</p></note></vsPart>"
        self.assertFalse(self.run_audit(text.replace("</vsTrack>", second + "</vsTrack>"))["valid"])

    def test_empty_phoneme(self):
        self.assertFalse(self.run_audit(fixture([(0,240,60,"x","",1)]))["valid"])

    def test_wrong_namespace(self):
        with self.assertRaises(ValueError):
            self.run_audit('<vsq3/>')

    def test_reject_doctype(self):
        with self.assertRaises(ValueError):
            self.run_audit('<!DOCTYPE foo><vsq4/>')


if __name__ == "__main__":
    unittest.main()
