import csv

class_order = ['knight', 'warrior', 'paladin', 'assassin', 'rogue', 'trickster', 'archer', 'huntress', 'mystic',
               'wizard', 'necromancer', 'ninja', 'samurai', 'priest', 'sorcerer']
# TODO: fix the issue with class order changing depending on the contest type

class PointsDataManager:
    def __init__(self):
        self.keywords = {}
        self.points_data = {}

    def parse_data(self, contest_type):
        data_file = open(contest_type + "_data.csv", "r")
        data_reader = csv.reader(data_file)
        data = []
        for row in data_reader:
            data.append(row)
        data = data[1:]

        self.keywords = {}
        self.points_data = {}

        for row in data:
            self.keywords[row[0].lower()] = [row[1].lower()]
            self.points_data[row[0].lower()] = {}
            for i in range(0, len(class_order)):
                self.points_data[row[0].lower()][class_order[i].lower()] = int(row[2+i])
