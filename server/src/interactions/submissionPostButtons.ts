import { ButtonInteraction, userMention } from "discord.js";
import { SUBMISSION_POST_BUTTON_CUSTOM_IDS } from "../constants";
import { PointsManager } from "../pointsManager";
import { buildSubmissionEmbed } from "../processes/common";
import { getCharacter } from "../services/characterService";
import { acceptSubmission, getSubmission } from "../services/submissionService";
import { Settings } from "../settings";

export const isSubmissionPostButtonInteraction = (interaction: ButtonInteraction): boolean => {
  switch (interaction.customId) {
    case SUBMISSION_POST_BUTTON_CUSTOM_IDS.accept:
    case SUBMISSION_POST_BUTTON_CUSTOM_IDS.reject:
      return true;
    default:
      return false;
  }
};

export const handleSubmissionPostButtonInteraction = async (interaction: ButtonInteraction) => {
  switch (interaction.customId) {
    case SUBMISSION_POST_BUTTON_CUSTOM_IDS.accept:
      return await handleAcceptSubmissionButton(interaction);
    case SUBMISSION_POST_BUTTON_CUSTOM_IDS.reject:
      return await handleRejectSubmissionButton(interaction);
  }
};

const handleAcceptSubmissionButton = async (interaction: ButtonInteraction) => {
  await interaction.deferUpdate();
  const submissionId = interaction.message.embeds.at(0)?.footer?.text;
  if (!submissionId) return;
  const submission = await getSubmission(parseInt(submissionId));
  if (!submission) return;
  const character = await getCharacter(submission.characterId);
  if (!character) return;
  const user = await interaction.guild?.members.fetch(character.userId);

  await acceptSubmission(submission);
  const embed = buildSubmissionEmbed("Green", submission.id, {
    userId: character.userId,
    character,
    acceptedKeywords: submission.keywords,
    pointsAdded: PointsManager.getInstance().getPointsForAll(
      submission.keywords,
      character.rotmgClass,
      character.modifiers
    ),
    imageUrl: submission.imageUrl,
  });
  Settings.getInstance()
    .getChannel("log")
    .send({
      content: `Accepted by ${userMention(interaction.user.id)}`,
      embeds: [embed],
      allowedMentions: {
        parse: [],
      },
    });
  await interaction.message.delete();
  await user?.send({
    content: "Submission accepted:",
    embeds: [embed],
  });
};

const handleRejectSubmissionButton = async (interaction: ButtonInteraction) => {
  await interaction.deferUpdate();
  const submissionId = interaction.message.embeds.at(0)?.footer?.text;
  if (!submissionId) return;
  const submission = await getSubmission(parseInt(submissionId));
  if (!submission) return;
  const character = await getCharacter(submission.characterId);
  if (!character) return;
  const user = await interaction.guild?.members.fetch(character.userId);

  const embed = buildSubmissionEmbed("Red", submission.id, {
    userId: character.userId,
    character,
    acceptedKeywords: submission.keywords,
    pointsAdded: PointsManager.getInstance().getPointsForAll(
      submission.keywords,
      character.rotmgClass,
      character.modifiers
    ),
    imageUrl: submission.imageUrl,
  });
  Settings.getInstance()
    .getChannel("log")
    .send({
      content: `Rejected by ${userMention(interaction.user.id)}`,
      embeds: [embed],
      allowedMentions: {
        parse: [],
      },
    });
  await interaction.message.delete();
  await user?.send({
    content: "Submission rejected:",
    embeds: [embed],
  });
};
