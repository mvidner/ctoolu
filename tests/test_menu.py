"""Tests for ctoolu.menu."""

from ctoolu.menu import _add_mnemonic


class TestAddMnemonic:
    def test_first_letter(self):
        used = set()
        assert _add_mnemonic('Open browser', used) == '&Open browser'
        assert 'o' in used

    def test_skips_used_letter(self):
        used = {'o'}
        assert _add_mnemonic('Open folder', used) == 'Open &folder'
        assert 'f' in used

    def test_falls_back_to_non_initial(self):
        used = {'o', 'f'}
        assert _add_mnemonic('Open folder', used) == 'O&pen folder'
        assert 'p' in used

    def test_all_letters_used(self):
        used = set('openfld r')
        assert _add_mnemonic('Open folder', used) == 'Open folder'

    def test_case_insensitive(self):
        used = set()
        result = _add_mnemonic('Hello', used)
        assert result == '&Hello'
        assert 'h' in used
        # Now 'H' (uppercase) should also be skipped
        result2 = _add_mnemonic('Help', used)
        assert result2 == 'H&elp'

    def test_skips_non_alpha(self):
        used = set()
        assert _add_mnemonic('  indented', used) == '  &indented'

    def test_independent_groups(self):
        """Simulate building a menu with multiple items."""
        used = set()
        labels = ['Cancel', 'Copy URL', 'Copy text']
        results = [_add_mnemonic(label, used) for label in labels]
        assert results[0] == '&Cancel'
        assert results[1] == 'Copy &URL'
        assert results[2] == 'Copy &text'
