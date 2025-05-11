import functions.generate_numbers.app as app

def test_generate_numbers_returns_10_numbers():
    result = app.lambda_handler({"name1": "Alice", "name2": "Bob"}, {})
    assert "numbers" in result
    assert result["numbers"] == list(range(10))
