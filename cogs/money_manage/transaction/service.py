from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Session
from sqlalchemy import DateTime, create_engine, extract
from typing import Optional, List, Literal
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Transaction(Base):
    __tablename__ = "user_money"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int]
    amount: Mapped[float]
    # should be 'income' or 'expense'
    type: Mapped[str]
    description: Mapped[Optional[str]]
    date: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return (
            f"Transaction(id={self.id!r}, user_id={self.user_id!r}, amount={self.amount!r}, "
            f"type={self.type!r}, description={self.description!r})"
        )


class TransactionService:
    def __init__(self) -> None:
        self.engine = create_engine("sqlite:///money.db")
        Base.metadata.create_all(self.engine)

    def create_transaction(
        self, user_id: int, amount: float, type: str, description: Optional[str] = None
    ) -> None:
        with Session(self.engine) as session:
            transaction = Transaction(
                user_id=user_id, amount=amount, type=type, description=description
            )
            session.add(transaction)
            session.commit()

    def get_transaction(self, transaction_id: int) -> Optional[Transaction]:
        with Session(self.engine) as session:
            return session.query(Transaction).filter_by(id=transaction_id).first()

    def delete_transaction(self, transaction_id: int) -> None:
        with Session(self.engine) as session:
            transaction = self.get_transaction(transaction_id)
            if transaction:
                session.delete(transaction)
                session.commit()

    def update_transaction(
        self,
        transaction_id: int,
        amount: Optional[float] = None,
        type: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        with Session(self.engine) as session:
            transaction = self.get_transaction(transaction_id)
            if transaction:
                if amount:
                    transaction.amount = amount
                if type:
                    transaction.type = type
                if description:
                    transaction.description = description
                session.commit()

    def get_transactions(self, user_id: int) -> List[Transaction]:
        with Session(self.engine) as session:
            return session.query(Transaction).filter_by(user_id=user_id).all()

    def get_transactions_by_type(
        self, user_id: int, type: Literal["income", "expense"]
    ) -> List[Transaction]:
        with Session(self.engine) as session:
            return (
                session.query(Transaction).filter_by(user_id=user_id, type=type).all()
            )

    def get_total_by_type(
        self,
        user_id: int,
        type: Literal["income", "expense"] = "income",
        month: Optional[int] = -1,
    ) -> float:
        """
        Calculate the total amount of transactions for a user by type and month.
        Args:
            user_id (int): The ID of the user whose transactions are being queried.
            type (Literal["income", "expense"], optional): The type of transactions to sum. Defaults to "income".
            month (Optional[int], optional): The month for which to calculate the total.
            Defaults to the current month if not specified.
        Returns:
            float: The total amount of the specified type of transactions for the given user and month.
        """

        if month == -1:
            month = datetime.now().month

        with Session(self.engine) as session:
            return sum(
                transaction.amount
                for transaction in session.query(Transaction)
                .filter_by(user_id=user_id, type=type)
                .filter(extract("month", Transaction.date) == month)
                .all()
            )

    def get_balance(self, user_id: int, month: Optional[int] = -1) -> float:
        """
        Calculate the balance for a user by subtracting total expenses from total income.

        Args:
            user_id (int): The ID of the user whose balance is being calculated.
            month (Optional[int]): The month for which the balance is calculated. Defaults to -1, which indicates
            the current month.

        Returns:
            float: The calculated balance for the user.
        """
        return self.get_total_by_type(
            user_id, "income", month
        ) - self.get_total_by_type(user_id, "expense", month)

    def get_top_transactions_by_type(
        self,
        user_id: int,
        type: Literal["income", "expense"],
        month: Optional[int] = -1,
        limit: int = 5,
        order: Literal["asc", "desc"] = "desc",
    ) -> List[Transaction]:
        """
        Retrieve the top transactions of a specified type for a user within a given month.
        Args:
            user_id (int): The ID of the user whose transactions are to be retrieved.
            type (Literal["income", "expense"]): The type of transactions to retrieve, either "income" or "expense".
            month (Optional[int], optional): The month for which to retrieve transactions.
            Defaults to the current month if not specified.
            limit (int, optional): The maximum number of transactions to retrieve. Defaults to 5.
            order (Literal["asc", "desc"], optional): The order in which to sort the transactions by amount. Defaults to "desc" for descending order.
        Returns:
            List[Transaction]: A list of transactions matching the specified criteria.
        """
        if month == -1:
            month = datetime.now().month

        if order == "asc":
            order_by = Transaction.amount.asc()
        else:
            order_by = Transaction.amount.desc()

        with Session(self.engine) as session:
            return (
                session.query(Transaction)
                .filter_by(user_id=user_id, type=type)
                .filter(extract("month", Transaction.date) == month)
                .order_by(order_by)
                .limit(limit)
                .all()
            )

    def clear_transactions(self, user_id: int) -> None:
        with Session(self.engine) as session:
            session.query(Transaction).filter_by(user_id=user_id).delete()
            session.commit()

    def clear_all_transactions(self) -> None:
        with Session(self.engine) as session:
            session.query(Transaction).delete()
            session.commit()
