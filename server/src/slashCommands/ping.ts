import {
  CacheType,
  ChatInputCommandInteraction,
  EmbedBuilder,
  SlashCommandBuilder,
} from "discord.js";
import { SlashCommand } from "../types";

const command: SlashCommand = {
  command: new SlashCommandBuilder().setName("ping").setDescription("Get server ping."),
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
