import unittest
import os
import json
from autoclicker_core import load_config, save_config, CONFIG_FILE

class TestAutoClickerCore(unittest.TestCase):

    def setUp(self):
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)

    def tearDown(self):
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)

    def test_default_config_loading(self):
        config = load_config()
        self.assertIn("Vortex", config["step1_keywords"])
        self.assertIn("Slow Download", config["step2_keywords"])
        self.assertTrue(config["ad_auto_close"])
        self.assertIn("Close", config["ad_keywords"])

    def test_config_saving_and_loading(self):
        custom_config = {
            "step1_keywords": ["Abrir Mod"],
            "step1_x": 400,
            "step1_y": 300,
            "step1_timeout": 3.0,
            
            "step2_keywords": ["Baixar Agora"],
            "step2_x": 800,
            "step2_y": 600,
            "step2_timeout": 6.0,

            "step_delay": 2.5,

            "ad_auto_close": True,
            "ad_keywords": ["Fechar", "Skip"]
        }
        save_config(custom_config)
        loaded = load_config()

        self.assertEqual(loaded["step1_keywords"], ["Abrir Mod"])
        self.assertEqual(loaded["step2_keywords"], ["Baixar Agora"])
        self.assertTrue(loaded["ad_auto_close"])
        self.assertEqual(loaded["ad_keywords"], ["Fechar", "Skip"])

if __name__ == "__main__":
    unittest.main()
