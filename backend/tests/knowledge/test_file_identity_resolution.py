from pathlib import Path

import pytest

from core.project import Project, ProjectMetadata

from app.knowledge.builder import KnowledgeBuilder


def build(
    project_root: Path,
    files: list[Path],
    previous=None,
):
    project = Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=project_root,
        )
    )
    project.statistics.scanned_files = files
    return KnowledgeBuilder().build(
        project,
        previous=previous,
    )


def current_location(file):
    return next(
        location
        for location in file.locations
        if location.is_current
    )


def current_fingerprint(file):
    return next(
        fingerprint
        for fingerprint in file.fingerprints
        if fingerprint.is_current
    )


def test_new_file_identity_is_deterministic_and_path_is_relative(
    tmp_path,
):
    source = tmp_path / "main.py"
    source.write_text("value = 1\n")

    first = build(tmp_path, [source])
    second = build(tmp_path, [source])

    assert first.files[0].file_id == second.files[0].file_id
    assert current_location(first.files[0]).path == "main.py"
    assert first.files[0].file_id != "main.py"


def test_content_change_preserves_identity_and_adds_fingerprint(
    tmp_path,
):
    source = tmp_path / "main.py"
    source.write_text("value = 1\n")
    first = build(tmp_path, [source])

    source.write_text("value = 2\n")
    second = build(tmp_path, [source], previous=first)

    assert first.files[0].file_id == second.files[0].file_id
    assert len(second.files[0].fingerprints) == 2
    assert (
        current_fingerprint(second.files[0]).content_hash
        != current_fingerprint(first.files[0]).content_hash
    )


@pytest.mark.parametrize(
    "destination_name",
    ["renamed.py", "src/main.py"],
)
def test_unique_fingerprint_detects_move_or_rename_and_preserves_history(
    tmp_path,
    destination_name,
):
    source = tmp_path / "main.py"
    source.write_text("value = 1\n")
    first = build(tmp_path, [source])

    destination = tmp_path / destination_name
    destination.parent.mkdir(exist_ok=True)
    source.rename(destination)
    second = build(tmp_path, [destination], previous=first)

    assert first.files[0].file_id == second.files[0].file_id
    assert [
        (location.path, location.is_current)
        for location in second.files[0].locations
    ] == [
        ("main.py", False),
        (destination_name, True),
    ]


def test_removed_file_history_is_retained(
    tmp_path,
):
    source = tmp_path / "main.py"
    source.write_text("value = 1\n")
    first = build(tmp_path, [source])

    second = build(tmp_path, [], previous=first)

    assert len(second.files) == 1
    assert second.files[0].file_id == first.files[0].file_id
    assert not any(
        location.is_current
        for location in second.files[0].locations
    )
    assert not any(
        fingerprint.is_current
        for fingerprint in second.files[0].fingerprints
    )


def test_removed_file_reappearance_preserves_identity(
    tmp_path,
):
    source = tmp_path / "main.py"
    source.write_text("value = 1\n")
    first = build(tmp_path, [source])
    removed = build(tmp_path, [], previous=first)
    reappeared = build(tmp_path, [source], previous=removed)

    assert reappeared.files[0].file_id == first.files[0].file_id
    assert current_location(reappeared.files[0]).path == "main.py"


def test_ambiguous_duplicate_content_does_not_merge_identities(
    tmp_path,
):
    first_path = tmp_path / "a.py"
    second_path = tmp_path / "b.py"
    first_path.write_text("same = True\n")
    second_path.write_text("same = True\n")
    first = build(tmp_path, [first_path, second_path])
    previous_ids = {file.file_id for file in first.files}

    destination = tmp_path / "c.py"
    destination.write_text("same = True\n")
    second = build(tmp_path, [destination], previous=first)
    current = next(
        file
        for file in second.files
        if any(
            location.path == "c.py" and location.is_current
            for location in file.locations
        )
    )

    assert current.file_id not in previous_ids
    assert len(second.files) == 3


def test_reverted_content_selects_historical_fingerprint(
    tmp_path,
):
    source = tmp_path / "main.py"
    source.write_text("value = 1\n")
    first = build(tmp_path, [source])
    original_hash = current_fingerprint(
        first.files[0]
    ).content_hash

    source.write_text("value = 2\n")
    second = build(tmp_path, [source], previous=first)
    source.write_text("value = 1\n")
    third = build(tmp_path, [source], previous=second)

    assert len(third.files[0].fingerprints) == 2
    assert (
        current_fingerprint(third.files[0]).content_hash
        == original_hash
    )
