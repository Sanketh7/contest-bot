import {
  ActionRowBuilder,
  ButtonBuilder,
  ButtonStyle,
  Message,
  StringSelectMenuBuilder,
  StringSelectMenuInteraction,
  StringSelectMenuOptionBuilder,
  User,
} from "discord.js";
import { CHARACTER_MODIFIERS, DEFAULT_TIMEOUT_MS, ROTMG_CLASSES } from "../constants";
import { buildProcessCustomId } from "../util";

type ProcessState = {
  selectedClass?: string;
  selectedModifiers?: string[];
};

export class NewCharacterProcess {
  private user: User;
  private message: Message;
  private state: ProcessState;

  constructor(user: User, message: Message) {
    this.user = user;
    this.message = message;
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
        return await this.cancel();
      }
      await response.deferUpdate();
    } catch (e) {
      return await this.cancel();
    }
    this.state = {
      ...this.state,
      selectedClass: (response as StringSelectMenuInteraction).values[0],
    };
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
        return await this.cancel();
      }
      await response.deferUpdate();
    } catch (e) {
      return await this.cancel();
    }
    this.state = {
      ...this.state,
      selectedModifiers: (response as StringSelectMenuInteraction).values ?? [],
    };
    return this.doConfirm();
  }

  private async doConfirm() {
    if (this.state.selectedClass === undefined || this.state.selectedModifiers === undefined) {
      return await this.cancel("unknown");
    }
    const confirmButtonCustomId = buildProcessCustomId(NewCharacterProcess.name, "confirmButton");
    const confirmButton = new ButtonBuilder()
      .setCustomId(confirmButtonCustomId)
      .setLabel("Confirm")
      .setStyle(ButtonStyle.Success);
    const { cancelButton, cancelButtonCustomId } = this.buildCancelButton();

    await this.message.edit({
      content: `Creating character:\n**Class:** ${this.state.selectedClass}\n**Modifiers:** ${this.state.selectedModifiers}`,
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
        return await this.cancel();
      }
      await response.deferUpdate();
    } catch (e) {
      return await this.cancel("timeout");
    }

    // TODO: create character
    return await this.message.edit({
      content: `Created character:\n**Class:** ${this.state.selectedClass}\n**Modifiers:** ${this.state.selectedModifiers}`,
      components: [],
    });
  }

  private async cancel(reason?: "button" | "timeout" | "unknown") {
    let reasonMessage: string = "Cancelled.";
    switch (reason) {
      case "button":
        reasonMessage = "Cancelled.";
        break;
      case "timeout":
        reasonMessage = "Cancelled due to timeout.";
        break;
      case "unknown":
        reasonMessage = "Cancelled because something went wrong.";
        break;
    }
    await this.message.edit({
      content: reasonMessage,
      components: [],
    });
  }

  private buildCancelButton(): { cancelButton: ButtonBuilder; cancelButtonCustomId: string } {
    const cancelButtonCustomId = buildProcessCustomId(NewCharacterProcess.name, "cancelButton");
    const cancelButton = new ButtonBuilder()
      .setCustomId(cancelButtonCustomId)
      .setLabel("Cancel")
      .setStyle(ButtonStyle.Danger);
    return {
      cancelButton,
      cancelButtonCustomId,
    };
  }
}
