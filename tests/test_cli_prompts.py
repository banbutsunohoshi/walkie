from cli import prompts


def test_prompt_walk_type_retries_until_valid(monkeypatch):
    inputs = iter(["0", "2"])
    messages: list[str] = []

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(prompts, "display_message", lambda message: messages.append(message))

    result = prompts._prompt_walk_type()

    assert result == "pair"
    assert "Некорректный выбор" in messages[-1]


def test_prompt_text_requires_value(monkeypatch):
    inputs = iter(["", "hello"])
    messages: list[str] = []

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(prompts, "display_message", lambda message: messages.append(message))

    result = prompts._prompt_text("Prompt: ")

    assert result == "hello"
    assert "Введите непустое значение." in messages


def test_prompt_time_requires_positive(monkeypatch):
    inputs = iter(["0", "-2", "abc", "15"])
    messages: list[str] = []

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(prompts, "display_message", lambda message: messages.append(message))

    result = prompts._prompt_time()

    assert result == 15
    assert messages.count("Введите положительное число минут.") == 3


def test_collect_walk_params(monkeypatch):
    inputs = iter(["1", "calm", "relax", "30"])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(prompts, "display_message", lambda _: None)

    params = prompts.collect_walk_params()

    assert params.walk_type == "solo"
    assert params.mood == "calm"
    assert params.goal == "relax"
    assert params.time_limit == 30
