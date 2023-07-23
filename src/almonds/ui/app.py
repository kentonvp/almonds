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
        row-span: 3;
        column-span: 1;
    }
    """

    def compose(self) -> ComposeResult:
        for i in range(10):
            yield Item(id="budget" + str(i))


class TransactionContainer(Placeholder):
    DEFAULT_CSS = """
    TransactionContainer {
        row-span: 3;
        column-span: 1;
    }
    """

    def compose(self) -> ComposeResult:
        for i in range(5):
            yield Item(id="transaction" + str(i))


class SavingsContainer(Placeholder):
    DEFAULT_CSS = """
    SavingsContainer {
        row-span: 2;
        column-span: 2;
    }
    """


class HomeScreen(Screen):
    def __init__(self):
        super().__init__()
        self._focus_index = 0
        self._cycle_order = ['Budgets', 'Transactions', 'Savings']

    def compose(self) -> ComposeResult:
        yield Header(id="Header")
        yield Footer(id="Footer")
        yield BudgetContainer(id="Budgets")
        yield TransactionContainer(id="Transactions")
        yield SavingsContainer(id="Savings")

    def on_mount(self) -> None:
        self.border_focus()

    def border_focus(self) -> None:
        for i, id_name in enumerate(self._cycle_order):
            if i == self._focus_index:
                self.query_one(f"#{id_name}").styles.border = ("solid", "white")
            else:
                self.query_one(f"#{id_name}").styles.border = None

    def rotate_focus_right(self):
        self._focus_index = (self._focus_index + 1) % len(self._cycle_order)
        print(f"Rotate focus: {self._cycle_order[self._focus_index]}")
        self.border_focus()

    def rotate_focus_left(self):
        self._focus_index = (self._focus_index - 1) % len(self._cycle_order)
        print(f"Rotate focus: {self._cycle_order[self._focus_index]}")
        self.border_focus()

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


class NewTransactionContainer(Placeholder):
    DEFAULT_CSS = """
    NewTransactionContainer {
        height: 4;
        width: 60%;
        content-align: center middle;
        background: red 20%;
    }
    """

class NewTransactionScreen(Screen[bool]):
    DEFAULT_CSS = """
    NewTransactionScreen {
        align: center middle;
        background: rgba(12, 30, 46, 0.5);
    }
    """
    BINDINGS = [
        ("escape", "cancel_transaction", "Pop screen"),
        ("enter", "add_transaction", "Add transaction item"),
    ]
    def compose(self) -> ComposeResult:
        yield NewTransactionContainer(id="NewTransaction")

    def action_cancel_transaction(self) -> None:
        self.dismiss(False)

    def action_add_transaction(self) -> None:
        print("Add transaction item")
        self.dismiss(True)


class NewBudgetContainer(Placeholder):
    DEFAULT_CSS = """
    NewBudgetContainer {
        height: 4;
        width: 60%;
        content-align: center middle;
        background: red 20%;
    }
    """

class NewBudgetScreen(Screen[bool]):
    DEFAULT_CSS = """
    NewBudgetScreen {
        align: center middle;
        background: rgba(12, 30, 46, 0.5);
    }
    """
    BINDINGS = [
        ("escape", "cancel_budget", "Pop screen"),
        ("enter", "add_budget", "Add budget item"),
    ]
    def compose(self) -> ComposeResult:
        yield NewBudgetContainer(id="NewBudget")

    def action_cancel_budget(self) -> None:
        self.dismiss(False)

    def action_add_budget(self) -> None:
        print("Add budget item")
        self.dismiss(True)


class AlmondsApp(App):
    SCREENS = {
        "home": HomeScreen(),
        "help": HelpScreen(),
        'new_transaction': NewTransactionScreen(),
        'new_budget': NewBudgetScreen()
    }
    BINDINGS = [
        ("question_mark", "display_help", "Help"),
        ("t", "new_transaction", "Add a transaction"),
        ("b", "new_budget", "Add a budget category"),
        ("h", "cycle_left", "Cycle left"),
        ("l", "cycle_right", "Cycle right"),
        ("a", "add_focused", "Add focused"),
    ]

    def on_mount(self) -> None:
        self.push_screen("home")

    def action_display_help(self) -> None:
        self.push_screen("help")

    def action_new_transaction(self) -> None:
        def process_result(result) -> None:
            print(f"Process transaction: {result}")
        self.push_screen("new_transaction", process_result)

    def action_new_budget(self) -> None:
        def process_result(result) -> None:
            print(f"Process budget: {result}")
        self.push_screen("new_budget", process_result)

    def action_add_focused(self) -> None:
        if self.SCREENS['home']._focus_index == 0:
            self.action_new_budget()
        elif self.SCREENS['home']._focus_index == 1:
            self.action_new_transaction()
        else:
            print("Add savings not implemented")

    def action_cycle_left(self) -> None:
        self.SCREENS['home'].rotate_focus_left()

    def action_cycle_right(self) -> None:
        self.SCREENS['home'].rotate_focus_right()


if __name__ == "__main__":
    app = AlmondsApp(css_path="app.css")
    app.run()
