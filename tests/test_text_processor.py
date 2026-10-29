from app.text_processor import TextProcessor


def test_process():
    processor = TextProcessor()

    result = processor.process("Machine learning is very useful!")

    assert result == ["machin", "learn", "use"]