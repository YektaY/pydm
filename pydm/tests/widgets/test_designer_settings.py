import pytest

from pydm.widgets.designer_settings import PropertyMacroTable


class FakeWidget:
    """Minimal mock with a macros attribute for PropertyMacroTable tests."""

    def __init__(self, macros):
        self.macros = macros


def _make_table(qtbot, macros_value):
    """Create a PropertyMacroTable backed by a FakeWidget.

    Parameters
    ----------
    qtbot : fixture
        pytest-qt fixture for widget management.
    macros_value : str, list of str, or None
        The macro value to initialize the table with.

    Returns
    -------
    PropertyMacroTable
    """
    widget = FakeWidget(macros=macros_value)
    table = PropertyMacroTable(property_widget=widget, property_name="macros")
    qtbot.addWidget(table)
    return table


def test_macro_table_single_string(qtbot):
    """PropertyMacroTable handles a single JSON string (PyDMEmbeddedDisplay)."""
    table = _make_table(qtbot, '{"top": "FooBar"}')
    assert table.dictionary == {"top": "FooBar"}


def test_macro_table_list_single_element(qtbot):
    """PropertyMacroTable handles a list with one JSON string (PyDMRelatedDisplayButton)."""
    table = _make_table(qtbot, ['{"top": "FooBar"}'])
    assert table.dictionary == {"top": "FooBar"}


def test_macro_table_list_multiple_elements(qtbot):
    """PropertyMacroTable merges multiple macro sets from a list."""
    table = _make_table(qtbot, ['{"a": "1"}', '{"b": "2"}'])
    assert table.dictionary == {"a": "1", "b": "2"}


def test_macro_table_list_with_empty_string(qtbot):
    """PropertyMacroTable handles lists that include empty strings."""
    table = _make_table(qtbot, ['{"top": "FooBar"}', ""])
    assert table.dictionary == {"top": "FooBar"}


def test_macro_table_empty_string(qtbot):
    """PropertyMacroTable handles an empty string gracefully."""
    table = _make_table(qtbot, "")
    assert table.dictionary == {}


def test_macro_table_none(qtbot):
    """PropertyMacroTable handles None gracefully."""
    table = _make_table(qtbot, None)
    assert table.dictionary == {}
