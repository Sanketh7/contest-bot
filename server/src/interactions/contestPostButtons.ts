import { ButtonInteraction, GuildMember } from "discord.js";
import { CONTEST_POST_BUTTON_CUSTOM_IDS } from "../constants";
import { EditCharacterProcess } from "../processes/editCharacter";
import { NewCharacterProcess } from "../processes/newCharacter";
import { getActiveContest } from "../services/contestService";
import { getBanList } from "../services/guildService";
import { Settings } from "../settings";
import { checkAcl } from "../util";

export const isContestPostButtonInteraction = (interaction: ButtonInteraction): boolean => {
  switch (interaction.customId) {
    case CONTEST_POST_BUTTON_CUSTOM_IDS.signUp:
    case CONTEST_POST_BUTTON_CUSTOM_IDS.signOut:
    case CONTEST_POST_BUTTON_CUSTOM_IDS.newCharacter:
    case CONTEST_POST_BUTTON_CUSTOM_IDS.editCharacter:
      return true;
    default:
      return false;
  }
};

export const handleContestPostButtonInteraction = async (interaction: ButtonInteraction) => {
  switch (interaction.customId) {
    case CONTEST_POST_BUTTON_CUSTOM_IDS.signUp:
      return await handleSignUpButton(interaction);
    case CONTEST_POST_BUTTON_CUSTOM_IDS.signOut:
      return await handleSignOutButton(interaction);
    case CONTEST_POST_BUTTON_CUSTOM_IDS.newCharacter:
      return await handleNewCharacterButton(interaction);
    case CONTEST_POST_BUTTON_CUSTOM_IDS.editCharacter:
      return await handleEditCharacterButton(interaction);
  }
};

const handleSignUpButton = async (interaction: ButtonInteraction) => {
  const member = interaction.member;
  if (!(member instanceof GuildMember)) {
    return await interaction.reply({
      ephemeral: true,
      content: "Failed to sign up: could not find member.",
    });
  }
  if ((await getBanList(member.guild)).includes(interaction.user.id)) {
    return await interaction.reply({
      ephemeral: true,
      content: "You've been banned from participating in contests.",
    });
  }

  const role = Settings.getInstance().getRole("contestant");
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

export const handleSignOutButton = async (interaction: ButtonInteraction) => {
  const member = interaction.member;
  if (!(member instanceof GuildMember)) {
    return await interaction.reply({
      ephemeral: true,
      content: "Failed to sign up: could not find member.",
    });
  }

  const role = Settings.getInstance().getRole("contestant");
  if (!member.roles.cache.has(role.id)) {
    return await interaction.reply({
      ephemeral: true,
      content: "You've already signed out.",
    });
  }
  await member.roles.remove(role);
  return await interaction.reply({
    ephemeral: true,
    content:
      "Signed out of the contest. Note that your submissions and characters were not deleted.",
  });
};

const handleEditCharacterButton = async (interaction: ButtonInteraction) => {
  const aclOk = await checkAcl(interaction.user, new Set(["Contestant"]));
  if (!aclOk) {
    return await interaction.reply({
      ephemeral: true,
      content: "Sign up for the contest first!",
    });
  }
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
  const aclOk = await checkAcl(interaction.user, new Set(["Contestant"]));
  if (!aclOk) {
    return await interaction.reply({
      ephemeral: true,
      content: "Sign up for the contest first!",
    });
  }
  await interaction.deferUpdate();
  const contest = await getActiveContest();
  if (!contest) return;
  const message = await interaction.user.send({
    content: "Loading...",
  });
  const process = new NewCharacterProcess(interaction.user, message, contest);
  await process.start();
};
