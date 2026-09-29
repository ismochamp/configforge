"""Behavior-focused checks against the compiled C++ engine and local adapter."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from server import execute

class MigrationTests(unittest.TestCase):
    def run_engine(self,text,mapping=None,existing=None,raw=False,same_path=False):
        with tempfile.TemporaryDirectory() as work:
            work=Path(work);source=work/'source.ini';output=source if same_path else work/'out.json'
            source.write_bytes(text if raw else text.encode('utf-8'));original=source.read_bytes()
            if existing is not None:output.write_text(existing)
            args=[str(ROOT/'build'/('migrator.exe' if sys.platform=='win32' else 'migrator')),'--input',str(source),'--output',str(output)]
            if mapping is not None:
                schema=work/'mapping.tsv';schema.write_text(mapping);args+=['--map',str(schema)]
            p=subprocess.run(args,capture_output=True,text=True);result=json.loads(p.stdout)
            self.assertEqual(p.returncode,0 if result['ok'] else 2);self.assertEqual(source.read_bytes(),original)
            data=output.read_text() if output.exists() else None;self.assertFalse(list(work.glob('*.tmp-*')))
            return result,data

    def test_typed_fixture_preserves_windows_path(self):
        report,out=self.run_engine((ROOT/'fixtures/application.ini').read_text(),(ROOT/'fixtures/mapping.tsv').read_text());self.assertTrue(report['ok']);data=json.loads(out)
        self.assertEqual(data['worker_count'],4);self.assertEqual(data['port'],8080);self.assertEqual(data['timeout_seconds'],12.5)
        self.assertIs(data['debug_enabled'],False);self.assertIs(data['compression_enabled'],True)
        self.assertEqual(data['archive_path'],'C:\\Archive\\inbox')

    def test_comments_quoted_hash_and_escapes(self):
        report,out=self.run_engine('title="A # B; C" ; note\nmessage="first\\nsecond"\nurl=https://example.com/#anchor\nplain=yes # note\n')
        self.assertTrue(report['ok']);data=json.loads(out);self.assertEqual(data['title'],'A # B; C');self.assertEqual(data['message'],'first\nsecond');self.assertEqual(data['url'],'https://example.com/#anchor');self.assertEqual(data['plain'],'yes')

    def test_bom_crlf_unicode(self):
        report,out=self.run_engine('\ufeff[app]\r\nname=Müller\r\n');self.assertTrue(report['ok']);self.assertEqual(json.loads(out),{'[app]name':'Müller'})

    def test_duplicate_key_is_an_error(self):
        report,out=self.run_engine('[server]\nport=80\nport=90\n');self.assertFalse(report['ok']);self.assertIsNone(out);self.assertEqual(report['errors'][0]['line'],3)

    def test_duplicate_section_is_an_error(self):
        report,out=self.run_engine('[a]\nx=1\n[a]\ny=2\n');self.assertFalse(report['ok']);self.assertIsNone(out)

    def test_malformed_section_and_missing_equals(self):
        report,out=self.run_engine('[bad\nno equals\n');self.assertFalse(report['ok']);self.assertIsNone(out);self.assertGreaterEqual(len(report['errors']),2)

    def test_quoted_value_errors_block_export(self):
        for text in ['a="unfinished\n','a="value"trailing\n','a="bad\\z"\n']:
            with self.subTest(text=text):
                report,out=self.run_engine(text);self.assertFalse(report['ok']);self.assertIsNone(out)

    def test_required_missing_source(self):
        report,out=self.run_engine('[a]\nx=1\n','[a]missing\tkey\tinteger\ttrue\n');self.assertFalse(report['ok']);self.assertIsNone(out)

    def test_optional_empty_and_omitted_settings(self):
        report,out=self.run_engine('x=\ny=2\n','x\tempty\tinteger\tfalse\nz\tabsent\tstring\tfalse\n');self.assertTrue(report['ok']);self.assertEqual(json.loads(out),{'empty':None,'absent':None});self.assertEqual(len(report['warnings']),2)

    def test_invalid_types_block_entire_export(self):
        report,out=self.run_engine('x=4.2\ny=perhaps\nz=Infinity\n','x\tx\tinteger\ttrue\ny\ty\tboolean\ttrue\nz\tz\tnumber\ttrue\n');self.assertFalse(report['ok']);self.assertEqual(len(report['errors']),3);self.assertIsNone(out)

    def test_duplicate_json_target(self):
        report,out=self.run_engine('x=1\ny=2\n','x\tx\tinteger\ttrue\ny\tx\tinteger\ttrue\n');self.assertFalse(report['ok']);self.assertIsNone(out)

    def test_existing_output_is_not_replaced(self):
        report,out=self.run_engine('x=1\n',existing='KEEP ME');self.assertFalse(report['ok']);self.assertEqual(out,'KEEP ME')

    def test_input_cannot_be_output(self):
        report,out=self.run_engine('x=1\n',same_path=True);self.assertFalse(report['ok']);self.assertEqual(out,'x=1\n')

    def test_invalid_utf8(self):
        report,out=self.run_engine(b'x=\xff\n',raw=True);self.assertFalse(report['ok']);self.assertIsNone(out)

    def test_dashboard_adapter_runs_real_engine(self):
        result=execute('[server]\nport=443\n',[{'source':'[server]port','target':'listen_port','type':'integer','required':True}]);self.assertTrue(result['ok']);self.assertEqual(result['preview'],{'listen_port':443});self.assertEqual(json.loads(result['output']),result['preview'])

    def test_dashboard_rejects_bad_required_type(self):
        with self.assertRaises(ValueError):execute('x=1\n',[{'source':'x','target':'x','type':'string','required':'true'}])

if __name__=='__main__':unittest.main(verbosity=2)
