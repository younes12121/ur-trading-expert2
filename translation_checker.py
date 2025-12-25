#!/usr/bin/env python3
"""
Translation Completion Checker and Auto-Completer
Checks all language files and completes missing translations
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Set

class TranslationManager:
    def __init__(self, languages_dir: str = "languages"):
        self.languages_dir = Path(languages_dir)
        self.languages_dir.mkdir(exist_ok=True)
        self.base_language = "en"

    def load_language(self, lang_code: str) -> Dict[str, Any]:
        """Load a language file"""
        lang_file = self.languages_dir / f"{lang_code}.json"
        if not lang_file.exists():
            return {}

        try:
            with open(lang_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {lang_code}: {e}")
            return {}

    def save_language(self, lang_code: str, data: Dict[str, Any]):
        """Save a language file"""
        lang_file = self.languages_dir / f"{lang_code}.json"
        with open(lang_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_all_keys(self, data: Dict[str, Any], prefix: str = "") -> Set[str]:
        """Get all translation keys recursively"""
        keys = set()
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            keys.add(full_key)
            if isinstance(value, dict):
                keys.update(self.get_all_keys(value, full_key))
        return keys

    def get_missing_keys(self, base_data: Dict[str, Any], target_data: Dict[str, Any]) -> Set[str]:
        """Get keys missing in target language"""
        base_keys = self.get_all_keys(base_data)
        target_keys = self.get_all_keys(target_data)
        return base_keys - target_keys

    def count_translations(self, base_data: Dict[str, Any], target_data: Dict[str, Any]) -> tuple[int, int]:
        """Count completed vs total translations"""
        base_keys = self.get_all_keys(base_data)
        target_keys = self.get_all_keys(target_data)
        completed = len(base_keys & target_keys)
        total = len(base_keys)
        return completed, total

    def check_all_languages(self):
        """Check completion status of all languages"""
        base_data = self.load_language(self.base_language)
        if not base_data:
            print("Error: English base language file not found!")
            return

        languages = [f.stem for f in self.languages_dir.glob("*.json") if f.stem != self.base_language]

        print("TRANSLATION COMPLETION STATUS")
        print("=" * 60)

        for lang in sorted(languages):
            lang_data = self.load_language(lang)
            completed, total = self.count_translations(base_data, lang_data)

            if total == 0:
                percentage = 0
            else:
                percentage = (completed / total) * 100

            if percentage >= 95:
                status = "[COMPLETE]"
            elif percentage >= 75:
                status = "[MOSTLY COMPLETE]"
            elif percentage >= 50:
                status = "[PARTIALLY COMPLETE]"
            else:
                status = "[NEEDS WORK]"

            print("20")

        print("\n" + "=" * 60)

    def complete_translations(self, target_lang: str, source_lang: str = None):
        """Complete missing translations for a target language"""
        if source_lang is None:
            source_lang = self.base_language

        base_data = self.load_language(self.base_language)
        source_data = self.load_language(source_lang)
        target_data = self.load_language(target_lang)

        if not base_data:
            print("Error: Base language file not found!")
            return

        # Copy structure from base
        completed_data = self._deep_copy_structure(base_data)

        # Fill in existing translations
        self._merge_translations(completed_data, target_data)

        # Save completed file
        self.save_language(target_lang, completed_data)
        print(f"Completed translations for {target_lang}")

    def _deep_copy_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Deep copy the structure of translation data"""
        result = {}
        for key, value in data.items():
            if isinstance(value, dict):
                result[key] = self._deep_copy_structure(value)
            else:
                result[key] = ""  # Empty placeholder
        return result

    def _merge_translations(self, target: Dict[str, Any], source: Dict[str, Any]):
        """Merge existing translations into target structure"""
        for key, value in source.items():
            if key in target:
                if isinstance(value, dict) and isinstance(target[key], dict):
                    self._merge_translations(target[key], value)
                else:
                    target[key] = value

def main():
    manager = TranslationManager()

    print("Checking translation status...")
    manager.check_all_languages()

    print("\nAUTO-COMPLETING MISSING TRANSLATIONS...")

    # Languages that need completion
    priority_langs = ["es", "ar", "zh", "ru", "it"]
    additional_langs = ["pt", "ja", "de", "fr", "hi"]

    all_langs = priority_langs + additional_langs

    for lang in all_langs:
        lang_file = manager.languages_dir / f"{lang}.json"
        if not lang_file.exists():
            print(f"Creating new language file: {lang}")
            manager.complete_translations(lang)
        else:
            print(f"Checking and updating: {lang}")
            manager.complete_translations(lang)

    print("\nTRANSLATION COMPLETION FINISHED!")
    print("\nNEXT STEPS:")
    print("1. Review each language file manually")
    print("2. Fill in missing translations marked with empty strings")
    print("3. Test translations in the bot with /language command")
    print("4. Add any language-specific cultural adaptations")

if __name__ == "__main__":
    main()
