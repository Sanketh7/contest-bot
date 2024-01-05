import { Client, Collection } from "discord.js";
import fs from "node:fs";
import path from "node:path";
import { Command } from "./types";

export const loadCommands = (client: Client) => {
  client.commands = new Collection();

  const foldersPath = __dirname;
  const commandFolders = fs.readdirSync(foldersPath).filter((name) => !name.includes("."));

  for (const folder of commandFolders) {
    const commandsPath = path.join(foldersPath, folder);
    const commandFiles = fs.readdirSync(commandsPath).filter((file) => file.endsWith(".js"));
    for (const file of commandFiles) {
      const filePath = path.join(commandsPath, file);
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const command: Command = require(filePath).default;
      console.log(`Adding command: ${command.data.name}`);
      client.commands.set(command.data.name, command);
    }
  }
};
