import { Client, REST, Routes } from "discord.js";
import { readdirSync } from "fs";
import { join } from "path";
import { ENV } from "../env";
import { CommandBuilder, SlashCommand } from "../types";

module.exports = (client: Client) => {
  const slashCommands: CommandBuilder[] = [];
  const slashCommandsDir = join(__dirname, "../slashCommands");
  readdirSync(slashCommandsDir).forEach((file) => {
    if (file.endsWith(".js")) {
      const command: SlashCommand = require(`${slashCommandsDir}/${file}`).default;
      slashCommands.push(command.command);
      client.slashCommands.set(command.command.name, command);
    }
  });

  if (ENV.RELOAD_SLASH_COMMANDS) {
    const rest = new REST().setToken(ENV.DISCORD_TOKEN);
    rest
      .put(Routes.applicationCommands(client.user!.id), {
        body: slashCommands.map((command) => command.toJSON()),
      })
      .then((data: any) => {
        console.log(`Loaded ${data.length} slash commands.`);
      })
      .catch((err) => {
        console.error(err);
      });
  }
};
