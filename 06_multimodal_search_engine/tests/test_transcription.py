from app.transcription.provider import parse_transcript


def test_parse_transcript_with_timecodes():
    result = parse_transcript("0.0-3.5 | Docker intro\n3.5-9.0 | Compose example")

    assert result[0].start == 0.0
    assert result[0].end == 3.5
    assert result[1].text == "Compose example"
