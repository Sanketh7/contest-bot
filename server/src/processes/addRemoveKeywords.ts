import { Character, Contest } from "@prisma/client";
import {
  ActionRowBuilder,
  ButtonBuilder,
  Collection,
  ColorResolvable,
  EmbedBuilder,
  Message,
  MessageComponentInteraction,
  User,
  bold,
  userMention,
} from "discord.js";
import { DEFAULT_TIMEOUT_MS } from "../constants";
import { Points, PointsManager } from "../pointsManager";
import { modifyCharacterKeywords } from "../services/characterService";
import { Settings } from "../settings";
import { formatKeywordsForDisplay, formatPointsForDisplay } from "../util";
import { buildCharacterEmbed } from "./common";
import { Process } from "./process";

type ProcessState = {
  acceptedKeywords?: string[];
  rejectedKeywords?: string[];
  pointsDelta?: Points;
};

export class AddRemoveKeywordsProcess extends Process<Contest | null> {
  private state: ProcessState;
  private character: Character;
  private action: "add" | "remove";

  constructor(user: User, message: Message, character: Character, action: "add" | "remove") {
    super(user, message, null);
    this.state = {};
    this.character = character;
    this.action = action;
  }

  async start() {
    return await this.doConfirmCharacterMenu();
  }

  private async doConfirmCharacterMenu() {
    const embed = new EmbedBuilder()
      .setColor("Yellow")
      .setTitle("Confirm Character")
      .addFields({
        name: "Instructions",
        value: `Confirm if you want to ${bold(this.action)} keywords to this character.`,
      });

    const characterEmbed = buildCharacterEmbed("Yellow", "truncate", this.character);
    const { confirmButton, confirmButtonCustomId } = this.buildConfirmButton();
    const { cancelButton, cancelButtonCustomId } = this.buildCancelButton();

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
    return await this.doKeywordEntry();
  }

  private async doKeywordEntry() {
    const { cancelButton, cancelButtonCustomId } = this.buildCancelButton();
    const { confirmButton, confirmButtonCustomId } = this.buildConfirmButton();

    this.message = await this.message.reply({
      embeds: [this.buildKeywordSubmitEmbed()],
      components: [new ActionRowBuilder<ButtonBuilder>().addComponents(cancelButton)],
    });

    while (true) {
      let response: MessageComponentInteraction | Collection<string, Message<boolean>>;
      try {
        const buttonResponsePromise = this.message.awaitMessageComponent({
          filter: (i) =>
            (i.customId === cancelButtonCustomId || i.customId === confirmButtonCustomId) &&
            i.user.id === this.user.id,
          time: DEFAULT_TIMEOUT_MS,
        });
        const keywordsMessagePromise = this.message.channel.awaitMessages({
          filter: (m) => m.author.id === this.user.id && m.content.length > 0,
          max: 1,
          time: DEFAULT_TIMEOUT_MS,
          errors: ["time"],
        });
        response = await Promise.race([buttonResponsePromise, keywordsMessagePromise]);
      } catch (e) {
        return await this.cancel("timeout");
      }

      if (response instanceof MessageComponentInteraction) {
        if (response.customId === confirmButtonCustomId) {
          await response.deferUpdate();
          return await this.doConfirmSubmission();
        } else if (response.customId === cancelButtonCustomId) {
          return await this.cancel("button");
        } else {
          return await this.cancel("unknown");
        }
      } else {
        const keywordsInput = response.at(0)?.content ?? "";
        const keywords = PointsManager.getInstance().extractKeywords(keywordsInput);
        const acceptedKeywords = new Set<string>(keywords);
        const rejectedKeywords = new Set<string>();

        if (this.action === "add") {
          for (const kw of this.character.keywords) {
            if (acceptedKeywords.has(kw)) {
              acceptedKeywords.delete(kw);
              rejectedKeywords.add(kw);
            }
          }
        } else {
          const characterKeywords = new Set<string>(this.character.keywords);
          for (const kw of acceptedKeywords) {
            if (!characterKeywords.has(kw)) {
              acceptedKeywords.delete(kw);
              rejectedKeywords.add(kw);
            }
          }
        }

        this.state.acceptedKeywords = Array.from(acceptedKeywords);
        this.state.rejectedKeywords = Array.from(rejectedKeywords);
        this.state.pointsDelta = PointsManager.getInstance().getPointsForAll(
          this.state.acceptedKeywords,
          this.character!.rotmgClass,
          this.character!.modifiers
        );

        await this.message.edit({
          embeds: [this.buildKeywordSubmitEmbed()],
          components:
            this.state.acceptedKeywords && this.state.acceptedKeywords.length > 0
              ? [new ActionRowBuilder<ButtonBuilder>().addComponents(confirmButton, cancelButton)]
              : [new ActionRowBuilder<ButtonBuilder>().addComponents(cancelButton)],
        });
      }
    }
  }

