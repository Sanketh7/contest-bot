import {
  CacheType,
  ChatInputCommandInteraction,
  SlashCommandBuilder,
  User,
  channelMention,
  userMention,
} from "discord.js";
import { buildCharacterEmbed } from "../processes/common";
import { getCharacter, getCharactersByUserId } from "../services/characterService";
import { getActiveContest } from "../services/contestService";
import { SlashCommand } from "../types";

const handleProfile = async (interaction: ChatInputCommandInteraction, user: User) => {
  const contest = await getActiveContest();
  if (!contest) {
    return await interaction.reply({
      ephemeral: true,
      content: "No active contest.",
    });
  }

  const characters = await getCharactersByUserId(user.id, contest);
  const headerMsg = await interaction.user.send({
    content: `${userMention(user.id)}'s Characters:`,
  });
  for (const c of characters) {
    await headerMsg.reply({
      embeds: [buildCharacterEmbed("Blue", "truncate", c)],
    });
  }
  await interaction.reply({
    ephemeral: true,
    content: channelMention(headerMsg.channelId),
  });
};

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
