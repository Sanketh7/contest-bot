import {
  CacheType,
  ChatInputCommandInteraction,
  SlashCommandBuilder,
  messageLink,
} from "discord.js";
import { AddRemoveKeywordsProcess } from "../processes/addRemoveKeywords";
import { getCharacter } from "../services/characterService";
import { SlashCommand } from "../types";

const handleKeywordsAddRemove = async (
  interaction: ChatInputCommandInteraction,
  action: "add" | "remove"
) => {
  const characterId = interaction.options.getNumber("character-id", true);
  const character = await getCharacter(characterId);
  if (!character) {
    return await interaction.reply({
      content: "Character not found.",
    });
  }

  const message = await interaction.user.send({
    content: "Loading...",
  });
  await interaction.reply({
    content: messageLink(message.channel.id, message.id),
  });
  const process = new AddRemoveKeywordsProcess(interaction.user, message, character, action);
  return await process.start();
};

const command: SlashCommand = {
  defaultAcl: ["Admin"],
  subcommandAcl: {
    add: ["Contest Staff"],
    remove: ["Contest Staff"],
  },
  command: new SlashCommandBuilder()
    .setName("keywords")
    .setDescription("Manage the current contest.")
    .addSubcommand((subcommand) =>
      subcommand
        .setName("add")
        .setDescription("Add keywords to a character.")
        .addNumberOption((option) =>
          option.setName("character-id").setDescription("Character ID").setRequired(true)
        )
    )
    .addSubcommand((subcommand) =>
      subcommand
        .setName("remove")
        .setDescription("Remove keywords from a character.")
        .addNumberOption((option) =>
          option.setName("character-id").setDescription("Character ID").setRequired(true)
        )
    ),
  async execute(interaction: ChatInputCommandInteraction<CacheType>) {
    const subcommand = interaction.options.getSubcommand();
    switch (subcommand) {
      case "add":
        return await handleKeywordsAddRemove(interaction, "add");
      case "remove":
        return await handleKeywordsAddRemove(interaction, "remove");
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
