import * as csv from "fast-csv";
import FlashText from "flashtext2js";
import { readFileSync } from "fs";
import { finished } from "stream/promises";
import { CHARACTER_MODIFER_PERCENTS, ROTMG_CLASSES } from "./constants";
import { CharacterModifier, RotmgClass } from "./types";

export type Points = {
  raw: number;
  modifier: number;
  total: number;
};

export class PointsManager {
  private static instance: PointsManager;
  private processor: FlashText;
  private points: Map<string, number>;

  private constructor() {
    this.processor = new FlashText({
      ignore: true, // ignore case
    });
    this.points = new Map<string, number>();
  }

  static getInstance(): PointsManager {
    if (!this.instance) {
      this.instance = new PointsManager();
    }
    return this.instance;
  }

  async loadCsv(path: string) {
    try {
      const csvData = readFileSync(path, "utf-8");
      const stream = csv
        .parse({ headers: true })
        .on("error", console.error)
        .on("data", (row) => {
          const keyword = (row["Item Name"] as string).toLowerCase();
          const shortName = (row["Short Name"] as string).toLowerCase();
          this.processor.addKeyWordsFromArray([keyword, shortName], keyword);
          for (const rotmgClass of ROTMG_CLASSES) {
            this.points.set(
              this.createPointsMapKey(keyword, rotmgClass),
              parseInt(row[rotmgClass])
            );
          }
        });
      stream.write(csvData);
      stream.end();
      await finished(stream);
    } catch (err) {
      console.error(err);
    }
  }

  getPointsFor(
    keyword: string,
    rotmgClass: RotmgClass,
    modifiers: CharacterModifier[]
  ): number | undefined {
    const percent = Array.from(new Set(modifiers))
      .map((m) => CHARACTER_MODIFER_PERCENTS[m])
      .reduce((a, x) => a + x, 0);
    const rawPoints = this.points.get(this.createPointsMapKey(keyword, rotmgClass));
    return rawPoints ? rawPoints * (1 + percent / 100) : undefined;
  }

  getPointsForAll(
    keywords: string[],
    rotmgClass: RotmgClass,
    modifers: CharacterModifier[]
  ): Points {
    const ret = Array.from(new Set(keywords))
      .map((k) => {
        const raw = this.getPointsFor(k, rotmgClass, []) ?? 0;
        const total = this.getPointsFor(k, rotmgClass, modifers) ?? 0;
        return {
          raw,
          modifier: total - raw,
          total,
        };
      })
      .reduce(
        (a, x) => ({
          raw: a.raw + x.raw,
          modifier: a.modifier + x.modifier,
          total: a.total + x.total,
        }),
        {
          raw: 0,
          modifier: 0,
          total: 0,
        }
      );
    return {
      ...ret,
      total: Math.max(0, Math.round(ret.total)),
    };
  }

  extractKeywords(input: string): string[] {
    return this.processor.extractKeywords(input) as string[];
  }

  private createPointsMapKey(keyword: string, rotmgClass: RotmgClass): string {
    return `${keyword}$${rotmgClass}`;
  }
}
