import {
  ActionRowBuilder,
  ButtonBuilder,
  ButtonInteraction,
  ButtonStyle,
  CacheType,
  ChatInputCommandInteraction,
  ComponentType,
  EmbedBuilder,
  SlashCommandBuilder,
  channelLink,
  hideLinkEmbed,
  hyperlink,
} from "discord.js";
import { PointsManager } from "../pointsManager";
import { buildCharacterEmbed } from "../processes/common";
import { getCharacter, updateCharacterActivity, getActiveCharacterByUserId, createCharacter } from "../services/characterService";
import { getContest, getActiveContest } from "../services/contestService";
import { getSubmissionsForCharacter } from "../services/submissionService";
import { SlashCommand, SlashCommandDescriptions } from "../types";
import { formatKeywordsForDisplay, formatPointsForDisplay } from "../util";
import { Contest } from "@prisma/client";
import { RotmgClass, CharacterModifier } from "../types";
import { ROTMG_CLASSES, CHARACTER_MODIFIERS } from "../constants";
import { v4 as uuidv4 } from "uuid";

const descriptions = {
  description: "Character info.",
  subcommands: {
    view: {
      description: "View full character info.",
      options: {
        characterId: "Character ID.",
      },
    },
    submissions: {
      description: "View character submissions.",
      options: {
        characterId: "Character ID.",
        last: "Last X character submissions.",
      },
    },
    allSubmissions: {
      description: "View all character submissions.",
      options: {
        characterId: "Character ID.",
      },
    },
    setActive: {
      description: "Set a character as active.",
      options: {
        characterId: "Character ID.",
        isActive: "Whether the character should be active or not.",
      },
    },
    create: {
      description: "Create a new character.",
      options: {
        target: "User to create character for.",
        contestId: "Optional: Contest ID. Omit to use active contest.",
        rotmgClass: "Character class.",
        modifiers: "Comma-separated list of character modifiers.",
      },
    },
  },
} satisfies SlashCommandDescriptions;

const handleCharacterView = async (interaction: ChatInputCommandInteraction) => {
  await interaction.deferReply();
  const characterId = interaction.options.getNumber("character-id", true);
  const character = await getCharacter(characterId);
  if (!character) {
    return await interaction.editReply({
      content: "Character not found.",
    });
  } else {
    return await interaction.editReply({
      embeds: [buildCharacterEmbed("Blue", "all", character)],
    });
  }
};

const handleCharacterSubmissions = async (
  interaction: ChatInputCommandInteraction,
  listAll: boolean
) => {
  await interaction.deferReply({ ephemeral: true });
  const characterId = interaction.options.getNumber("character-id", true);
  const last = listAll ? undefined : interaction.options.getNumber("last", true);
  const character = await getCharacter(characterId);
  if (!character) {
    return await interaction.editReply({
      content: "Character not found.",
    });
  }
  const submissions = await getSubmissionsForCharacter(characterId, last);
  if (submissions.length === 0) {
    return await interaction.editReply({
      content: "No submissions.",
    });
  }

  const textParts = submissions.map((submission) => {
    const points = PointsManager.getInstance().getPointsForAll(
      submission.keywords,
      character.rotmgClass,
      character.modifiers
    );
    return (
      `**Submission ID: ${submission.id}**${submission.isAccepted ? " (Accepted)" : ""}\n` +
      `Keywords: ${formatKeywordsForDisplay(submission.keywords)}\n` +
      `Points: \`${formatPointsForDisplay(points)}\`\n` +
      `${hyperlink("Proof", hideLinkEmbed(submission.proofUrl))}`
    );
  });
  let textBuf = "";
  for (const part of textParts) {
    if (textBuf.length + part.length > 1800) {
      if (textBuf.length === 0) {
        await interaction.user.send({
          content: "Submission skipped (this should not happen).",
        });
        continue;
      }
      await interaction.user.send({
        content: textBuf,
      });
      textBuf = "";
    }
    textBuf += part + "\n\n";
  }
  if (textBuf.length > 0) {
    await interaction.user.send({
      content: textBuf,
    });
  }
  await interaction.editReply({
    content: interaction.user.dmChannel ? channelLink(interaction.user.dmChannel.id) : "Check DMs",
  });
};

