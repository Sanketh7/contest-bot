import { Events } from "discord.js";
import * as dotenv from "dotenv";
import { client } from "./client";
import { loadCommands } from "./commands/load-commands";
import { reloadCommands } from "./commands/reload-commands";

dotenv.config();

client.once(Events.ClientReady, (readyClient) => {
  console.log(`${readyClient.user.tag} connected!`);
});

loadCommands(client);

client.on(Events.InteractionCreate, async (interaction) => {
  if (!interaction.isChatInputCommand()) return;

  const command = interaction.client.commands.get(interaction.commandName);
  if (!command) {
    console.error(`Command ${interaction.commandName} not found.`);
    return;
  }

  try {
    await command.execute(interaction);
  } catch (error) {
    console.log(error);
    if (interaction.replied || interaction.deferred) {
      await interaction.followUp({ content: "An error occurred.", ephemeral: true });
    } else {
      await interaction.reply({ content: "An error occurred.", ephemeral: true });
    }
  }
});

client.on(Events.MessageCreate, async (message) => {
  const command = message.content.trim();
  if (command === "+reload guild") {
    if (!message.guildId) {
      message.reply("This command needs to be used in a guild.");
      return;
    }
    await reloadCommands(
      message.guildId,
      message.client.user.id,
      process.env.DISCORD_TOKEN as string
    );
  } else if (command === "+reload global") {
    await reloadCommands(null, message.client.user.id, process.env.DISCORD_TOKEN as string);
  }
});

client.login(process.env.DISCORD_TOKEN);
