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

        """
        Temporary mapping from old keyword to new keyword
        new name -> old name
        """
        legacy_keyword_map = {
            'Oryxmas Ornament: Energized': 'UT. Oryxmas Ornament: Energized',
            'Oryxmas Ornament: Weak': 'UT. Oryxmas Ornament: Weak',
            'Oryxmas Ornament: Exposed': 'UT. Oryxmas Ornament: Exposed',
            'Battalion Banner': 'Battallion Banner',
            'Spider\'s Eye Ring': 'Spider Eye Ring'
        }
        legacy_keyword_map = dict((k.lower(), v.lower()) for k,v in legacy_keyword_map.items())

        for row in data:
            if row[0].lower() in map(lambda s: s.lower(), legacy_keyword_map.keys()):
                PointsManager.keywords[row[0].lower()] = [
                    row[0].lower(), row[1].lower(), legacy_keyword_map[row[0].lower()].lower()]
                print(PointsManager.keywords[row[0].lower()])
            else:
                PointsManager.keywords[row[0].lower()] = [
                    row[0].lower(), row[1].lower()]
            PointsManager.points_data[row[0].lower()] = {}
            for i in range(0, len(rotmg_classes)):
                try:
                    PointsManager.points_data[row[0].lower()][rotmg_classes[i].lower()] = int(row[2+i])
                except ValueError:
                    print(f"row {row[0].lower()} class {rotmg_classes[i].lower()} val {row[2+i]}")
        for new_name, old_name in legacy_keyword_map.items():
            PointsManager.points_data[old_name.lower()] = PointsManager.points_data[new_name.lower()]


    # uses flashtext to extract the keywords from a raw input string
    # raw input comes from processes
    @staticmethod
    def parse_keywords(raw: str):
        proc = KeywordProcessor()
        proc.add_keywords_from_dict(PointsManager.keywords)
        return proc.extract_keywords(raw)
