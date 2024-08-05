from click.testing import CliRunner
from dns_updater.cli import main

def test_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
