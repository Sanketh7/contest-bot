import { ButtonInteraction, GuildMember, Interaction, userMention } from "discord.js";
import { CONTEST_POST_BUTTON_CUSTOM_IDS, SUBMISSION_POST_BUTTON_CUSTOM_IDS } from "../constants";
import { PointsManager } from "../pointsManager";
import { buildSubmissionEmbed } from "../processes/common";
import { EditCharacterProcess } from "../processes/editCharacter";
import { NewCharacterProcess } from "../processes/newCharacter";
import { getCharacter } from "../services/characterService";
import { getActiveContest } from "../services/contestService";
import { acceptSubmission, getSubmission } from "../services/submissionService";
import { Settings } from "../settings";
import { Event } from "../types";

const handleSignUpButton = async (interaction: ButtonInteraction) => {
  const member = interaction.member;
  if (!(member instanceof GuildMember)) {
    return await interaction.reply({
      ephemeral: true,
      content: "Failed to sign up: could not find member.",
    });
  }
  const role = Settings.getInstance().data.roles!.contestant;
  if (member.roles.cache.has(role.id)) {
    return await interaction.reply({
      ephemeral: true,
      content: "You've already signed up.",
    });
  }
  await member.roles.add(role);
  return await interaction.reply({
    ephemeral: true,
    content: "Signed up for the contest!",
  });
};

const handleEditCharacterButton = async (interaction: ButtonInteraction) => {
  await interaction.deferUpdate();
  const contest = await getActiveContest();
  if (!contest) return;
  const message = await interaction.user.send({
    content: "Loading...",
  });
  const process = new EditCharacterProcess(interaction.user, message, contest);
  await process.start();
};

const handleNewCharacterButton = async (interaction: ButtonInteraction) => {
  await interaction.deferUpdate();
  const contest = await getActiveContest();
  if (!contest) return;
  const message = await interaction.user.send({
    content: "Loading...",
  });
  const process = new NewCharacterProcess(interaction.user, message, contest);
  await process.start();
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
      character.rotmgClass
    ),
    imageUrl: submission.imageUrl,
  });
  Settings.getInstance().data.channels!.log.send({
    content: `Accepted by ${userMention(interaction.user.id)}`,
    embeds: [embed],
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
      character.rotmgClass
    ),
    imageUrl: submission.imageUrl,
  });
  Settings.getInstance().data.channels!.log.send({
    content: `Rejected by ${userMention(interaction.user.id)}`,
    embeds: [embed],
  });
  await interaction.message.delete();
  await user?.send({
    content: "Submission rejected:",
    embeds: [embed],
  });
};

const event: Event = {
  name: "interactionCreate",
  async execute(interaction: Interaction) {
    if (interaction.isChatInputCommand()) {
      const command = interaction.client.slashCommands.get(interaction.commandName);
      if (!command) return;
      await command.execute(interaction).catch(console.error);
    } else if (interaction.isAutocomplete()) {
      const command = interaction.client.slashCommands.get(interaction.commandName);
      if (!command || !command.autocomplete) return;
      await command.autocomplete(interaction);
    } else if (interaction.isModalSubmit()) {
      const command = interaction.client.slashCommands.get(interaction.customId);
      if (!command || !command.modal) return;
      await command.modal(interaction);
    } else if (interaction.isButton()) {
      if (interaction.customId === CONTEST_POST_BUTTON_CUSTOM_IDS.signUp) {
        return await handleSignUpButton(interaction);
      } else if (interaction.customId === CONTEST_POST_BUTTON_CUSTOM_IDS.newCharacter) {
        return await handleNewCharacterButton(interaction);
      } else if (interaction.customId === CONTEST_POST_BUTTON_CUSTOM_IDS.editCharacter) {
        return await handleEditCharacterButton(interaction);
      }

      if (interaction.customId === SUBMISSION_POST_BUTTON_CUSTOM_IDS.accept) {
        return await handleAcceptSubmissionButton(interaction);
      } else if (interaction.customId === SUBMISSION_POST_BUTTON_CUSTOM_IDS.reject) {
        return await handleRejectSubmissionButton(interaction);
      }
    }
  },
};

export default event;