import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "extract_video_frames.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("extract_video_frames", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ExtractVideoFramesTest(unittest.TestCase):
    def test_build_command_supports_every_n_frames(self):
        module = load_module()
        command = module.build_ffmpeg_command(
            ffmpeg_bin="ffmpeg",
            input_path=Path("/tmp/demo.mp4"),
            output_pattern=Path("/tmp/frames/frame-%05d.png"),
            fps=None,
            every_n_frames=10,
        )

        self.assertEqual(command[:3], ["ffmpeg", "-i", "/tmp/demo.mp4"])
        self.assertIn("select=not(mod(n\\,10))", command)
        self.assertIn("-vsync", command)
        self.assertIn("vfr", command)

    def test_resolve_ffmpeg_bin_prefers_rtk_env_override(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            fake_ffmpeg = Path(temp_dir) / "ffmpeg"
            fake_ffmpeg.write_text("#!/bin/sh\n", encoding="utf-8")
            fake_ffmpeg.chmod(0o755)

            resolved = module.resolve_ffmpeg_bin({"RTK_FFMPEG_BIN": str(fake_ffmpeg)})
            self.assertEqual(resolved, str(fake_ffmpeg))


if __name__ == "__main__":
    unittest.main()
