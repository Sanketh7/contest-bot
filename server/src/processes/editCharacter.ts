import { Character, Contest } from "@prisma/client";
import {
  ActionRowBuilder,
  ButtonBuilder,
  ButtonStyle,
  Collection,
  ColorResolvable,
  EmbedBuilder,
  Message,
  MessageComponentInteraction,
  User,
} from "discord.js";
import { DEFAULT_TIMEOUT_MS, SUBMISSION_POST_BUTTON_CUSTOM_IDS } from "../constants";
import { Points, PointsManager } from "../pointsManager";
import { getActiveCharacterByUserId } from "../services/characterService";
import { createSubmission } from "../services/submissionService";
import { Settings } from "../settings";
import { formatKeywordsForDisplay, formatPointsForDisplay } from "../util";
import { buildSubmissionEmbed } from "./common";
import { Process } from "./process";

type ProcessState = {
  proofUrls: string[];
  acceptedKeywords?: string[];
  rejectedKeywords?: string[];
  pointsAdded?: Points;
};

export class EditCharacterProcess extends Process<Contest> {
  private state: ProcessState;
  private character?: Character;

  constructor(user: User, message: Message, contest: Contest) {
    super(user, message, contest);
    this.state = {
      proofUrls: [],
    };
  }

  async start() {
    const character = await getActiveCharacterByUserId(this.user.id, this.contest);
    if (!character) {
      return await this.message.edit({
        content: "You have no active characters to edit.",
        embeds: [],
        components: [],
      });
    }
    this.character = character;
    return await this.doProofUpload();
  }

  private async doProofUpload() {
    const embed = new EmbedBuilder().setTitle("Submission").addFields({
      name: "Instructions",
      value: `Use this [document](${Settings.getInstance().get(
        "pointsRefUrl"
      )}) for a list of items and achievements.

      Send a message with proof **in this DM** as specified in the contest rules.

      Valid formats:
      \\- Upload an image (click the plus button to upload or copy and paste)
      \\- Upload a video (click the plus button to upload)
      \\- Send a link to a YouTube video.

      If you do not use any of these methods, the bot cannot detect it.

      **You MUST have your ENTIRE game visible (i.e. not just your inventory).**
      If you don't follow these rules, your submission will likely be denied.`,
    });
    const { cancelButton, cancelButtonCustomId } = this.buildCancelButton();

    await this.message.edit({
      content: "",
      embeds: [embed],
      components: [new ActionRowBuilder<ButtonBuilder>().addComponents(cancelButton)],
    });

    const extractValidAttachment = (msg: Message): string | null => {
      const file = msg.attachments.at(0);
      if (!file || !file.contentType) {
        return null;
      }
      const isValid = file.contentType.startsWith("image") || file.contentType.startsWith("video");
      if (isValid) {
        return file.url;
      }
      return null;
    };

    const extractVideoLink = (text: string): string | null => {
      const ytRegex =
        /((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?/;
      const ytMatch = ytRegex.exec(text);
      if (ytMatch) {
        return ytMatch[0];
      }
      return null;
    };

    const filter = (msg: Message) => {
      if (msg.author.id !== this.user.id) {
        return false;
      }
      return extractValidAttachment(msg) !== null || extractVideoLink(msg.cleanContent) !== null;
    };

    let collected: Collection<string, Message<boolean>>;
    try {
      const p1 = this.message.awaitMessageComponent({
        filter: (i) => i.customId === cancelButtonCustomId && i.user.id === this.user.id,
        time: DEFAULT_TIMEOUT_MS,
      });
      const p2 = this.message.channel.awaitMessages({
        filter,
        max: 1,
        time: DEFAULT_TIMEOUT_MS,
        errors: ["time"],
      });

      const res = await Promise.race([p1, p2]);
      if (res instanceof MessageComponentInteraction) {
        return await this.cancel("button");
      }
      collected = res;
    } catch (err) {
      return await this.cancel("timeout");
    }

    const proofUrl =
      extractValidAttachment(collected.at(0)!) ??
      extractVideoLink(collected.at(0)!.cleanContent) ??
      "";
    this.state.proofUrls.push(proofUrl);
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
        for (const kw of this.character?.keywords ?? []) {
          if (acceptedKeywords.has(kw)) {
            acceptedKeywords.delete(kw);
            rejectedKeywords.add(kw);
          }
        }

        this.state.acceptedKeywords = Array.from(acceptedKeywords);
        this.state.rejectedKeywords = Array.from(rejectedKeywords);
        this.state.pointsAdded = PointsManager.getInstance().getPointsForAll(
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
      embeds: [this.buildSubmissionEmbed("Yellow", null)],
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
    if (!this.character || this.state.proofUrls.length == 0 || !this.state.acceptedKeywords) {
      return await this.cancel("unknown");
    }
    const submission = await createSubmission(this.character, {
      keywords: this.state.acceptedKeywords,
      proofUrls: this.state.proofUrls,
    });
    await this.message.edit({
      embeds: [this.buildSubmissionEmbed("Green", submission.id)],
      components: [],
      content: "",
    });

    const acceptButton = new ButtonBuilder()
      .setCustomId(SUBMISSION_POST_BUTTON_CUSTOM_IDS.accept)
      .setLabel("Accept")
      .setStyle(ButtonStyle.Success);
    const rejectButton = new ButtonBuilder()
      .setCustomId(SUBMISSION_POST_BUTTON_CUSTOM_IDS.reject)
      .setLabel("Reject")
      .setStyle(ButtonStyle.Danger);
    return await Settings.getInstance()
      .getChannel("submission")
      .send({
        embeds: [this.buildSubmissionEmbed("Yellow", submission.id)],
        components: [
          new ActionRowBuilder<ButtonBuilder>().addComponents(acceptButton, rejectButton),
        ],
      });
  }

  private buildKeywordSubmitEmbed(): EmbedBuilder {
    const embed = new EmbedBuilder().setTitle("Submission").addFields({
      name: "Instructions",
      value: `Using this [document](${Settings.getInstance().get(
        "pointsRefUrl"
      )}) as reference, enter the keywords that correspond to your items/achievements.
      This is how you will get your points.

      **If points are not entered correctly, your submission will be denied.**`,
    });
    if (this.state.acceptedKeywords !== undefined || this.state.rejectedKeywords !== undefined) {
      embed.addFields({
        name: "Accepted Keywords",
        value: `These keywords were accepted. To edit, send another message with your updated keywords list.\n ${formatKeywordsForDisplay(
          this.state.acceptedKeywords
        )}`,
      });
      embed.addFields({
        name: "Points Added",
        value: formatPointsForDisplay(this.state.pointsAdded),
      });
      embed.addFields({
        name: "Rejected Keywords",
        value: `These keywords were rejected because your character already has them.\n${formatKeywordsForDisplay(
          this.state.rejectedKeywords
        )}`,
      });
    }
    return embed;
  }

  private buildSubmissionEmbed(color: ColorResolvable, submissionId: number | null): EmbedBuilder {
    return buildSubmissionEmbed(color, submissionId, {
      userId: this.user.id,
      character: this.character,
      acceptedKeywords: this.state.acceptedKeywords ?? [],
      pointsAdded: this.state.pointsAdded,
      proofUrls: this.state.proofUrls,
    });
  }
}
