import { CacheType, ChatInputCommandInteraction, SlashCommandBuilder } from "discord.js";
import { buildCharacterEmbed } from "../processes/common";
import { getCharacter } from "../services/characterService";
import { SlashCommand } from "../types";

const command: SlashCommand = {
  defaultAcl: ["Contestant"],
  subcommandAcl: null,
  command: new SlashCommandBuilder()
    .setName("character")
    .setDescription("View full character info.")
    .addNumberOption((option) =>
      option.setName("character-id").setDescription("Character ID.").setRequired(true)
    ),
  async execute(interaction: ChatInputCommandInteraction<CacheType>) {
    const characterId = interaction.options.getNumber("character-id", true);
    const character = await getCharacter(characterId);
    if (!character) {
      return await interaction.reply({
        content: "Character not found.",
      });
    } else {
      return await interaction.reply({
        embeds: [buildCharacterEmbed("Blue", "all", character)],
      });
    }
  },
  cooldown: 10,
};

export default command;
