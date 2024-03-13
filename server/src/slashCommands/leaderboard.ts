import { CacheType, ChatInputCommandInteraction, SlashCommandBuilder } from "discord.js";
import { getActiveContest } from "../services/contestService";
import {
  cleanLeaderboardChannel,
  displayTopCharactersLeaderboard,
} from "../services/leaderboardService";
import { SlashCommand } from "../types";

const handleLeaderboardRefresh = async (interaction: ChatInputCommandInteraction) => {
  const contest = await getActiveContest();
  if (!contest) {
    return await interaction.reply({
      ephemeral: true,
      content: "No active contest.",
    });
  }
  await cleanLeaderboardChannel();
  await displayTopCharactersLeaderboard(contest, "all");
  await displayTopCharactersLeaderboard(contest, "active");
  return await interaction.reply({
    content: "Refreshed leaderboard.",
  });
};

const command: SlashCommand = {
  command: new SlashCommandBuilder()
    .setName("leaderboard")
    .setDescription("Manage the leaderboard.")
    .addSubcommand((subcommand) =>
      subcommand
        .setName("refresh")
        .setDescription("Force-refresh the current contest's leaderboard.")
    ),
  async execute(interaction: ChatInputCommandInteraction<CacheType>) {
    const subcommand = interaction.options.getSubcommand();
    switch (subcommand) {
      case "refresh":
        return await handleLeaderboardRefresh(interaction);
      default:
        return await interaction.reply({
          ephemeral: true,
          content: "Invalid subcommand.",
        });
    }
  },
  cooldown: 10,
};

export default command;
