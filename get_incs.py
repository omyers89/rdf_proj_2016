import csv
import pickle
import os

def get_incs_f(subj_name):
    rf_name = subj_name + "/" + subj_name + "_incs.dump"
    if not os.path.exists(rf_name):
        return
    incs_file = open(rf_name, 'r')
    inco_dict = pickle.load(incs_file)

    incs_file.close()
    csvf_name = subj_name + "/" + subj_name + "_incs.csv"
    with open(csvf_name, 'w') as csvfile:
        fieldnames = ['Person', 'Property', 'Type']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for pers, pt in inco_dict.items():
            uni_pers = pers.encode('utf-8')
            for p, t in pt:
                uni_p = p.encode('utf-8')
                uni_t = t.encode('utf-8')
                writer.writerow({'Person': uni_pers, 'Property': uni_p, 'Type': uni_t})
                #print {'Person': pers, 'Property': p, 'Type': t}
    csvfile.close()


if __name__ == '__main__':
    

    subjects_f = {'person': "http://dbpedia.org/ontology/Person",
                  'Event': "http://dbpedia.org/ontology/Event",
                  'Location': "http://dbpedia.org/ontology/Location",
                  'Organisation': "http://dbpedia.org/ontology/Organisation",
                  'Manga': "http://dbpedia.org/ontology/Manga",
                  'Animal': "http://dbpedia.org/ontology/Animal",
                  'Mammal': "http://dbpedia.org/ontology/Mammal",
                  'Eukaryote': "http://dbpedia.org/ontology/Eukaryote",
                  'Software': "http://dbpedia.org/ontology/Software",
                  'Play': "http://dbpedia.org/ontology/Play"}

    subjects1 = {'person': "http://dbpedia.org/ontology/Person",
             'Plant': "http://dbpedia.org/ontology/Plant",
             'Animal': "http://dbpedia.org/ontology/Animal",
             'Mammal': "http://dbpedia.org/ontology/Mammal",
             'Software': "http://dbpedia.org/ontology/Software"}
    subjectsPerson = {  # 'personn': "http://dbpedia.org/ontology/Person",
        # 'politician': "http://dbpedia.org/ontology/Politician",
        # 'soccer_player': "http://dbpedia.org/ontology/SoccerPlayer",
        # 'baseball_players': "http://dbpedia.org/ontology/BaseballPlayer",
        'comedian': "http://dbpedia.org/ontology/Comedian"}

    for s, suri in subjectsPerson.items():
        get_incs_f(s)