  private async doConfirmSubmission() {
    const { confirmButton, confirmButtonCustomId } = this.buildConfirmButton();
    const { cancelButton, cancelButtonCustomId } = this.buildCancelButton();

    this.message = await this.message.reply({
      embeds: [this.buildConfirmationEmbed("Yellow")],
      components: [
        new ActionRowBuilder<ButtonBuilder>().addComponents(confirmButton, cancelButton),
      ],
    });

    let response;
    try {
      response = await this.message.awaitMessageComponent({
        filter: (i) =>
          i.user.id === this.user.id &&
          (i.customId === cancelButtonCustomId || i.customId === confirmButtonCustomId),
        time: DEFAULT_TIMEOUT_MS,
      });
    } catch (err) {
      return await this.cancel("timeout");
    }

    if (response.customId === confirmButtonCustomId) {
      await response.deferUpdate();
      return await this.uploadSubmission();
    } else if (response.customId === cancelButtonCustomId) {
      return await this.cancel("button");
    } else {
      return await this.cancel("unknown");
    }
  }

  private async uploadSubmission() {
    await modifyCharacterKeywords(
      this.character.id,
      Array.from(this.state?.acceptedKeywords ?? []),
      this.action
    );
    await this.message.edit({
      embeds: [this.buildConfirmationEmbed("Green")],
      components: [],
      content: "",
    });
    return await Settings.getInstance()
      .getChannel("log")
      .send({
        content:
          userMention(this.user.id) +
          " is " +
          (this.action === "add" ? "adding keywords" : "removing keywords"),
        embeds: [this.buildConfirmationEmbed(this.action === "add" ? "Green" : "Red")],
      });
  }

  private buildKeywordSubmitEmbed(): EmbedBuilder {
    const embed = new EmbedBuilder().setTitle("Submission").addFields({
      name: "Instructions",
      value: `Using this [document](${Settings.getInstance().get(
        "pointsRefUrl"
      )}) as reference, enter the keywords.`,
    });
    if (this.state.acceptedKeywords !== undefined || this.state.rejectedKeywords !== undefined) {
      embed.addFields({
        name: "Accepted Keywords",
        value: `These keywords were accepted. To edit, send another message with your updated keywords list.\n ${formatKeywordsForDisplay(
          this.state.acceptedKeywords
        )}`,
      });
      embed.addFields({
        name: `Points ${this.action === "add" ? "Added" : "Removed"}`,
        value: formatPointsForDisplay(this.state.pointsDelta),
      });
      embed.addFields({
        name: "Rejected Keywords",
        value: `These keywords were rejected.\n${formatKeywordsForDisplay(
          this.state.rejectedKeywords
        )}`,
      });
    }
    return embed;
  }

  private buildConfirmationEmbed(color: ColorResolvable) {
    const embed = new EmbedBuilder()
      .setTitle("Modifying Keywords")
      .setColor(color)
      .addFields(
        {
          name: "Character",
          value: `${userMention(this.character.userId)}'s ${this.character.rotmgClass}`,
          inline: true,
        },
        {
          name: "Modifiers",
          value: formatKeywordsForDisplay(this.character.modifiers),
          inline: true,
        },
        {
          name: "Items/Achievements",
          value: formatKeywordsForDisplay(this.state.acceptedKeywords),
        },
        {
          name: `Points ${this.action === "add" ? "Added" : "Removed"}`,
          value: formatPointsForDisplay(this.state.pointsDelta),
          inline: true,
        }
      );
    return embed;
  }
}
