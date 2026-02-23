import { Character, Contest } from "@prisma/client";
import {
  ActionRowBuilder,
  ButtonBuilder,
  ButtonStyle,
  EmbedBuilder,
  Message,
  StringSelectMenuBuilder,
  StringSelectMenuInteraction,
  StringSelectMenuOptionBuilder,
  User,
} from "discord.js";
import { CHARACTER_MODIFIERS, DEFAULT_TIMEOUT_MS, ROTMG_SELECTABLE_CLASSES } from "../constants";
import {
  createCharacter,
  getActiveCharacterByUserId,
  updateCharacterActivity,
} from "../services/characterService";
import { CharacterModifier, RotmgClass } from "../types";
import {
  buildProcessCustomId,
  formatKeywordsForDisplay,
  formatModifierChoiceForDisplay,
} from "../util";
import { buildCharacterEmbed } from "./common";
import { Process } from "./process";

type ProcessState = {
  selectedClass?: RotmgClass;
  selectedModifiers?: CharacterModifier[];
};

export class NewCharacterProcess extends Process<Contest> {
  private state: ProcessState;
  private oldCharacter?: Character;

  constructor(user: User, message: Message, contest: Contest) {
    super(user, message, contest);
    this.state = {};
  }

  async start() {
    this.oldCharacter = (await getActiveCharacterByUserId(this.user.id, this.contest)) ?? undefined;
    if (this.oldCharacter) {
      return await this.doConfirmOldCharacterMenu(this.oldCharacter);
    } else {
      return await this.doSelectClassMenu();
    }
  }

  private async doConfirmOldCharacterMenu(oldCharacter: Character) {
    const embed = new EmbedBuilder()
      .setColor("Yellow")
      .setTitle("Confirm Ending Current Character")
      .addFields({
        name: "Instructions",
        value:
          "Creating a new character will end your current character (shown below), preventing you from adding new items to this character.",
      });

    const characterEmbed = buildCharacterEmbed("Yellow", "truncate", oldCharacter);
    const { confirmButton, confirmButtonCustomId } = this.buildConfirmButton();
    const { cancelButton, cancelButtonCustomId } = this.buildCancelButton();
    confirmButton.setLabel("End Current Character");

    await this.message.edit({
      content: "",
      embeds: [embed, characterEmbed],
      components: [
        new ActionRowBuilder<ButtonBuilder>().addComponents(confirmButton, cancelButton),
      ],
    });

    try {
      const response = await this.message.awaitMessageComponent({
        filter: (i) =>
          (i.customId === confirmButtonCustomId || i.customId === cancelButtonCustomId) &&
          i.user.id === this.user.id,
        time: DEFAULT_TIMEOUT_MS,
      });
      if (response.customId === cancelButtonCustomId) {
        return await this.cancel("button");
      }
      await response.deferUpdate();
    } catch (err) {
      return await this.cancel("timeout");
    }
    return await this.doSelectClassMenu();
  }

  private async doSelectClassMenu() {
    const menuCustomId = buildProcessCustomId(NewCharacterProcess.name, "selectClassMenu");
    const selectClassMenu = new StringSelectMenuBuilder()
      .setCustomId(menuCustomId)
      .setPlaceholder("Select a class.")
      .setMinValues(1)
      .setMaxValues(1)
      .addOptions(
        // ...ROTMG_CLASSES.map((c) => new StringSelectMenuOptionBuilder().setLabel(c).setValue(c))
        ...ROTMG_SELECTABLE_CLASSES.map((c) => new StringSelectMenuOptionBuilder().setLabel(c).setValue(c))
      );
    const { cancelButton, cancelButtonCustomId } = this.buildCancelButton();

    await this.message.edit({
      content: "Choose your new character's class:",
      embeds: [],
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
    this.state.selectedClass = (response as StringSelectMenuInteraction).values[0] as RotmgClass;
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
          new StringSelectMenuOptionBuilder()
            .setLabel(formatModifierChoiceForDisplay(m))
            .setValue(m)
        )
      );
    const { cancelButton, cancelButtonCustomId } = this.buildCancelButton();
    const noModsButtonCustomId = buildProcessCustomId(NewCharacterProcess.name, "noModsButton");
    const noModsButton = new ButtonBuilder()
      .setCustomId(noModsButtonCustomId)
      .setStyle(ButtonStyle.Primary)
      .setLabel("No Modifiers");

    await this.message.edit({
      content: `Choose modifiers for your new ${this.state.selectedClass}. These are **OPTIONAL**:`,
      embeds: [],
      components: [
        new ActionRowBuilder<StringSelectMenuBuilder>().addComponents(selectModiferMenu),
        new ActionRowBuilder<ButtonBuilder>().addComponents(noModsButton, cancelButton),
      ],
    });

    let response;
    let noModsSelected: boolean = false;
    try {
      response = await this.message.awaitMessageComponent({
        filter: (i) =>
          (i.customId === menuCustomId ||
            i.customId === cancelButtonCustomId ||
            i.customId === noModsButtonCustomId) &&
          i.user.id === this.user.id,
        time: DEFAULT_TIMEOUT_MS,
      });
      if (response.customId === cancelButtonCustomId) {
        return await this.cancel("button");
      } else if (response.customId === noModsButtonCustomId) {
        noModsSelected = true;
      }
      await response.deferUpdate();
    } catch (e) {
      return await this.cancel("timeout");
    }
    if (noModsSelected) {
      this.state.selectedModifiers = [];
    } else {
      this.state.selectedModifiers =
        ((response as StringSelectMenuInteraction).values as CharacterModifier[]) ?? [];
    }
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
        { name: "Class", value: this.state.selectedClass.toString() },
        { name: "Modifiers", value: formatKeywordsForDisplay(this.state.selectedModifiers) }
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

    if (this.oldCharacter) {
      await updateCharacterActivity(this.oldCharacter, false);
    }
    await createCharacter(this.user.id, this.contest, {
      isActive: true,
      rotmgClass: this.state.selectedClass,
      modifiers: this.state.selectedModifiers,
    });

    const embed2 = new EmbedBuilder()
      .setColor("Green")
      .setTitle("Created Character")
      .addFields(
        { name: "Class", value: this.state.selectedClass.toString() },
        { name: "Modifiers", value: formatKeywordsForDisplay(this.state.selectedModifiers) }
      );
    return await this.message.edit({
      content: "",
      embeds: [embed2],
      components: [],
    });
  }
}
