from agentic_bi_copilot.cli import main


def test_cli_lists_supported_sample_questions(capsys):
    exit_code = main(["--list-questions"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Supported sample questions" in captured.out
    assert "segment_revenue" in captured.out
    assert "Which customer segment has the highest revenue?" in captured.out
