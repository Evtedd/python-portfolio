from app.core.template import render_value


def test_template_renders_nested_context() -> None:
    value = {"text": "Новый товар {{event.name}} за {{event.price}}"}

    rendered = render_value(value, {"event": {"name": "Сумка", "price": 4200}})

    assert rendered["text"] == "Новый товар Сумка за 4200"
