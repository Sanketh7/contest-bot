import { Interaction } from "discord.js";
import { Event } from "../types";

const event: Event = {
  name: "interactionCreate",
  async execute(interaction: Interaction) {
    if (interaction.isChatInputCommand()) {
      const command = interaction.client.slashCommands.get(interaction.commandName);
      if (!command) return;
      await command.execute(interaction).catch(console.error);
    } else if (interaction.isAutocomplete()) {
      const command = interaction.client.slashCommands.get(interaction.commandName);
      if (!command || !command.autocomplete) return;
      await command.autocomplete(interaction);
    } else if (interaction.isModalSubmit()) {
      const command = interaction.client.slashCommands.get(interaction.customId);
      if (!command || !command.modal) return;
      await command.modal(interaction);
    }
  },
};

export default event;
