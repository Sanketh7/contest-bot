import {
  CacheType,
  ChatInputCommandInteraction,
  SlashCommandBuilder,
  messageLink,
} from "discord.js";
import { table } from "table";
import { getActiveContest } from "../services/contestService";
import {
  cleanLeaderboardChannel,
  displayTopCharactersLeaderboard,
  generateTopCharactersLeaderboard,
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

export const handleLeaderboardDownload = async (interaction: ChatInputCommandInteraction) => {
  const contest = await getActiveContest();
  if (!contest) {
    return await interaction.reply({
      ephemeral: true,
      content: "No active contest.",
    });
  }

  const [activeTableData, allTableData] = await Promise.all([
    generateTopCharactersLeaderboard(contest, "active", "inf"),
    generateTopCharactersLeaderboard(contest, "all", "inf"),
  ]);
  const msg = await interaction.user.send({
    content: "Leaderboards:",
    files: [
      {
        attachment: Buffer.from(table(activeTableData)),
        name: "active-leaderboard.txt",
      },
      {
        attachment: Buffer.from(table(allTableData)),
        name: "leaderboard.txt",
      },
    ],
  });
  await interaction.reply({
    ephemeral: true,
    content: messageLink(msg.channelId, msg.id),
  });
};

const command: SlashCommand = {
  defaultAcl: ["Admin"],
  subcommandAcl: {
    refresh: ["Contest Staff"],
    view: ["Contest Staff"],
  },
  command: new SlashCommandBuilder()
    .setName("leaderboard")
    .setDescription("Manage the leaderboard.")
    .addSubcommand((subcommand) =>
      subcommand
        .setName("refresh")
        .setDescription("Force-refresh the current contest's leaderboard.")
    )
    .addSubcommand((subcommand) =>
      subcommand.setName("download").setDescription("View the full leaderboard as a txt file.")
    ),
  async execute(interaction: ChatInputCommandInteraction<CacheType>) {
    const subcommand = interaction.options.getSubcommand();
    switch (subcommand) {
      case "refresh":
        return await handleLeaderboardRefresh(interaction);
      case "download":
        return await handleLeaderboardDownload(interaction);
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
