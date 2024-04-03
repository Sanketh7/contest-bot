import { CacheType, ChatInputCommandInteraction, SlashCommandBuilder } from "discord.js";
import { getBorderCharacters, table } from "table";
import { SlashCommand, SlashCommandDescriptions } from "../types";

const descriptions = {
  description: "Get a list of all commands.",
} satisfies SlashCommandDescriptions;

const command: SlashCommand = {
  defaultAcl: [],
  subcommandAcl: null,
  descriptions,
  command: new SlashCommandBuilder().setName("help").setDescription(descriptions.description),
  async execute(interaction: ChatInputCommandInteraction<CacheType>) {
    const tableData: string[][] = [];
    for (const slashCommand of interaction.client.slashCommands) {
      const baseCommand = slashCommand[1].command.name;
      const descriptions = slashCommand[1].descriptions;
      if ("subcommands" in descriptions) {
        for (const subcommand of Object.keys(descriptions.subcommands)) {
          tableData.push([
            `/${baseCommand} ${subcommand}`,
            descriptions.subcommands[subcommand].description,
          ]);
        }
      } else {
        tableData.push([`/${baseCommand}`, descriptions.description]);
      }
    }
    const tableStr = table(tableData, {
      border: getBorderCharacters("void"),
      columnDefault: {
        paddingLeft: 0,
        paddingRight: 1,
      },
      drawHorizontalLine: () => false,
    });
    return await interaction.reply({
      content: "```" + tableStr + "```",
    });
  },
  cooldown: 10,
};

export default command;
