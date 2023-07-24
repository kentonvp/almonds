from rich.console import RenderableType
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Placeholder, Pretty, Static

import datetime

from dataclasses import dataclass


@dataclass
class Transaction:
    id: int
    purchase_date: datetime.datetime
    description: str
    amount: float


transactions: list[Transaction] = []


class TransactionHeader(Static):
    DEFAULT_CSS = """
    TransactionHeader {
        height: 3;
        content-align: center middle;
    }
    """

    def on_mount(self) -> None:
        self.update("Purchase Date - Description - Amount")


class TransactionItem(Static):
    DEFAULT_CSS = """
    TransactionItem {
        height: 2;
        content-align: center middle;
    }
    """

    def __init__(self, transaction: Transaction, **kwargs):
        super().__init__(**kwargs)
        self.update(
            f"{datetime.datetime.strftime(transaction.purchase_date, '%Y-%m-%d %H:%M')} - {transaction.description} - {transaction.amount:>.2f}"
        )


class TransactionContainer(Static):
    DEFAULT_CSS = """
    TransactionContainer {
        row-span: 3;
        column-span: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield TransactionHeader()
        for i, txn in enumerate(self.get_transactions()):
            yield TransactionItem(txn, id="transaction" + str(i))

    def get_transactions(self) -> list[Transaction]:
        # TODO:
        return []


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
        ("escape", "cancel_transaction", "Cancel"),
        ("enter", "add_transaction", "Add transaction"),
    ]

    i = reactive(0)

    def compose(self) -> ComposeResult:
        yield NewTransactionContainer(id="NewTransaction")

    def action_cancel_transaction(self) -> None:
        self.dismiss()

    def action_add_transaction(self) -> None:
        print("Add transaction item")
        self.dismiss(
            Transaction(
                self.i, datetime.datetime.now(), f"Something#{self.i}", 10.0 * self.i
            )
        )
