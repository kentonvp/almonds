from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Placeholder


class Header(Placeholder):
    DEFAULT_CSS = """
    Header {
        height: 3;
        dock: top;
    }
    """


class Footer(Placeholder):
    DEFAULT_CSS = """
    Footer {
        height: 1;
        dock: bottom;
    }
    """

class BudgetContainer(Placeholder):
    DEFAULT_CSS = """
    BudgetContainer {
        row-span: 1;
        column-span: 1;
        border: solid white;
    }
    """

class TransactionContainer(Placeholder):
    DEFAULT_CSS = """
    TransactionContainer {
        row-span: 1;
        column-span: 1;
        border: solid white;
    }
    """


class SavingsContainer(Placeholder):
    DEFAULT_CSS = """
    SavingsContainer {
        row-span: 1;
        column-span: 2;
        border: solid white;
    }
    """


class AlmondsScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(id="Header")
        yield Footer(id="Footer")
        yield BudgetContainer(id="Budgets")
        yield TransactionContainer(id="Transactions")
        yield SavingsContainer(id="Savings")


class AlmondsApp(App):
    def on_mount(self) -> None:
        self.push_screen(AlmondsScreen())


if __name__ == "__main__":
    app = AlmondsApp(css_path="app.css")
    app.run()
