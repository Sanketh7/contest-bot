import dayjs from "dayjs";
import { User } from "discord.js";
import { CHARACTER_MODIFER_PERCENTS } from "./constants";
import { Points } from "./pointsManager";
import { Settings } from "./settings";
import { AclGroup, CharacterModifier, SlashCommand } from "./types";

export const checkAcl = async (user: User, acls: Set<AclGroup>): Promise<boolean> => {
  if (acls.size === 0) {
    return true;
  }
  if (user.id === Settings.getInstance().get("botOwner").id) {
    return true;
  }
  const guild = Settings.getInstance().get("guild");
  const member = await guild.members.fetch(user.id);
  let ok = false;
  for (const acl of acls) {
    if (acl === "Admin") {
      ok = ok || member.roles.cache.has(Settings.getInstance().getRole("admin").id);
    } else if (acl === "Contest Staff") {
      ok = ok || member.roles.cache.has(Settings.getInstance().getRole("contestStaff").id);
    } else if (acl === "Contestant") {
      ok = ok || member.roles.cache.has(Settings.getInstance().getRole("contestant").id);
    }
  }
  return ok;
};

export const getAcl = (command: SlashCommand, subcommandName: string | null): Set<AclGroup> => {
  let acl = new Set(command.defaultAcl);
  if (
    subcommandName &&
    command.subcommandAcl &&
    Object.keys(command.subcommandAcl).includes(subcommandName)
  ) {
    acl = new Set(command.subcommandAcl[subcommandName]);
  }
  return acl;
};

export function buildProcessCustomId(processName: string, componentName: string) {
  return `process#${processName}#${componentName}`;
}

export function buildGlobalCustomId(scope: string, componentName: string) {
  return `global#${scope}#${componentName}`;
}

export const formatKeywordsForDisplay = (keywords: string[] | undefined | null) => {
  if (!keywords) {
    return "`[]`";
  } else {
    return `\`[${keywords.join(", ")}]\``;
  }
};

export const formatModifierChoiceForDisplay = (modifier: CharacterModifier): string => {
  const name = modifier.replaceAll("_", " ");
  const percent = CHARACTER_MODIFER_PERCENTS[modifier];
  return `${name} (${percent >= 0 ? "+" : "-"}${Math.abs(percent)}%)`;
};

export const formatPointsForDisplay = (points: Points | null | undefined): string => {
  if (!points) return "0";
  if (points.modifier > 0) {
    return `${points.raw} + ${points.modifier.toFixed(2)}`;
  } else if (points.modifier < 0) {
    return `${points.raw} - ${-points.modifier.toFixed(2)}`;
  } else {
    return points.total.toString();
  }
};

export const truncateEllipses = (str: string, length: number) => {
  if (str.length > length) {
    return str.substring(0, Math.max(length - 3, 0)) + "...";
  } else {
    return str;
  }
};

export const parseDatetimeString = (input: string): Date | null => {
  const ret = dayjs.utc(input, "YYYY-MM-DD HH:mm", true);
  return ret.isValid() ? ret.toDate() : null;
};

export const displayDatetimeString = (input: Date): string => {
  return dayjs.utc(input).format("YYYY-MM-DD HH:mm");
};
