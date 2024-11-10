import discord
from typing import List, Callable

from cogs.music.core.song import SongMeta


class MusicView(discord.ui.View):
    def __init__(self, tracks: List[SongMeta], callback: Callable, timeout: int = 60):
        super().__init__(timeout=timeout)
        self.tracks = tracks
        self.callback = callback
        self.current_page = 0
        self.tracks_per_page = 5
        self.total_pages = (len(tracks) - 1) // self.tracks_per_page + 1

        # Add selection buttons for each track on the page
        self.update_buttons()

    def create_embed(self) -> discord.Embed:
        start_idx = self.current_page * self.tracks_per_page
        end_idx = min(start_idx + self.tracks_per_page, len(self.tracks))
        current_tracks = self.tracks[start_idx:end_idx]

        embed = discord.Embed(
            title="Search Results",
            description="Select a track to play:",
            color=discord.Color.blue(),
        )

        for idx, track in enumerate(current_tracks, start=1):
            duration = track.duration or "??:??"
            title = track.title or "Unknown"
            author = track.author or "Unknown"
            embed.add_field(
                name=f"{idx}. {title}",
                value=f"By: {author} | Duration: {duration}",
                inline=False,
            )

        embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages}")
        return embed

    def update_buttons(self):
        # Clear all existing items
        self.clear_items()

        # Add navigation buttons
        self.add_item(self.previous_button)
        self.add_item(self.next_button)

        # Add selection buttons for current page
        start_idx = self.current_page * self.tracks_per_page
        end_idx = min(start_idx + self.tracks_per_page, len(self.tracks))

        for i in range(start_idx, end_idx):
            button = discord.ui.Button(
                style=discord.ButtonStyle.green,
                label=str(i - start_idx + 1),
                custom_id=f"select_{i}",
                row=1
            )
            button.callback = lambda interaction, track_idx=i: self.select_track(
                interaction, track_idx
            )
            self.add_item(button)

    async def select_track(self, interaction: discord.Interaction, track_idx: int):
        selected_track = self.tracks[track_idx]
        await interaction.response.defer()  # Acknowledge the interaction
        await self.callback(
            interaction, selected_track
        )  # Call the provided callback with the selected track
        self.stop()  # Stop listening for further interactions

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.grey, row=0)
    async def previous_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            await interaction.response.edit_message(
                embed=self.create_embed(), view=self
            )
        else:
            await interaction.response.defer()

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.grey, row=0)
    async def next_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_buttons()
            await interaction.response.edit_message(
                embed=self.create_embed(), view=self
            )
        else:
            await interaction.response.defer()
