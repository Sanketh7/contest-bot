import { CacheType, ChatInputCommandInteraction, SlashCommandBuilder } from "discord.js";
import { endContest, getActiveContest } from "../services/contestService";
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

const command: SlashCommand = {
  command: new SlashCommandBuilder()
    .setName("contest")
    .setDescription("Manage the current contest.")
    .addSubcommand((subcommand) =>
      subcommand.setName("end").setDescription("Force-end the current contest.")
    ),
  async execute(interaction: ChatInputCommandInteraction<CacheType>) {
    const subcommand = interaction.options.getSubcommand();
    switch (subcommand) {
      case "end":
        return await handleContestEnd(interaction);
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
