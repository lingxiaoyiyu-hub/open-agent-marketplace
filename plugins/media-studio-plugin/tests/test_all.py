import os
import sys
import unittest

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from media_studio.config import StudioConfig
from media_studio.client import StudioClient
from media_studio.tts import split_text_into_chunks, synthesize_speech
from media_studio.image import generate_image
from media_studio.video import understand_video

class TestMediaStudioTools(unittest.TestCase):

    def test_config(self):
        cfg = StudioConfig()
        self.assertTrue(cfg.api_key)
        self.assertEqual(cfg.base_url, "https://api.stepfun.com/v1")

    def test_chunking(self):
        short_text = "这是一段短文本。"
        chunks = split_text_into_chunks(short_text, max_chars=100)
        self.assertEqual(len(chunks), 1)

        long_text = "段落一。" * 30 + "\n段落二！" * 30
        chunks_long = split_text_into_chunks(long_text, max_chars=100)
        self.assertGreaterThan = self.assertGreater(len(chunks_long), 1)
        for c in chunks_long:
            self.assertLessEqual(len(c), 100)

    def test_short_tts(self):
        out_path = os.path.join(os.path.dirname(__file__), "test_short.mp3")
        res_file = synthesize_speech(
            text="媒体创作语音合成测试",
            output_path=out_path,
            instruction="语气温柔"
        )
        self.assertTrue(os.path.exists(res_file))
        self.assertGreater(os.path.getsize(res_file), 1000)

    def test_long_tts(self):
        out_path = os.path.join(os.path.dirname(__file__), "test_long.mp3")
        # Create long text > 1000 chars
        para = "这是一段用于测试长文本自动分段合成的文案。这一段用于测试长文本自动分段合成与音频无缝拼接功能。"
        long_text = (para + "\n") * 12  # ~1100 chars
        
        res_file = synthesize_speech(
            text=long_text,
            output_path=out_path,
            instruction="语速偏快"
        )
        self.assertTrue(os.path.exists(res_file))
        self.assertGreater(os.path.getsize(res_file), 10000)

    def test_image_generation(self):
        out_path = os.path.join(os.path.dirname(__file__), "test_gen.png")
        res_file = generate_image(
            prompt="可爱的小猫咪在阳光下晒太阳",
            output_path=out_path,
            size="1024x1024"
        )
        self.assertTrue(os.path.exists(res_file))
        self.assertGreater(os.path.getsize(res_file), 10000)

if __name__ == "__main__":
    unittest.main()
