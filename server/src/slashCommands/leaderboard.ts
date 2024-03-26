import { Contest } from "@prisma/client";
import {
  CacheType,
  ChatInputCommandInteraction,
  SlashCommandBuilder,
  messageLink,
} from "discord.js";
import { table } from "table";
import { getActiveContest, getContest } from "../services/contestService";
import {
  cleanLeaderboardChannel,
  displayTopCharactersLeaderboard,
  generateTopCharactersLeaderboard,
} from "../services/leaderboardService";
import { SlashCommand } from "../types";

const handleLeaderboardRefresh = async (interaction: ChatInputCommandInteraction) => {
  await cleanLeaderboardChannel();
  const contest = await getActiveContest();
  if (!contest) {
    return await interaction.reply({
      ephemeral: true,
      content: "No active contest.",
    });
  }
  await displayTopCharactersLeaderboard(contest, "all");
  await displayTopCharactersLeaderboard(contest, "active");
  return await interaction.reply({
    content: "Refreshed leaderboard.",
  });
};

export const handleLeaderboardDownload = async (interaction: ChatInputCommandInteraction) => {
  let contest: Contest;
  const contestIdInput = interaction.options.getNumber("contest-id");
  if (contestIdInput === null) {
    const activeContest = await getActiveContest();
    if (!activeContest) {
      return await interaction.reply({
        ephemeral: true,
        content: "No active contest.",
      });
    }
    contest = activeContest;
  } else {
    const maybeContest = await getContest(contestIdInput);
    if (!maybeContest) {
      return await interaction.reply({
        ephemeral: true,
        content: "Invalid contest.",
      });
    }
    contest = maybeContest;
  }

  const [activeTableData, allTableData, topTableData] = await Promise.all([
    generateTopCharactersLeaderboard(contest, "active", "inf"),
    generateTopCharactersLeaderboard(contest, "all", "inf"),
    generateTopCharactersLeaderboard(contest, "top", "inf"),
  ]);
  const msg = await interaction.user.send({
    content: "Leaderboards:",
    files: [
      {
        attachment: Buffer.from("Active Characters Only:\n\n" + table(activeTableData)),
        name: "active-leaderboard.txt",
      },
      {
        attachment: Buffer.from("All Characters:\n\n" + table(allTableData)),
        name: "leaderboard.txt",
      },
      {
        attachment: Buffer.from("Top Character per User Only:\n\n" + table(topTableData)),
        name: "top-leaderboard.txt",
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
      subcommand
        .setName("download")
        .setDescription("View the full leaderboard as a txt file.")
        .addNumberOption((option) =>
          option
            .setName("contest-id")
            .setDescription("Optional: Contest ID. Omit to use active contest.")
            .setRequired(false)
        )
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
