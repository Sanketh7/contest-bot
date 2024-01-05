import { REST, Routes } from "discord.js";
import fs from "node:fs";
import path from "node:path";
import { Command } from "./types";

export const reloadCommands = async (
  guildId: string | null,
  clientId: string,
  discordToken: string
) => {
  const commands = [];
  const foldersPath = __dirname;
  const commandFolders = fs.readdirSync(foldersPath).filter((name) => !name.includes("."));

  for (const folder of commandFolders) {
    const commandsPath = path.join(foldersPath, folder);
    const commandFiles = fs.readdirSync(commandsPath).filter((file) => file.endsWith(".js"));
    for (const file of commandFiles) {
      const filePath = path.join(commandsPath, file);
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const command: Command = require(filePath).default;
      console.log(`Reloading guild commands: found command ${command.data.name}.`);
      commands.push(command.data.toJSON());
    }
  }
  console.log(`Reloading guild commands: found ${commands.length} commands.`);

  const rest = new REST().setToken(discordToken);
  try {
    const data = (await rest.put(
      guildId
        ? Routes.applicationGuildCommands(clientId, guildId)
        : Routes.applicationCommands(clientId),
      { body: commands }
    )) as { length: number };
    console.log(`Reloading guild commands: successfully reloaded ${data.length} commands.`);
  } catch (error) {
    console.log(error);
  }
};
