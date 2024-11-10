from typing import Optional
from discord.ext import commands
from discord import app_commands
import discord
from datetime import datetime

from cogs.money_manage.transaction.service import TransactionService
from cogs.components.discord_embed import Embed


class MoneyManagement(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.transaction_service = TransactionService()

    @app_commands.command(
        name="transaction", description="Add a transaction to your account."
    )
    async def transaction(
        self,
        interaction: discord.Interaction,
        request_amount: str,
        description: Optional[str] = None,
    ) -> None:
        user_id = interaction.user.id
        if request_amount is None:
            await interaction.response.send_message(
                content="Please provide an amount.", ephemeral=True
            )
            return
        try:
            sign = request_amount[0]
            if sign.isdigit():
                amount = float(request_amount)
                type = "income"
            else:
                if sign == "-":
                    amount = float(request_amount[1:])
                    type = "expense"
                else:
                    amount = float(request_amount[1:])
                    type = "income"
        except ValueError:
            await interaction.response.send_message(
                content="Invalid amount provided.", ephemeral=True
            )
            return

        self.transaction_service.create_transaction(user_id, amount, type, description)
        await interaction.response.send_message(
            content="Transaction added successfully.", ephemeral=True
        )

    @app_commands.command(name="summary", description="Show a summary of your account.")
    async def summary(self, interaction: discord.Interaction) -> None:
        user_id = interaction.user.id
        total_income = self.transaction_service.get_total_by_type(user_id, "income")
        total_expense = self.transaction_service.get_total_by_type(user_id, "expense")
        balance = self.transaction_service.get_balance(user_id)
        most_expense = self.transaction_service.get_top_transactions_by_type(
            user_id, "expense"
        )[0]
        most_income = self.transaction_service.get_top_transactions_by_type(
            user_id, "income"
        )[0]

        embed = Embed().summary(
            total_income=total_income,
            total_expense=total_expense,
            balance=balance,
            most_expense=most_expense,
            most_income=most_income,
            month=datetime.now().month,
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)
