import csv
import typing
from flashtext import KeywordProcessor
from settings import Settings


class PointsManager:
    keywords: dict[str, tuple(str, str)]  # keywords along with their alt names
    points_data: dict[str, dict[str, int]]  # keyword -> class -> points

    @staticmethod
    def parse_data():
        data_file = open(Settings.points_data_file, "r")
        data_reader = csv.reader(data_file)
        data = []
        for row in data_reader:
            data.append(row)
        data = data[1:]

        for row in data:
            PointsManager.keywords[row[0].lower()] = [
                row[0].lower(), row[1].lower()]
            PointsManager.points_data[row[0].lower()] = {}
            for i in range(0, len(Settings.rotmg_classes)):
                PointsManager.points_data[row[0].lower()][Settings.rotmg_classes[i].lower()] = int(
                    row[2+i])

    @staticmethod
    def parse_keywords(raw: str):
        proc = KeywordProcessor()
        proc.add_keywords_from_dict(PointsManager.keywords)
        return proc.extract_keywords(raw)
