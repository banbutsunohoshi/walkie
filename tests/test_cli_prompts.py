from cli.prompts import WalkPrompter


def test_prompt_walk_type_retries_until_valid(monkeypatch):
    inputs = iter(["0", "2"])
    messages: list[str] = []

    prompter = WalkPrompter(
        input_func=lambda _: next(inputs),
        display_func=lambda message: messages.append(message),
    )

    result = prompter.prompt_walk_type()

    assert result == "pair"
    assert "Некорректный выбор" in messages[-1]


def test_prompt_text_requires_value(monkeypatch):
    inputs = iter(["", "hello"])
    messages: list[str] = []

    prompter = WalkPrompter(
        input_func=lambda _: next(inputs),
        display_func=lambda message: messages.append(message),
    )

    result = prompter.prompt_text("Prompt: ")

    assert result == "hello"
    assert "Введите непустое значение." in messages


def test_prompt_time_requires_positive(monkeypatch):
    inputs = iter(["0", "-2", "abc", "15"])
    messages: list[str] = []

    prompter = WalkPrompter(
        input_func=lambda _: next(inputs),
        display_func=lambda message: messages.append(message),
    )

    result = prompter.prompt_time()

    assert result == 15
    assert messages.count("Введите положительное число минут.") == 3


def test_collect_walk_params(monkeypatch):
    inputs = iter(["1", "calm", "relax", "30"])

    prompter = WalkPrompter(
        input_func=lambda _: next(inputs),
        display_func=lambda _: None,
    )

    params = prompter.collect_walk_params()

    assert params.walk_type == "solo"
    assert params.mood == "calm"
    assert params.goal == "relax"
    assert params.time_limit == 30
