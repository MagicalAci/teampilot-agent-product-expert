"""scripts/security_self_check.py 单元测试。

为避免测试源码自身被仓库级扫描误判，所有"假密钥"均在运行时拼接构造，
源码里不出现可被正则匹配的字面量（该文件也已在脚本 SELF_SKIP 中）。
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import security_self_check as sc  # noqa: E402


class SecuritySelfCheckTest(unittest.TestCase):
    def test_detects_openai_style_key(self):
        secret = "sk-" + "A1b2C3d4" * 4  # 运行时构造，源码无字面量密钥
        findings = sc.scan_text(f'SECRET_KEY = "{secret}"')
        self.assertTrue(findings)
        self.assertEqual(findings[0]["type"], "OpenAI/Anthropic key")

    def test_detects_github_token(self):
        token = "ghp_" + "x9Y8z7W6" * 3
        findings = sc.scan_text(f'token = "{token}"')
        self.assertTrue(any("GitHub" in f["type"] for f in findings))

    def test_detects_generic_assignment(self):
        value = "Ab1" + "q7W2e9R4" * 2
        findings = sc.scan_text(f'api_key = "{value}"')
        self.assertTrue(findings)

    def test_ignores_placeholders(self):
        for line in [
            'API_KEY = "your-key-here"',
            'token = "${MY_TOKEN}"',
            'SECRET_KEY = os.environ.get("HELLOBIKE_API_KEY", "")',
            'key = "<replace-with-real-key>"',
        ]:
            with self.subTest(line=line):
                self.assertEqual(sc.scan_text(line), [])

    def test_allowlist_marker_exempts_line(self):
        secret = "sk-" + "Z9y8X7w6" * 4
        line = f'EXAMPLE = "{secret}"  # pragma: allowlist secret'
        self.assertEqual(sc.scan_text(line), [])

    def test_clean_code_has_no_findings(self):
        self.assertEqual(sc.scan_text("def hello():\n    return 'world'\n"), [])

    def test_allowlisted_secret_is_exempt(self):
        # 从模块读取，避免在测试源码里写死密钥字面量。
        allowed = next(iter(sc.ALLOWLISTED_SECRETS))
        self.assertEqual(sc.scan_text(f'SECRET_KEY = "{allowed}"'), [])

    def test_repo_currently_passes(self):
        # 修复硬编码 key 后，本仓库应当通过密钥扫描。
        self.assertEqual(sc.scan_repo(), [])


if __name__ == "__main__":
    unittest.main()
