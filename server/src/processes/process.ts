import { ButtonBuilder, ButtonStyle, Message, User } from "discord.js";
import { buildProcessCustomId } from "../util";

export abstract class Process<C> {
  protected user: User;
  protected message: Message;
  protected contest: C;

  constructor(user: User, message: Message, contest: C) {
    this.user = user;
    this.message = message;
    this.contest = contest;
  }

  abstract start(): Promise<any>;

  protected async cancel(reason: "button" | "timeout" | "unknown") {
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
      embeds: [],
    });
  }

  protected buildCancelButton(): { cancelButton: ButtonBuilder; cancelButtonCustomId: string } {
    const cancelButtonCustomId = buildProcessCustomId(this.constructor.name, "cancelButton");
    const cancelButton = new ButtonBuilder()
      .setCustomId(cancelButtonCustomId)
      .setLabel("Cancel")
      .setStyle(ButtonStyle.Danger);
    return {
      cancelButton,
      cancelButtonCustomId,
    };
  }

  protected buildConfirmButton(): { confirmButton: ButtonBuilder; confirmButtonCustomId: string } {
    const confirmButtonCustomId = buildProcessCustomId(this.constructor.name, "confirmButton");
    const confirmButton = new ButtonBuilder()
      .setCustomId(confirmButtonCustomId)
      .setLabel("Confirm")
      .setStyle(ButtonStyle.Success);
    return {
      confirmButton,
      confirmButtonCustomId,
    };
  }
}
