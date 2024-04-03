import {
  CacheType,
  ChatInputCommandInteraction,
  EmbedBuilder,
  SlashCommandBuilder,
} from "discord.js";
import { SlashCommand, SlashCommandDescriptions } from "../types";

const descriptions = {
  description: "Get server ping.",
} satisfies SlashCommandDescriptions;

const command: SlashCommand = {
  defaultAcl: [],
  subcommandAcl: null,
  descriptions,
  command: new SlashCommandBuilder().setName("ping").setDescription(descriptions.description),
  async execute(interaction: ChatInputCommandInteraction<CacheType>) {
    await interaction.reply({
      embeds: [
        new EmbedBuilder()
          .setDescription(`Pong! Ping: ${interaction.client.ws.ping}ms`)
          .setColor("Green"),
      ],
    });
  },
  cooldown: 10,
};

export default command;
