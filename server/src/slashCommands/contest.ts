import { CacheType, ChatInputCommandInteraction, SlashCommandBuilder } from "discord.js";
import { endContest, getActiveContest, refreshContestPost } from "../services/contestService";
import { SlashCommand } from "../types";

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

const handleContestRefresh = async (interaction: ChatInputCommandInteraction) => {
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
  command: new SlashCommandBuilder()
    .setName("contest")
    .setDescription("Manage the current contest.")
    .addSubcommand((subcommand) =>
      subcommand.setName("end").setDescription("Force-end the current contest.")
    )
    .addSubcommand((subcommand) =>
      subcommand.setName("refresh").setDescription("Refresh the contest sign up post.")
    ),
  async execute(interaction: ChatInputCommandInteraction<CacheType>) {
    const subcommand = interaction.options.getSubcommand();
    switch (subcommand) {
      case "end":
        return await handleContestEnd(interaction);
      case "refresh":
        return await handleContestRefresh(interaction);
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
