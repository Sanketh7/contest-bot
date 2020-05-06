import csv

class_order = ['knight', 'warrior', 'paladin', 'assassin', 'rogue', 'trickster', 'archer', 'huntress', 'mystic',
               'wizard', 'necromancer', 'samurai', 'priest', 'sorcerer']


class PointsDataManager:
    def __init__(self):
        data_file = open("../ppe_data.csv", "r")
        data_reader = csv.reader(data_file)
        self.data = []
        for row in data_reader:
            self.data.append(row)
        self.data = self.data[1:]

        self.keywords = {}
        self.points_data = {}

        self.parse_data()

    def parse_data(self):
        for row in self.data:
            self.keywords[row[0].lower()] = [row[1].lower()]
            self.points_data[row[0].lower()] = {}
            for i in range(0, len(class_order)):
                self.points_data[row[0].lower()][class_order[i].lower()] = int(row[2+i])
