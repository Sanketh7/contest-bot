import { Interaction } from "discord.js";
import {
  handleContestPostButtonInteraction,
  isContestPostButtonInteraction,
} from "../interactions/contestPostButtons";
import {
  handleSubmissionPostButtonInteraction,
  isSubmissionPostButtonInteraction,
} from "../interactions/submissionPostButtons";
import { Event } from "../types";
import { checkAcl, getAcl } from "../util";

const event: Event = {
  name: "interactionCreate",
  async execute(interaction: Interaction) {
    try {
      if (interaction.isChatInputCommand()) {
        const command = interaction.client.slashCommands.get(interaction.commandName);
        if (!command) return;

        // check acl
        const subcommandName = interaction.options.getSubcommand(false);
        const acl = getAcl(command, subcommandName);
        const aclOk = await checkAcl(interaction.user, acl);
        if (!aclOk) {
          return await interaction.reply({
            ephemeral: true,
            content: "Insufficient permissions.",
          });
        }

        await command.execute(interaction).catch(console.error);
      } else if (interaction.isAutocomplete()) {
        const command = interaction.client.slashCommands.get(interaction.commandName);
        if (!command || !command.autocomplete) return;
        await command.autocomplete(interaction);
      } else if (interaction.isModalSubmit()) {
        const command = interaction.client.slashCommands.get(interaction.customId);
        if (!command || !command.modal) return;
        await command.modal(interaction);
      } else if (interaction.isButton()) {
        if (isContestPostButtonInteraction(interaction)) {
          return await handleContestPostButtonInteraction(interaction);
        } else if (isSubmissionPostButtonInteraction(interaction)) {
          return await handleSubmissionPostButtonInteraction(interaction);
        }
      }
    } catch (err) {
      console.error(err);
    }
  },
};

export default event;
