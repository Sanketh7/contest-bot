import { CacheType, ChatInputCommandInteraction, SlashCommandBuilder } from "discord.js";
import { NewCharacterProcess } from "../processes/newCharacter";
import { SlashCommand } from "../types";

const command: SlashCommand = {
  command: new SlashCommandBuilder().setName("foo").setDescription("foobar"),
  async execute(interaction: ChatInputCommandInteraction<CacheType>) {
    const message = await interaction.user.send({
      content: "Loading...",
    });
    const process = new NewCharacterProcess(interaction.user, message);
    await process.start();
  },
  cooldown: 10,
};

export default command;
