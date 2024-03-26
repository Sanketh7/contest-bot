import { PrismaClient } from "@prisma/client";
import { createSoftDeleteExtension } from "prisma-extension-soft-delete";
import { PointsManager } from "./pointsManager";

const softDeleteExtension = createSoftDeleteExtension({
  models: {
    Contest: true,
    Character: true,
    Submission: true,
    Guild: true,
  },
  defaultConfig: {
    field: "deletedAt",
    createValue: (deleted) => {
      if (deleted) return new Date();
      return null;
    },
  },
});

export const prisma = new PrismaClient().$extends(softDeleteExtension);

export const prismaWithPoints = new PrismaClient()
  .$extends({
    result: {
      character: {
        points: {
          needs: { keywords: true, rotmgClass: true, modifiers: true },
          compute(character) {
            return PointsManager.getInstance().getPointsForAll(
              character.keywords,
              character.rotmgClass,
              character.modifiers
            );
          },
        },
      },
    },
  })
  .$extends(softDeleteExtension);
