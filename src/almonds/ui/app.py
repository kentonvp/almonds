from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.geometry import Size
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


class Item(Placeholder):
    DEFAULT_CSS = """
    Item {
        height: 2;
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

    def compose(self) -> ComposeResult:
        for i in range(10):
            yield Item(id="budget" + str(i))


class TransactionContainer(Placeholder):
    DEFAULT_CSS = """
    TransactionContainer {
        row-span: 1;
        column-span: 1;
        border: solid white;
    }
    """

    def compose(self) -> ComposeResult:
        for i in range(5):
            yield Item(id="transaction" + str(i))


class SavingsContainer(Placeholder):
    DEFAULT_CSS = """
    SavingsContainer {
        row-span: 1;
        column-span: 2;
        border: solid white;
    }
    """


class HomeScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(id="Header")
        yield Footer(id="Footer")
        yield BudgetContainer(id="Budgets")
        yield TransactionContainer(id="Transactions")
        yield SavingsContainer(id="Savings")


class HelpContainer(Placeholder):
    DEFAULT_CSS = """
    HelpContainer {
        height: 75%;
        width: 75%;
        content-align: center middle;
        background: red 20%;
    }
    """


class HelpScreen(Screen):
    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
        background: rgba(12, 30, 46, 0.5);
    }
    """
    BINDINGS = [
        ("question_mark", "app.pop_screen", "Pop screen"),
        ("escape", "app.pop_screen", "Pop screen"),
    ]

    def compose(self) -> ComposeResult:
        yield HelpContainer(id="Help")


class AlmondsApp(App):
    SCREENS = {"home": HomeScreen(), "help": HelpScreen()}
    BINDINGS = [("question_mark", "push_screen('help')", "Help")]

    def on_mount(self) -> None:
        self.push_screen("home")


if __name__ == "__main__":
    app = AlmondsApp(css_path="app.css")
    app.run()
