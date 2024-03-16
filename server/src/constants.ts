import { CharacterModifier } from "./types";
import { buildGlobalCustomId } from "./util";

export const ROTMG_CLASSES = [
  "Knight",
  "Warrior",
  "Paladin",
  "Assassin",
  "Rogue",
  "Trickster",
  "Archer",
  "Huntress",
  "Mystic",
  "Wizard",
  "Necromancer",
  "Ninja",
  "Samurai",
  "Priest",
  "Sorcerer",
  "Bard",
  "Summoner",
  "Kensei",
] as const;

export const CHARACTER_MODIFIERS = ["No_Pet", "Crucible", "UT_ST_Only", "Duo"] as const;
export const CHARACTER_MODIFER_PERCENTS: Record<CharacterModifier, number> = {
  No_Pet: 5,
  Crucible: 3,
  UT_ST_Only: 3,
  Duo: -5,
} as const;

export const ACL_GROUPS = ["Admin", "Contest Staff", "Contestant"] as const;

export const DEFAULT_TIMEOUT_MS = 300_000; // 5 minutes

export const CONTEST_POST_BUTTON_CUSTOM_IDS = {
  signUp: buildGlobalCustomId("contestPost", "signUp"),
  newCharacter: buildGlobalCustomId("contestPost", "newCharacter"),
  editCharacter: buildGlobalCustomId("contestPost", "editCharacter"),
};

export const SUBMISSION_POST_BUTTON_CUSTOM_IDS = {
  accept: buildGlobalCustomId("submissionPost", "accept"),
  reject: buildGlobalCustomId("submissionPost", "reject"),
};
