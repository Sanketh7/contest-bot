import { Contest } from "@prisma/client";
import {
  ActionRowBuilder,
  ButtonBuilder,
  EmbedBuilder,
  Message,
  StringSelectMenuBuilder,
  StringSelectMenuInteraction,
  StringSelectMenuOptionBuilder,
  User,
} from "discord.js";
import { CHARACTER_MODIFIERS, DEFAULT_TIMEOUT_MS, ROTMG_CLASSES } from "../constants";
import { buildProcessCustomId } from "../util";
import { Process } from "./process";

type ProcessState = {
  selectedClass?: string;
  selectedModifiers?: string[];
};

export class NewCharacterProcess extends Process {
  private state: ProcessState;

  constructor(user: User, message: Message, contest: Contest) {
    super(user, message, contest);
    this.state = {};
  }

  async start() {
    await this.doSelectClassMenu();
  }

  private async doSelectClassMenu() {
    const menuCustomId = buildProcessCustomId(NewCharacterProcess.name, "selectClassMenu");
    const selectClassMenu = new StringSelectMenuBuilder()
      .setCustomId(menuCustomId)
      .setPlaceholder("Select a class.")
      .setMinValues(1)
      .setMaxValues(1)
      .addOptions(
        ...ROTMG_CLASSES.map((c) => new StringSelectMenuOptionBuilder().setLabel(c).setValue(c))
      );
    const { cancelButton, cancelButtonCustomId } = this.buildCancelButton();

    await this.message.edit({
      content: "Choose your new character's class:",
      components: [
        new ActionRowBuilder<StringSelectMenuBuilder>().addComponents(selectClassMenu),
        new ActionRowBuilder<ButtonBuilder>().addComponents(cancelButton),
      ],
    });

    let response;
    try {
      response = await this.message.awaitMessageComponent({
        filter: (i) =>
          (i.customId === menuCustomId || i.customId === cancelButtonCustomId) &&
          i.user.id === this.user.id,
        time: DEFAULT_TIMEOUT_MS,
      });
      if (response.customId === cancelButtonCustomId) {
        return await this.cancel("button");
      }
      await response.deferUpdate();
    } catch (e) {
      return await this.cancel("timeout");
    }
    this.state.selectedClass = (response as StringSelectMenuInteraction).values[0];
    return await this.doSelectModiferMenu();
  }

  private async doSelectModiferMenu(): Promise<any> {
    const menuCustomId = buildProcessCustomId(NewCharacterProcess.name, "selectModfierMenu");
    const selectModiferMenu = new StringSelectMenuBuilder()
      .setCustomId(menuCustomId)
      .setPlaceholder("Select modifiers (optional).")
      .setMinValues(0)
      .setMaxValues(CHARACTER_MODIFIERS.length)
      .addOptions(
        ...CHARACTER_MODIFIERS.map((m) =>
          new StringSelectMenuOptionBuilder().setLabel(m).setValue(m)
        )
      );
    const { cancelButton, cancelButtonCustomId } = this.buildCancelButton();

    await this.message.edit({
      content: `Choose modifiers for your new ${this.state.selectedClass}. These are **OPTIONAL**:`,
      components: [
        new ActionRowBuilder<StringSelectMenuBuilder>().addComponents(selectModiferMenu),
        new ActionRowBuilder<ButtonBuilder>().addComponents(cancelButton),
      ],
    });

    let response;
    try {
      response = await this.message.awaitMessageComponent({
        filter: (i) =>
          (i.customId === menuCustomId || i.customId === cancelButtonCustomId) &&
          i.user.id === this.user.id,
        time: DEFAULT_TIMEOUT_MS,
      });
      if (response.customId === cancelButtonCustomId) {
        return await this.cancel("button");
      }
      await response.deferUpdate();
    } catch (e) {
      return await this.cancel("timeout");
    }
    this.state.selectedModifiers = (response as StringSelectMenuInteraction).values ?? [];
    return this.doConfirm();
  }

  private async doConfirm() {
    if (this.state.selectedClass === undefined || this.state.selectedModifiers === undefined) {
      return await this.cancel("unknown");
    }
    const { cancelButton, cancelButtonCustomId } = this.buildCancelButton();
    const { confirmButton, confirmButtonCustomId } = this.buildConfirmButton();

    const embed1 = new EmbedBuilder()
      .setColor("Yellow")
      .setTitle("Confirm Character Creation")
      .addFields(
        { name: "Class", value: this.state.selectedClass },
        { name: "Modifiers", value: this.state.selectedModifiers.toString() }
      );
    await this.message.edit({
      content: "",
      embeds: [embed1],
      components: [
        new ActionRowBuilder<ButtonBuilder>().addComponents(confirmButton, cancelButton),
      ],
    });

    let response;
    try {
      response = await this.message.awaitMessageComponent({
        filter: (i) =>
          (i.customId === confirmButtonCustomId || i.customId === cancelButtonCustomId) &&
          i.user.id === this.user.id,
        time: DEFAULT_TIMEOUT_MS,
      });
      if (response.customId === cancelButtonCustomId) {
        return await this.cancel("button");
      }
      await response.deferUpdate();
    } catch (e) {
      return await this.cancel("timeout");
    }

    // TODO: create character
    const embed2 = new EmbedBuilder()
      .setColor("Green")
      .setTitle("Created Character")
      .addFields(
        { name: "Class", value: this.state.selectedClass },
        { name: "Modifiers", value: this.state.selectedModifiers.toString() }
      );
    return await this.message.edit({
      content: "",
      embeds: [embed2],
      components: [],
    });
  }
}