const handleCharacterSetActive = async (
  interaction: ChatInputCommandInteraction,
) => {
  await interaction.deferReply({ ephemeral: true });
  const characterId = interaction.options.getNumber("character-id", true);
  const isActive = interaction.options.getBoolean("is-active", true);
  const character = await getCharacter(characterId);
  if (!character) {
    return await interaction.editReply({
      content: "Character not found.",
    });
  }
  await updateCharacterActivity(character, isActive);
  return await interaction.editReply({
    content: `Character ${character.id} set as active=${isActive}.`,
  });
}

const handleCreateCharacter = async (
  interaction: ChatInputCommandInteraction,
) => {
  await interaction.deferReply({ ephemeral: true });
  const user = interaction.options.getUser("target", true);
  const maybeContestId = interaction.options.getNumber("contest-id");
  let contest: Contest | null = null;
  if (maybeContestId) {
    contest = await getContest(maybeContestId);
  } else {
    contest = await getActiveContest();
  }
  if (!contest) {
    return await interaction.editReply({
      content: "Could not find contest",
    });
  }
  const maybeActiveCharacter = await getActiveCharacterByUserId(user.id, contest);
  if (maybeActiveCharacter) {
    return await interaction.editReply({
      content: `User already has an active character (ID: ${maybeActiveCharacter.id}).`,
      embeds: [buildCharacterEmbed("Red", "truncate", maybeActiveCharacter)],
    });
  }

  const rotmgClassInput = interaction.options.getString("rotmg-class", true);
  let rotmgClass: RotmgClass | null = null;
  for (const candidate of ROTMG_CLASSES) {
    if (candidate.toLowerCase() === rotmgClassInput.toLowerCase()) {
      rotmgClass = candidate;
      break;
    }
  }
  if (!rotmgClass) {
    return await interaction.editReply({
      content: `Invalid class [${rotmgClassInput}]. Valid classes: [${ROTMG_CLASSES.join(", ")}]`,
    });
  }
  
  const modifiersInput = interaction.options.getString("modifiers", false) || "";
  const modifiersInputList = modifiersInput.split(",").map((s) => s.trim()).filter((s) => s.length > 0);

  let modifiers: CharacterModifier[] = [];
  for (const modifierInput of modifiersInputList) {
    let foundModifier: CharacterModifier | null = null;
    for (const candidate of CHARACTER_MODIFIERS) {
      if (candidate.toLowerCase() === modifierInput.toLowerCase()) {
        foundModifier = candidate;
        break;
      }
    }
    if (!foundModifier) {
      return await interaction.editReply({
        content: `Invalid modifier [${modifierInput}]. Valid modifiers: [${CHARACTER_MODIFIERS.join(", ")}]`,
      });
    }
    modifiers.push(foundModifier);
  }

  const embed1 = new EmbedBuilder()
    .setColor("Yellow")
    .setTitle("Confirm Character Creation")
    .addFields(
      { name: "Class", value: rotmgClass },
      { name: "Modifiers", value: formatKeywordsForDisplay(modifiers) }
    );
  const confirmButtonCustomId = uuidv4();
  const cancelButtonCustomId = uuidv4();
  const confirmButton = new ButtonBuilder()
    .setCustomId(confirmButtonCustomId)
    .setLabel("Confirm")
    .setStyle(ButtonStyle.Success);
  const cancelButton = new ButtonBuilder()
    .setCustomId(cancelButtonCustomId)
    .setLabel("Cancel")
    .setStyle(ButtonStyle.Danger);
  const confirmMessage = await interaction.editReply({
    content: "",
    embeds: [embed1],
    components: [
      new ActionRowBuilder<ButtonBuilder>().addComponents(confirmButton, cancelButton),
    ],
  });

  let confirmClick: ButtonInteraction;
  try {
    confirmClick = await confirmMessage.awaitMessageComponent({
      componentType: ComponentType.Button,
      filter: (i) => i.user.id === interaction.user.id,
      time: 15_000,
    });
  } catch {
    // Timed out with no click
    return await interaction.editReply({
      content: "Timed out, no character was created.",
      embeds: [],
      components: [],
    });
  }

  // Acknowledge the click so Discord doesn't show "This interaction failed"
  await confirmClick.deferUpdate();

  if (confirmClick.customId === cancelButtonCustomId) {
    return await interaction.editReply({
      content: "Cancelled.",
      embeds: [],
      components: [],
    });
  }

  const newCharacter = await createCharacter(user.id, contest, {
    isActive: true,
    rotmgClass: rotmgClass,
    modifiers: modifiers,
  });
  return await interaction.editReply({
    content: `Created character with ID: ${newCharacter.id}`,
    embeds: [buildCharacterEmbed("Green", "truncate", newCharacter)],
    components: [],
  });
}

