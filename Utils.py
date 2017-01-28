from json import JSONEncoder

class GraphObjectEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

subjectsPerson = {#'person': "http://dbpedia.org/ontology/Person",
                          'politician': "http://dbpedia.org/ontology/Politician",
                          'soccer_player': "http://dbpedia.org/ontology/SoccerPlayer",
                          'baseball_players': "http://dbpedia.org/ontology/BaseballPlayer",
                          'comedian': "http://dbpedia.org/ontology/Comedian",
                          "Company": "http://dbpedia.org/ontology/Company",
                          "EducationalInstitution": "http://dbpedia.org/ontology/EducationalInstitution"}


subjectsPlaces = {#'Place': "http://dbpedia.org/ontology/Place",
                  'NaturalPlace': "http://dbpedia.org/ontology/NaturalPlace",
                  'HistoricPlace': "http://dbpedia.org/ontology/HistoricPlace",
                  'CelestialBody': "http://dbpedia.org/ontology/CelestialBody",
                  'architectural_structure': "http://dbpedia.org/ontology/ArchitecturalStructure"}

subjectsLive = {#'Animal': "http://dbpedia.org/ontology/Animal",
                'Plant': "http://dbpedia.org/ontology/Plant",
                'Insect': "http://dbpedia.org/ontology/Insect",
                'Fish': "http://dbpedia.org/ontology/Fish",
                'Mammal': "http://dbpedia.org/ontology/Mammal",
                'Play': "http://dbpedia.org/ontology/Play"}

dictionaries = [subjectsPerson, subjectsPlaces, subjectsLive]



dictionariest = [{'politician': "http://dbpedia.org/ontology/Politician"}]