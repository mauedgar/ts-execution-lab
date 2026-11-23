"""Historical native Q5B archive join: source-only negative tests."""
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("q5b_join",ROOT/"adapters"/"original_q5b_native_consumer.py")
join=importlib.util.module_from_spec(spec)
spec.loader.exec_module(join)

class NativeHistoricalJoinNegatives(unittest.TestCase):
    def test_missing_original_metadata_blocks(self):
        r={"id":join.NATIVE_RUN,"head_sha":join.NATIVE_HEAD,"run_attempt":1,
           "status":"completed","conclusion":"success"}
        a={"id":join.NATIVE_ARTIFACT,"size_in_bytes":join.NATIVE_BYTES,
           "digest":"sha256:"+join.NATIVE_SHA,"expired":False,
           "workflow_run":{"id":join.NATIVE_RUN,"head_sha":join.NATIVE_HEAD}}
        join.verify_provider_meta(r,a)
        a["workflow_run"]["head_sha"]="0"*40
        with self.assertRaisesRegex(ValueError,"ARTIFACT_RUN_HEAD_MISMATCH"):
            join.verify_provider_meta(r,a)
        a["workflow_run"]["head_sha"]=join.NATIVE_HEAD
        a["expired"]=True
        with self.assertRaisesRegex(ValueError,"ARTIFACT_EXPIRED"):
            join.verify_provider_meta(r,a)

    def test_archive_digest_blocks_substituted_and_corrupt_zips(self):
        with self.assertRaisesRegex(ValueError,"NATIVE_ZIP_HASH_OR_SIZE_MISMATCH"):
            join.verify_zip(b"fake-zip-not-native")
        self.assertEqual(len(join.NAMES),16)
        self.assertEqual(len(set(join.NAMES)),16)

    def test_missing_report_cannot_construct_fake_original(self):
        report={"schema":"ts-ee/frontend-browser-qa/v0.1"}
        fake={name:b"{}" for name in join.NAMES}
        fake["common/COMMON_RECEIPT_V01.json"]=json.dumps(report).encode()
        with self.assertRaisesRegex(ValueError,"ORIGINAL_COMMON_SOURCE_MISMATCH"):
            join.verify_original_members(fake)

    def test_create_only_output_collision(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"join"
            p.mkdir()
            with self.assertRaisesRegex(ValueError,"CREATE_ONLY_OUTPUT_COLLISION"):
                join.create_only_output(p,{},{})

    def test_no_browser_launcher_in_python_source(self):
        code=(ROOT/"adapters"/"original_q5b_native_consumer.py").read_text("utf8")
        self.assertNotIn("selenium",code)
        self.assertNotIn("import subprocess",code)
        self.assertNotIn("webdriver",code)

if __name__=="__main__":unittest.main()
