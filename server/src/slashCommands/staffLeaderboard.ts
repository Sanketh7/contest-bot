import { Contest } from "@prisma/client";
import {
  CacheType,
  ChatInputCommandInteraction,
  messageLink,
  SlashCommandBuilder,
} from "discord.js";
import { table } from "table";
import { getActiveContest, getContest } from "../services/contestService";
import { generateTopStaffLeaderboard } from "../services/leaderboardService";
import { SlashCommand, SlashCommandDescriptions } from "../types";

const descriptions = {
  description: "Manage the Staff Leaderboard.",
  subcommands: {
    download: {
      description: "View the full staff leaderboard as a txt file.",
      options: {
        contestId: "Optional: Contest ID. Omit to use active contest.",
      },
    },
    refresh: {
      description: "Force-refresh the current contest's staff leaderboard.",
    },
  },
} satisfies SlashCommandDescriptions;

const handleLeaderboardDownload = async (interaction: ChatInputCommandInteraction) => {
  await interaction.deferReply({ ephemeral: true });
  let contest: Contest;
  const contestIdInput = interaction.options.getNumber("contest-id");
  if (contestIdInput == null) {
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

  const [topTableData] = await Promise.all([generateTopStaffLeaderboard(contest)]);
  const msg = await interaction.user.send({
    content: "Staff Leaderboard:",
    files: [
      {
        attachment: Buffer.from("Top Staff:\n\n" + table(topTableData)),
        name: "top-staff-leaderboard.txt",
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
    download: ["Moderator"],
  },
  descriptions,
  command: new SlashCommandBuilder()
    .setName("staff-leaderboard")
    .setDescription(descriptions.description)
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
