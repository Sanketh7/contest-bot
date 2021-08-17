import csv
from typing import Dict, Tuple
from flashtext import KeywordProcessor
from settings import Settings


class PointsManager:
    # keywords along with their alt names
    keywords: Dict[str, Tuple[str, str]] = dict()
    # keyword -> class -> points
    points_data: Dict[str, Dict[str, int]] = dict()

    # parses from the csv points data file
    @staticmethod
    def parse_data():
        data_file = open(Settings.points_data_file, "r")
        data_reader = csv.reader(data_file)
        data = []
        for row in data_reader:
            data.append(row)

        rotmg_classes = data[0][2:] # classes are in the first row of the csv (index 0)
        data = data[1:]

        for row in data:
            PointsManager.keywords[row[0].lower()] = [
                row[0].lower(), row[1].lower()]
            PointsManager.points_data[row[0].lower()] = {}
            for i in range(0, len(rotmg_classes)):
                PointsManager.points_data[row[0].lower(
                )][rotmg_classes[i].lower()] = int(row[2+i])

    # uses flashtext to extract the keywords from a raw input string
    # raw input comes from processes
    @staticmethod
    def parse_keywords(raw: str):
        proc = KeywordProcessor()
        proc.add_keywords_from_dict(PointsManager.keywords)
        return proc.extract_keywords(raw)
