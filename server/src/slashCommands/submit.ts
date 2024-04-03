import {
  CacheType,
  ChatInputCommandInteraction,
  SlashCommandBuilder,
  messageLink,
} from "discord.js";
import { EditCharacterProcess } from "../processes/editCharacter";
import { getActiveContest } from "../services/contestService";
import { SlashCommand, SlashCommandDescriptions } from "../types";

const descriptions = {
  description: "Edit active character.",
} satisfies SlashCommandDescriptions;

const command: SlashCommand = {
  defaultAcl: ["Contestant"],
  subcommandAcl: null,
  descriptions,
  command: new SlashCommandBuilder().setName("submit").setDescription(descriptions.description),
  async execute(interaction: ChatInputCommandInteraction<CacheType>) {
    const contest = await getActiveContest();
    if (!contest) {
      return await interaction.reply({
        content: "No active contest.",
      });
    }
    const message = await interaction.user.send({
      content: "Loading...",
    });
    await interaction.reply({
      ephemeral: true,
      content: messageLink(message.channel.id, message.id),
    });
    const process = new EditCharacterProcess(interaction.user, message, contest);
    await process.start();
  },
  cooldown: 10,
};

export default command;