const command: SlashCommand = {
  defaultAcl: ["Admin"],
  subcommandAcl: {
    view: ["Contestant"],
    submissions: ["Contestant"],
    setActive: ["Contest Staff", "Moderator", "Admin"],
    allSubmissions: ["Contest Staff", "Moderator", "Admin"],
    create: ["Contest Staff", "Moderator", "Admin"],
  },
  descriptions,
  command: new SlashCommandBuilder()
    .setName("character")
    .setDescription(descriptions.description)
    .addSubcommand((subcommand) =>
      subcommand
        .setName("view")
        .setDescription(descriptions.subcommands.view.description)
        .addNumberOption((option) =>
          option
            .setName("character-id")
            .setDescription(descriptions.subcommands.view.options.characterId)
            .setRequired(true)
        )
    )
    .addSubcommand((subcommand) =>
      subcommand
        .setName("submissions")
        .setDescription(descriptions.subcommands.submissions.description)
        .addNumberOption((option) =>
          option
            .setName("character-id")
            .setDescription(descriptions.subcommands.submissions.options.characterId)
            .setRequired(true)
        )
        .addNumberOption((option) =>
          option
            .setName("last")
            .setDescription(descriptions.subcommands.submissions.options.last)
            .setRequired(true)
        )
    )
    .addSubcommand((subcommand) =>
      subcommand
        .setName("all-submissions")
        .setDescription(descriptions.subcommands.allSubmissions.description)
        .addNumberOption((option) =>
          option
            .setName("character-id")
            .setDescription(descriptions.subcommands.allSubmissions.options.characterId)
            .setRequired(true)
        )
    )
    .addSubcommand((subcommand) =>
      subcommand
        .setName("setActive")
        .setDescription(descriptions.subcommands.setActive.description)
        .addNumberOption((option) =>
          option
            .setName("character-id")
            .setDescription(descriptions.subcommands.setActive.options.characterId)
            .setRequired(true)
        )
        .addBooleanOption((option) =>
          option
            .setName("is-active")
            .setDescription(descriptions.subcommands.setActive.options.isActive)
            .setRequired(true)
        )
    )
    .addSubcommand((subcommand) =>
      subcommand
        .setName("create")
        .setDescription(descriptions.subcommands.create.description)
        .addUserOption((option) =>
          option
            .setName("target")
            .setDescription(descriptions.subcommands.create.options.target)
            .setRequired(true)
        )
        .addNumberOption((option) =>
          option
            .setName("contest-id")
            .setDescription(descriptions.subcommands.create.options.contestId)
            .setRequired(false)
        )
        .addStringOption((option) =>
          option
            .setName("rotmg-class")
            .setDescription(descriptions.subcommands.create.options.rotmgClass)
            .setRequired(true)
        )
        .addStringOption((option) =>
          option
            .setName("modifiers")
            .setDescription(descriptions.subcommands.create.options.modifiers)
            .setRequired(false)
        )
    ),
  async execute(interaction: ChatInputCommandInteraction<CacheType>) {
    const subcommand = interaction.options.getSubcommand();
    switch (subcommand) {
      case "view":
        return await handleCharacterView(interaction);
      case "all-submissions":
        return await handleCharacterSubmissions(interaction, true);
      case "submissions":
        return await handleCharacterSubmissions(interaction, false);
      case "setActive":
        return await handleCharacterSetActive(interaction);
      case "create":
        return await handleCreateCharacter(interaction);
      default:
        return await interaction.reply({
          ephemeral: true,
          content: "Invalid subcommand.",
        });
    }
  },
  cooldown: 10,
};

export default command;
