import * as csv from "fast-csv";
import FlashText from "flashtext2js";
import { readFileSync } from "fs";
import { finished } from "stream/promises";
import { ROTMG_CLASSES } from "./constants";
import { RotmgClass } from "./types";

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

  getPointsFor(keyword: string, rotmgClass: RotmgClass): number | undefined {
    return this.points.get(this.createPointsMapKey(keyword, rotmgClass));
  }

  extractKeywords(input: string): string[] {
    return this.processor.extractKeywords(input) as string[];
  }

  private createPointsMapKey(keyword: string, rotmgClass: RotmgClass): string {
    return `${keyword}$${rotmgClass}`;
  }
}
