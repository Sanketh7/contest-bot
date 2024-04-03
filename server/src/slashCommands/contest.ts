import { CacheType, ChatInputCommandInteraction, SlashCommandBuilder } from "discord.js";
import { endContest, getActiveContest, refreshContestPost } from "../services/contestService";
import { SlashCommand, SlashCommandDescriptions } from "../types";

const descriptions = {
  description: "Manage the current contest.",
  subcommands: {
    end: {
      description: "Force-end the current contest.",
    },
    refreshPost: {
      description: "Refresh the contest sign up post.",
    },
  },
} satisfies SlashCommandDescriptions;

const handleContestEnd = async (interaction: ChatInputCommandInteraction) => {
  const contest = await getActiveContest();
  if (!contest) {
    return await interaction.reply({
      ephemeral: true,
      content: "No active contest.",
    });
  }
  await endContest(contest, { force: true });
  return await interaction.reply({
    content: `Ended contest with ID ${contest.id}`,
  });
};

const handleContestRefreshPost = async (interaction: ChatInputCommandInteraction) => {
  const contest = await getActiveContest();
  if (!contest) {
    return await interaction.reply({
      ephemeral: true,
      content: "No active contest.",
    });
  }
  await refreshContestPost(contest);
  return await interaction.reply({
    content: `Refreshed post for contest with ID ${contest.id}`,
  });
};

const command: SlashCommand = {
  defaultAcl: ["Admin"],
  subcommandAcl: {
    end: ["Admin"],
    refresh: ["Admin"],
  },
  descriptions,
  command: new SlashCommandBuilder()
    .setName("contest")
    .setDescription(descriptions.description)
    .addSubcommand((subcommand) =>
      subcommand.setName("end").setDescription(descriptions.subcommands.end.description)
    )
    .addSubcommand((subcommand) =>
      subcommand
        .setName("refresh-post")
        .setDescription(descriptions.subcommands.refreshPost.description)
    ),
  async execute(interaction: ChatInputCommandInteraction<CacheType>) {
    const subcommand = interaction.options.getSubcommand();
    switch (subcommand) {
      case "end":
        return await handleContestEnd(interaction);
      case "refresh-post":
        return await handleContestRefreshPost(interaction);
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
