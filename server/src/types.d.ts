import {
  AutocompleteInteraction,
  CacheType,
  ChatInputCommandInteraction,
  Collection,
  ModalSubmitInteraction,
  SlashCommandBuilder,
} from "discord.js";

export interface SlashCommand {
  command: SlashCommandBuilder;
  execute: (interaction: ChatInputCommandInteraction) => Promise<void>;
  autocomplete?: (interaction: AutocompleteInteraction) => void;
  modal?: (interaction: ModalSubmitInteraction<CacheType>) => void;
  cooldown?: number; // in seconds
}

export interface Event {
  name: string;
  once?: boolean | false;
  execute: (...args) => Promise<void>;
}

declare module "discord.js" {
  export interface Client {
    slashCommands: Collection<string, SlashCommand>;
    cooldowns: Collection<string, number>;
  }
}

export type RotmgClass = (typeof ROTMG_CLASSES)[number];
