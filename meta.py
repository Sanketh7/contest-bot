import json

class Meta:    
    prefix: str
    guild: 

    @staticmethod
    def init(file_path: str):
        with open(file_path) as fin:
            raw_data = json.loads(fin.read()) # TODO: catch and error out file exception
        
        # load individual settings
        Meta.prefix = Meta.raw_data["prefix"]