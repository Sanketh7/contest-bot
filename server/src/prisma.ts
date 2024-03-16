import { PrismaClient } from "@prisma/client";
import { PointsManager } from "./pointsManager";

export const prisma = new PrismaClient();

export const prismaWithPoints = new PrismaClient().$extends({
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
});
