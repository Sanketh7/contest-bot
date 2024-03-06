"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const fs_1 = require("fs");
const path_1 = require("path");
module.exports = (client) => {
  const slashCommands = [];
  const slashCommandsDir = (0, path_1.join)(__dirname, "../slashCommands");
  (0, fs_1.readdirSync)(slashCommandsDir).forEach((file) => {
    if (file.endsWith(".js")) {
      const command = require(`${slashCommandsDir}/${file}`).default;
      slashCommands.push(command.command);
      client.slashCommands.set(command.command.name, command);
    }
  });
  // const rest = new REST().setToken(ENV.DISCORD_TOKEN);
  // rest
  //   .put(Routes.applicationCommands(client.user!.id), {
  //     body: slashCommands.map((command) => command.toJSON()),
  //   })
  //   .then((data: any) => {
  //     console.log(`Loaded ${data.length} slash commands.`);
  //   })
  //   .catch((err) => {
  //     console.error(err);
  //   });
};
