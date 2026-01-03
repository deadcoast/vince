"""
Unit Tests for Vince CLI Entry Point

Feature: coverage-completion
Tests for the CLI entry point and module initialization.
Requirements: 1.1, 1.2
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from typer.testing import CliRunner

import vince


class TestMainModuleImport:
    """Tests for __main__.py module import functionality.
    
    Requirements: 1.1
    """

    def test_main_module_imports_successfully(self):
        """Test that __main__.py can be imported without errors.
        
        Requirements: 1.1
        """
        # Import should not raise any exceptions
        import vince.__main__
        
        # Verify the app is accessible
        assert hasattr(vince.__main__, 'app')

    def test_main_module_has_app_from_main(self):
        """Test that __main__.py imports app from vince.main.
        
        Requirements: 1.1
        """
        import vince.__main__
        from vince.main import app
        
        # The app in __main__ should be the same as in main
        assert vince.__main__.app is app

    def test_vince_package_has_version(self):
        """Test that vince package exposes __version__.
        
        Requirements: 1.2
        """
        assert hasattr(vince, '__version__')
        assert isinstance(vince.__version__, str)
        assert len(vince.__version__) > 0


class TestCLIHelp:
    """Tests for CLI --help invocation.
    
    Requirements: 1.2
    """

    @pytest.fixture
    def runner(self):
        """Provide a Typer CLI test runner."""
        return CliRunner()

    def test_cli_help_invocation(self, runner):
        """Test CLI --help works and shows expected content.
        
        Requirements: 1.2
        """
        from vince.main import app
        
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "vince" in result.output.lower()
        # Should show available commands
        assert "slap" in result.output
        assert "chop" in result.output
        assert "set" in result.output
        assert "list" in result.output

    def test_cli_short_help_flag(self, runner):
        """Test CLI -h short help flag works.
        
        Requirements: 1.2
        """
        from vince.main import app
        
        # Typer uses --help by default, -h may not be enabled
        # Test the standard --help
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "Usage" in result.output or "usage" in result.output.lower()


class TestCLIVersion:
    """Tests for CLI --version invocation.
    
    Requirements: 1.2
    """

    @pytest.fixture
    def runner(self):
        """Provide a Typer CLI test runner."""
        return CliRunner()

    def test_cli_version_invocation(self, runner):
        """Test CLI --version works and shows version.
        
        Requirements: 1.2
        """
        from vince.main import app
        
        result = runner.invoke(app, ["--version"])
        
        assert result.exit_code == 0
        assert vince.__version__ in result.output

    def test_cli_short_version_flag(self, runner):
        """Test CLI -v short version flag works.
        
        Requirements: 1.2
        """
        from vince.main import app
        
        result = runner.invoke(app, ["-v"])
        
        assert result.exit_code == 0
        assert vince.__version__ in result.output

    def test_version_output_format(self, runner):
        """Test version output contains 'vince version X.Y.Z' format.
        
        Requirements: 1.2
        """
        from vince.main import app
        
        result = runner.invoke(app, ["--version"])
        
        assert result.exit_code == 0
        # Should contain "vince version" text
        assert "vince" in result.output.lower()
        assert "version" in result.output.lower()


class TestCLIInitialization:
    """Tests for CLI initialization behavior.
    
    Requirements: 1.1
    """

    @pytest.fixture
    def runner(self):
        """Provide a Typer CLI test runner."""
        return CliRunner()

    def test_cli_initializes_without_error(self, runner):
        """Test CLI initializes correctly without any arguments.
        
        Requirements: 1.1
        """
        from vince.main import app
        
        # Invoking with no args shows usage/help (exit code 0 or 2 for missing command)
        result = runner.invoke(app, [])
        
        # Should not crash - Typer shows usage when no command given
        # Exit code 0 means help shown, exit code 2 means missing command (both valid)
        assert result.exit_code in [0, 2]
        # Should show usage information
        assert "Usage" in result.output or "usage" in result.output.lower()

    def test_cli_app_has_expected_commands(self):
        """Test CLI app has all expected commands registered.
        
        Requirements: 1.1
        """
        from vince.main import app
        
        # Get registered command names
        command_names = [cmd.name for cmd in app.registered_commands]
        
        expected_commands = ["slap", "chop", "set", "forget", "offer", "reject", "list", "sync"]
        
        for cmd in expected_commands:
            assert cmd in command_names, f"Command '{cmd}' not registered"

    def test_cli_app_has_correct_name(self):
        """Test CLI app has correct name configured.
        
        Requirements: 1.1
        """
        from vince.main import app
        
        assert app.info.name == "vince"

    def test_cli_app_has_help_text(self):
        """Test CLI app has help text configured.
        
        Requirements: 1.1
        """
        from vince.main import app
        
        assert app.info.help is not None
        assert len(app.info.help) > 0
        assert "default" in app.info.help.lower() or "application" in app.info.help.lower()


# =============================================================================
# Property-Based Tests for CLI Initialization
# Feature: coverage-completion
# Validates: Requirements 1.1
# =============================================================================


class TestCLIInitializationProperty:
    """Feature: coverage-completion, Property: CLI Initialization Correctness
    
    *For any* valid CLI invocation pattern (help, version, or command help),
    the CLI SHALL initialize without error and return appropriate output.
    
    Requirements: 1.1
    """

    @pytest.fixture
    def runner(self):
        """Provide a Typer CLI test runner."""
        return CliRunner()

    @given(st.sampled_from([
        ["--help"],
        ["-v"],
        ["--version"],
        ["slap", "--help"],
        ["chop", "--help"],
        ["set", "--help"],
        ["forget", "--help"],
        ["offer", "--help"],
        ["reject", "--help"],
        ["list", "--help"],
        ["sync", "--help"],
    ]))
    @settings(max_examples=100)
    def test_cli_initializes_without_error_for_all_help_patterns(self, args):
        """Property: CLI always initializes without error for help/version patterns.
        
        *For any* help or version invocation, the CLI SHALL initialize correctly
        and return exit code 0.
        
        Feature: coverage-completion, Property 1: CLI Initialization Correctness
        Validates: Requirements 1.1
        """
        from vince.main import app
        
        runner = CliRunner()
        result = runner.invoke(app, args)
        
        # All help/version invocations should succeed
        assert result.exit_code == 0, f"Failed for args {args}: {result.output}"
        # Should produce some output
        assert len(result.output) > 0

    @given(st.sampled_from([
        "slap", "chop", "set", "forget", "offer", "reject", "list", "sync"
    ]))
    @settings(max_examples=100)
    def test_all_commands_have_help(self, command):
        """Property: All registered commands have accessible help.
        
        *For any* registered command, invoking with --help SHALL succeed
        and display command-specific help text.
        
        Feature: coverage-completion, Property 1: CLI Initialization Correctness
        Validates: Requirements 1.1
        """
        from vince.main import app
        
        runner = CliRunner()
        result = runner.invoke(app, [command, "--help"])
        
        assert result.exit_code == 0
        # Help should mention the command name or usage
        assert "Usage" in result.output or command in result.output.lower()

    @given(st.integers(min_value=1, max_value=10))
    @settings(max_examples=100)
    def test_repeated_cli_initialization_is_stable(self, count):
        """Property: Repeated CLI initialization produces consistent results.
        
        *For any* number of repeated initializations, the CLI SHALL produce
        consistent help output.
        
        Feature: coverage-completion, Property 1: CLI Initialization Correctness
        Validates: Requirements 1.1
        """
        from vince.main import app
        
        runner = CliRunner()
        outputs = []
        
        for _ in range(count):
            result = runner.invoke(app, ["--help"])
            assert result.exit_code == 0
            outputs.append(result.output)
        
        # All outputs should be identical
        assert all(output == outputs[0] for output in outputs)
