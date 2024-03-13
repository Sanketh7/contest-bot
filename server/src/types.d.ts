import {
  AutocompleteInteraction,
  CacheType,
  ChatInputCommandInteraction,
  Collection,
  ModalSubmitInteraction,
  SlashCommandBuilder,
  SlashCommandSubcommandsOnlyBuilder,
} from "discord.js";
import type {
  JobCallback,
  RecurrenceRule,
  RecurrenceSpecDateRange,
  RecurrenceSpecObjLit,
} from "node-schedule";
import { CHARACTER_MODIFIERS, ROTMG_CLASSES } from "./constants";

export type CommandBuilder =
  | Omit<SlashCommandBuilder, "addSubcommandGroup" | "addSubcommand">
  | SlashCommandSubcommandsOnlyBuilder;

export interface SlashCommand {
  command: CommandBuilder;
  execute: (interaction: ChatInputCommandInteraction) => Promise<any>;
  autocomplete?: (interaction: AutocompleteInteraction) => void;
  modal?: (interaction: ModalSubmitInteraction<CacheType>) => void;
  cooldown?: number; // in seconds
}

export interface Event {
  name: string;
  once?: boolean | false;
  execute: (...args) => Promise<any>;
}

declare module "discord.js" {
  export interface Client {
    slashCommands: Collection<string, SlashCommand>;
    cooldowns: Collection<string, number>;
  }
}

export type RotmgClass = (typeof ROTMG_CLASSES)[number];
export type CharacterModifier = (typeof CHARACTER_MODIFIERS)[number];

export type Job = {
  schedule:
    | RecurrenceRule
    | RecurrenceSpecDateRange
    | RecurrenceSpecObjLit
    | Date
    | string
    | number;
  onTick: JobCallback;
};
