from pathlib import Path

import pytest

from paperchase.tools.files import read_file, write_file, edit_file, glob_files, grep_files


def test_write_then_read(tmp_path):
    p = tmp_path / "a.txt"
    write_file(str(p), "hello world")
    assert read_file(str(p)) == "hello world"


def test_edit_file(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("the quick brown fox")
    edit_file(str(p), old="brown", new="green")
    assert p.read_text() == "the quick green fox"


def test_edit_file_raises_when_old_missing(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("hi")
    with pytest.raises(ValueError):
        edit_file(str(p), old="bye", new="hello")


def test_glob_files(tmp_path):
    (tmp_path / "a.py").write_text("")
    (tmp_path / "b.py").write_text("")
    (tmp_path / "c.txt").write_text("")
    matches = sorted(glob_files(str(tmp_path / "*.py")))
    assert len(matches) == 2
    assert all(m.endswith(".py") for m in matches)


def test_grep_files(tmp_path):
    (tmp_path / "a.txt").write_text("alpha\nbeta\n")
    (tmp_path / "b.txt").write_text("beta\ngamma\n")
    hits = grep_files(pattern="beta", root=str(tmp_path))
    paths = sorted([h["path"] for h in hits])
    assert len(hits) == 2
    assert paths[0].endswith("a.txt") and paths[1].endswith("b.txt")
