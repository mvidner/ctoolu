"""Tests for ctoolu.actions."""

import re

import pytest

from ctoolu.actions import (
    CtooluAction,
    CtooluCommand,
    match_actions,
    posix_ere_to_python,
    substitute,
    _parse_action,
)


class TestPosixEreConversion:
    def test_digit_class(self):
        assert posix_ere_to_python('[[:digit:]]+') == '[0-9]+'

    def test_alpha_class(self):
        assert posix_ere_to_python('[[:alpha:]]') == '[a-zA-Z]'

    def test_space_class(self):
        result = posix_ere_to_python('[[:space:]]')
        assert re.match(result, ' ')
        assert re.match(result, '\t')

    def test_negated_class(self):
        result = posix_ere_to_python('[^[:space:]]')
        assert re.match(result, 'a')
        assert not re.match(result, ' ')

    def test_multiple_classes_in_one_bracket(self):
        result = posix_ere_to_python('[[:digit:][:alpha:]]')
        assert re.match(result, '5')
        assert re.match(result, 'x')
        assert not re.match(result, ' ')

    def test_no_posix_classes(self):
        assert posix_ere_to_python('abc(def)+') == 'abc(def)+'

    def test_complex_pattern(self):
        pattern = '[[:alpha:]][^[:space:]/]+(:[^[:space:]/]+)+'
        result = posix_ere_to_python(pattern)
        compiled = re.compile(result)
        assert compiled.search('openSUSE:Factory')
        assert compiled.search('systemsmanagement:Agama:Devel')
        assert not compiled.search('nocolon')


class TestSubstitute:
    def test_single_sequential(self):
        assert substitute('id=%s', ['42']) == 'id=42'

    def test_multiple_sequential(self):
        assert substitute('%s/%s', ['foo', 'bar']) == 'foo/bar'

    def test_positional(self):
        assert substitute('%1$s and %1$s', ['x']) == 'x and x'

    def test_mixed_positional(self):
        assert substitute('%1$s/%2$s/%1$s', ['a', 'b']) == 'a/b/a'

    def test_no_placeholders(self):
        assert substitute('plain text', []) == 'plain text'


class TestParseAction:
    def test_basic_action(self):
        data = {
            'label': 'Test',
            'regex': 'bug#([[:digit:]]+)',
            'url': 'https://example.com/%s',
        }
        action = _parse_action(data)
        assert action.label == 'Test'
        assert action.url == 'https://example.com/%s'
        m = action.regex.search('bug#123')
        assert m.group(1) == '123'

    def test_case_insensitive(self):
        data = {
            'label': 'Test',
            'regex': 'bug#([[:digit:]]+)',
            'case_sensitive': False,
        }
        action = _parse_action(data)
        assert action.regex.search('BUG#123')

    def test_case_sensitive_default(self):
        data = {
            'label': 'Test',
            'regex': 'Bug#([[:digit:]]+)',
        }
        action = _parse_action(data)
        assert action.regex.search('Bug#123')
        assert not action.regex.search('bug#123')

    def test_with_commands(self):
        data = {
            'label': 'Test',
            'regex': 'x(\\d+)',
            'commands': [
                {'label': 'cmd1', 'command': 'echo %s', 'keep_output': True},
                {'label': 'cmd2', 'command': 'run %s'},
            ],
        }
        action = _parse_action(data)
        assert len(action.commands) == 2
        assert action.commands[0].keep_output is True
        assert action.commands[1].keep_output is False


class TestMatchActions:
    def setup_method(self):
        self.actions = [
            CtooluAction('Bug', re.compile(r'bug#(\d+)', re.I), 'http://bugs/%s'),
            CtooluAction('URL', re.compile(r'(https?://\S+)'), None),
        ]

    def test_single_match(self):
        matches = match_actions('bug#42', self.actions)
        assert len(matches) == 1
        assert matches[0][0].label == 'Bug'
        assert matches[0][1].group(1) == '42'

    def test_multiple_matches(self):
        matches = match_actions('bug#42 http://example.com', self.actions)
        assert len(matches) == 2

    def test_no_match(self):
        matches = match_actions('nothing here', self.actions)
        assert len(matches) == 0


class TestCtooluCommand:
    def test_execute_keep_output(self, mocker):
        cmd = CtooluCommand('test', "echo 'hello %s'", keep_output=True)
        clipboard_values = []
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value.stdout = 'hello world'
        cmd.execute(['world'], clipboard_values.append)
        mock_run.assert_called_once_with(
            "echo 'hello world'", shell=True, capture_output=True, text=True,
        )
        assert clipboard_values == ['hello world']

    def test_execute_background(self, mocker):
        cmd = CtooluCommand('test', 'xdg-open %s', keep_output=False)
        mock_popen = mocker.patch('subprocess.Popen')
        cmd.execute(['http://example.com'], lambda x: None)
        mock_popen.assert_called_once()


class TestYamlPatterns:
    """Test that the converted YAML pattern files parse and match correctly."""

    @pytest.fixture
    def load_yaml_actions(self):
        """Load actions from a YAML file in data/ctoolu/."""
        import yaml
        from pathlib import Path

        def _load(filename):
            path = Path(__file__).parent.parent / 'data' / 'ctoolu' / filename
            with open(path) as f:
                data = yaml.safe_load(f)
            return [_parse_action(d) for d in data]
        return _load

    def test_opensuse_boo(self, load_yaml_actions):
        actions = load_yaml_actions('opensuse.yaml')
        boo = [a for a in actions if 'Bugzilla.openSUSE' in a.label][0]
        m = boo.regex.search('boo#999999')
        assert m
        assert m.group(1) == '999999'
        assert substitute(boo.url, list(m.groups())) == \
            'https://bugzilla.opensuse.org/show_bug.cgi?id=999999'

    def test_opensuse_boo_variants(self, load_yaml_actions):
        actions = load_yaml_actions('opensuse.yaml')
        boo = [a for a in actions if 'Bugzilla.openSUSE' in a.label][0]
        for text in ['boo#123', 'boo 123', 'boo-123', 'BOO#123']:
            assert boo.regex.search(text), f'Should match: {text}'

    def test_github_issue(self, load_yaml_actions):
        actions = load_yaml_actions('opensuse.yaml')
        gh = [a for a in actions if 'GitHub' in a.label][0]
        m = gh.regex.search('gh#agama-project/agama#999')
        assert m
        assert m.group(1) == 'agama-project/agama'
        assert m.group(2) == '999'

    def test_suse_bsc(self, load_yaml_actions):
        actions = load_yaml_actions('suse.yaml')
        bsc = [a for a in actions if 'Bugzilla.SUSE' in a.label][0]
        m = bsc.regex.search('bsc#1234567')
        assert m
        assert m.group(1) == '1234567'

    def test_obs_project(self, load_yaml_actions):
        actions = load_yaml_actions('opensuse.yaml')
        obs = [a for a in actions if 'BuildService Project' in a.label][0]
        m = obs.regex.search('openSUSE:Factory')
        assert m

    def test_url_pattern(self, load_yaml_actions):
        actions = load_yaml_actions('url.yaml')
        url_action = actions[0]
        m = url_action.regex.search('https://example.com/path')
        assert m
        assert m.group(1) == 'https://example.com/path'

    def test_kde_bug(self, load_yaml_actions):
        actions = load_yaml_actions('bugs.yaml')
        kde = [a for a in actions if 'KDE' in a.label][0]
        m = kde.regex.search('kde#12345')
        assert m
        assert m.group(1) == '12345'
        # Minimum 2 digits
        assert not kde.regex.search('kde#1')
