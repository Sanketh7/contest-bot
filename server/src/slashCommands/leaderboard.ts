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
import { SlashCommand, SlashCommandDescriptions } from "../types";

const descriptions = {
  description: "Manage the leaderboard.",
  subcommands: {
    download: {
      description: "View the full leaderboard as a txt file.",
      options: {
        contestId: "Optional: Contest ID. Omit to use active contest.",
      },
    },
    refresh: {
      description: "Force-refresh the current contest's leaderboard.",
    },
  },
} satisfies SlashCommandDescriptions;

const handleLeaderboardRefresh = async (interaction: ChatInputCommandInteraction) => {
  await interaction.deferReply({ ephemeral: true });
  await cleanLeaderboardChannel();
  const contest = await getActiveContest();
  if (!contest) {
    return await interaction.editReply({
      content: "No active contest.",
    });
  }
  await displayTopCharactersLeaderboard(contest, "all");
  await displayTopCharactersLeaderboard(contest, "active");
  return await interaction.editReply({
    content: "Refreshed leaderboard.",
  });
};

export const handleLeaderboardDownload = async (interaction: ChatInputCommandInteraction) => {
  await interaction.deferReply({ ephemeral: true });
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
  await interaction.editReply({
    content: messageLink(msg.channelId, msg.id),
  });
};

const command: SlashCommand = {
  defaultAcl: ["Admin"],
  subcommandAcl: {
    refresh: ["Contest Staff"],
    view: ["Contest Staff"],
  },
  descriptions,
  command: new SlashCommandBuilder()
    .setName("leaderboard")
    .setDescription(descriptions.description)
    .addSubcommand((subcommand) =>
      subcommand.setName("refresh").setDescription(descriptions.subcommands.refresh.description)
    )
    .addSubcommand((subcommand) =>
      subcommand
        .setName("download")
        .setDescription(descriptions.subcommands.download.description)
        .addNumberOption((option) =>
          option
            .setName("contest-id")
            .setDescription(descriptions.subcommands.download.options.contestId)
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
