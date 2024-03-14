/*
  Warnings:

  - The values [knight,warrior,paladin,assassin,rogue,trickster,archer,huntress,mystic,wizard,necromancer,ninja,samurai,priest,sorcerer,bard,summoner,kensei] on the enum `RotmgClass` will be removed. If these variants are still used in the database, this will fail.

*/
-- AlterEnum
BEGIN;
CREATE TYPE "RotmgClass_new" AS ENUM ('Knight', 'Warrior', 'Paladin', 'Assassin', 'Rogue', 'Trickster', 'Archer', 'Huntress', 'Mystic', 'Wizard', 'Necromancer', 'Ninja', 'Samurai', 'Priest', 'Sorcerer', 'Bard', 'Summoner', 'Kensei');
ALTER TABLE "Character" ALTER COLUMN "rotmgClass" TYPE "RotmgClass_new" USING ("rotmgClass"::text::"RotmgClass_new");
ALTER TYPE "RotmgClass" RENAME TO "RotmgClass_old";
ALTER TYPE "RotmgClass_new" RENAME TO "RotmgClass";
DROP TYPE "RotmgClass_old";
COMMIT;
