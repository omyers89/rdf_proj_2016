from SPARQLWrapper import SPARQLWrapper, JSON
from find_inconsistecies import fix_dbpedia, fix_graphic
import pickle
import sys
import os
import time
import graphp



DBPEDIA_URL = "http://tdk3.csf.technion.ac.il:8890/sparql"
SMAL_URL = "http://cultura.linkeddata.es/sparql"


class miner():

    def __init__(self, kb, subj, s_uri):
        self.knowledge_base = kb
        self.subject = subj
        self.subject_uri = s_uri
        self.sparql = SPARQLWrapper(kb)
        self.RG = graphp.SubjectGraph(s_uri)

    def get_ot_unique_dict(self, o_list, o_dict_t):
        res_dict = {}
        # single= False
        # if len(os) == 1:
        #     single = True
        for o in o_list:
            if o in o_dict_t:
                for t in o_dict_t[o]:

                    #if (t in res_dict) or single:
                    if t in res_dict:
                        res_dict[t] = False #this is the second time t in res_dict so not unique!
                    else:
                        res_dict[t] = True #this is the first time t in res_dict so unique so far!
        return res_dict


    def update_pt(self, t_dict_t,p_unique_t_dict):
        """
        the function count the uniquenes of types for a specific object and add it to the total statistics
        about the property & type
        :param t_dict_t: dictionary for all types that appears together with a specific property and true/false for
        uniqueness
        :param p_unique_t_dict: for every p the total statistics so far
        :return: just update the dictionary.
        """
        for t, v in t_dict_t.items():
            if t not in p_unique_t_dict:
                p_unique_t_dict[t] = {'pos': 0, 'tot': 0}
            if v:
                p_unique_t_dict[t]['pos'] += 1
            p_unique_t_dict[t]['tot'] += 1


    def get_os(self, o_list):
        """
        Given list of object and a specific knowledge base creates a dictionary of o and the list of dbo:type that
        defines it

        :param o_list: list of object for specific relation
        :param db: the KB we query
        :return: o_dict dictionar {'<object>' : [c1,c2,c3...] (type list)
        """

        o_dict = {}
        for o in o_list:
            o_dict[o] = []
            self.sparql.setQuery("""
                                SELECT  DISTINCT  ?c
                                WHERE{
                                    <%s>  a   ?c .
                                    FILTER regex(?c, "^http://dbpedia.org/ontology", "i")
                                }
                            """ % o)

            #need to filter the types to informative ones.
            self.sparql.setReturnFormat(JSON)
            results = self.sparql.query().convert()

            for result in results["results"]["bindings"]:
                c = result["c"]["value"]
                o_dict[o].append(c)

        return o_dict



    def mine_relation_rules(self, quick, min_pos_th=0.2, positive_total_ratio_th=0.8):
        pass
        # print "mining relation_rules for {}".format(self.subject)
        # s_dump_name = self.subject + "/" + self.subject + "_top.dump"
        # p_dump_name = self.subject + "/" + self.subject + "_prop.dump"
        # # get the 100 most popular properties for type person in dbp
        # p_dict = self.get_p_dict_from_dump(quick, p_dump_name)
        # s_dict = self.get_s_dict_from_dump(s_dump_name)
        # rules70_ = []
        # rules60_70 = []
        # rules50_60 = []
        # rules_wierd = []
        # one_of_a_kind = {}
        # progress = 0
        # p_size = len(p_dict)
        # t0 = time.time()
        # pttr_dict = {}
        # for p in p_dict:
        #     #is list of types for every s and p
        #     spt_tuples = get_spts()
        #
        #     spttr_dict = get_ttrs()





    def update_graph(self,s, p , t_dict):
        for t, u in t_dict.items():
            self.RG.add_type_to_prop(p, t, u)

        query_text = ("""
                        SELECT distinct  ?t1 ?r12 ?r21 ?t2
                        WHERE {
                        <%s> <%s> ?o1;
                              <%s> ?o2.
                        FILTER (?o1 < ?o2).
                        ?o1 a ?t1.
                        ?o2 a ?t2.
                        ?o1 ?r12 ?o2.
                        ?o2 ?r21 ?o1.

                        FILTER (regex(?t1, "^http://dbpedia.org/ontology", "i") && (!regex(?t1, "[#]", "i"))).
                        FILTER (regex(?t2, "^http://dbpedia.org/ontology", "i") && (!regex(?t2, "[#]", "i")))

                        FILTER regex(?r12, "^http://dbpedia.org/ontology", "i").
                        FILTER regex(?r21, "^http://dbpedia.org/ontology", "i").
                        FILTER (?t1 != ?t2).
                    }""" % (s, p, p))

        # I figured out that a good filter for the type of the object has to  be of "^http://dbpedia.org/ontology"
        # in oreder to get valuable results
        self.sparql.setQuery(query_text)
        self.sparql.setReturnFormat(JSON)
        results_inner = self.sparql.query().convert()
        for inner_res in results_inner["results"]["bindings"]:
            t1 = inner_res["t1"]["value"]
            t2 = inner_res["t2"]["value"]
            r12 = inner_res["r12"]["value"]
            r21 = inner_res["r21"]["value"]

            self.RG.add_relation(t1,t2,p,r12)
            self.RG.add_relation(t2,t1,p,r21)





    def get_sub_graph(self, s):
        p_dump_name = self.subject + "/" + self.subject + "_prop.dump"
        # get the 100 most popular properties for type person in dbp
        p_dict = self.get_p_dict_from_dump(quick, p_dump_name)
        sinles = {}
        for p in p_dict:
            self.RG.add_prop(p)
            o_list = self.update_so_dict(p, s)
            ot_dict = self.get_os(o_list)
            t_dict = self.get_ot_unique_dict(o_list,
                                             ot_dict)  # Done: for specific person and property find the unique types!
            if len(o_list) == 1:
                sinles[p] = 1
            self.update_graph(s, p, t_dict)

        self.RG.normalize_graph(1, {}, sinles)


    def mine_rules(self, quick, min_pos_th=0.2, positive_total_ratio_th=0.8):
        print "mining rules for {}".format(self.subject)
        s_dump_name = self.subject + "/" + self.subject + "_top.dump"
        p_dump_name = self.subject + "/" + self.subject + "_prop.dump"
        # get the 100 most popular properties for type person in dbp
        p_dict = self.get_p_dict_from_dump(quick, p_dump_name)
        s_dict = self.get_s_dict_from_dump(s_dump_name)
        rules70_ = {}
        rules60_70 = []
        rules50_60= []
        rules_wierd = []
        one_of_a_kind = {}
        progress = 0
        p_size = len(p_dict)
        t0 = time.time()
        for p in p_dict:

            #s_dict = {}
            #this dictionary holds the statistics for every p separately p_unique_t_dict[t]={'pos': #uniqueness, 'tot': #totalappearence}
            p_unique_t_dict = {}
             #s is a sepecific person and os=[o1,o2,o3] is the list of objects that are in the relation: P(s,o)
            #
            p_count = 0
            # for every person in the list (2000 in total)
            p_only_one = 0
            for i,s  in enumerate(s_dict):
                self.RG.add_prop(p)
                o_list = self.update_so_dict(p, s)
                if o_list:
                    p_count += 1
                ot_dict = self.get_os(o_list)
                t_dict = self.get_ot_unique_dict(o_list, ot_dict)  # Done: for specific person and property find the unique types!
                if len(o_list) > 1:
                    #ot_dict is list of types for every o in the list for specific person and property

                    self.update_pt(t_dict,p_unique_t_dict) #Done: add up the times that t was unique for the specific p
                elif len(o_list) == 1:
                    p_only_one += 1

                self.update_graph(s, p , t_dict)

                txt = "\b S loop progress: {}".format(i)
                sys.stdout.write(txt)
                sys.stdout.write("\r")
                sys.stdout.flush()



            sys.stdout.write("\b the total p are : {}".format(p_count))
            sys.stdout.write("\r")
            sys.stdout.flush()

            #print total_totals
            for t, counts in p_unique_t_dict.items():
                pos = float(counts['pos'])
                tot = float(counts['tot'])
                data = {'p': p, 't': t, 'pos': pos, 'tot': tot}
                if tot != 0:
                    data['ratio'] = pos / tot
                t_key = t + '@' + p
                if (tot/p_count) >= min_pos_th:
                #if (tot >= min_pos_th):
                    if ((pos /tot) >= positive_total_ratio_th) :
                        rules70_[t_key](data)
                    elif((pos /tot) >= 0.6):
                        rules60_70.append(data)
                    elif((pos /tot) >= 0.5):
                        rules50_60.append(data)
                else:
                    rules_wierd.append(data)

            if p_count > 0:
                p_once_ratio = float(p_only_one)/p_count
                if  p_once_ratio > 0.9:
                    one_of_a_kind[p] = p_once_ratio

            self.RG.norma_uni_single(len(s_dict), rules70_, one_of_a_kind)

            txt = "\b Properties progress:{} / {} ".format(progress, p_size)
            sys.stdout.write(txt)
            sys.stdout.write("\r")
            sys.stdout.flush()



        all_rules_list = (rules70_ ,rules60_70, rules50_60 ,rules_wierd, one_of_a_kind)

        dir_name = self.subject
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        dump_name = dir_name + "/" + self.subject + "_rules.dump"
        r_dict_file = open(dump_name, 'w')
        pickle.dump(all_rules_list, r_dict_file)
        r_dict_file.close()

        t1 = time.time()
        total_time = t1 - t0
        avg_time = float(total_time) / p_size
        print "get p_rules done, avg time {}".format(avg_time)
        return all_rules_list


    def update_so_dict(self, p, s):


        o_list = []
        query_text = ("""
                    SELECT DISTINCT ?o
                    WHERE{
                            <%s> <%s> ?o .
                            ?o a ?t .
                            FILTER regex(?t, "^http://dbpedia.org/", "i")
                        } """ % (s, p))
        # I figured out that a good filter for the type of the object has to  be of "^http://dbpedia.org/ontology"
        # in oreder to get valuable results
        self.sparql.setQuery(query_text)
        self.sparql.setReturnFormat(JSON)
        results_inner = self.sparql.query().convert()
        for inner_res in results_inner["results"]["bindings"]:
            # s = inner_res["s"]["value"]
            o = inner_res["o"]["value"]

            # if s not in s_dict:
            #   s_dict[s] = []
            o_list.append(o)

        return o_list

    def get_p_dict_from_dump(self, quick, dump_name):


        p_dict_file = open(dump_name, 'r')
        p_dict = pickle.load(p_dict_file)

        p_dict_file.close()
        p_dict_ret = {}
        if quick:
            for i,p in enumerate(p_dict):
                p_dict_ret[p] = 0
                if i > 15 :
                    return p_dict_ret



        return p_dict


    def get_s_dict_from_dump(self, dump_name):

        s_dict_file = open(dump_name, 'r')
        s_dict = pickle.load(s_dict_file)

        s_dict_file.close()
        return s_dict


    def get_p_dict(self,quick, uri):

        p_dict = {}
        if quick:

            p_dict["http://dbpedia.org/ontology/birthPlace"] = 0
            #p_dict["http://dbpedia.org/ontology/residence"] = 0
        else:
            query_text = ("""
                SELECT ?p (COUNT (?p) AS ?cnt)
                WHERE {
                    {
                    SELECT DISTINCT ?s
                    WHERE {
                        ?s a <%s>.
                    }LIMIT 500000
                    }
                    ?s ?p ?o
                    FILTER regex(?p, "^http://dbpedia.org/", "i")
                }GROUP BY ?p
                 ORDER BY DESC(?cnt)
                 LIMIT 100
                """ % uri)
            self.sparql.setQuery(query_text)
            self.sparql.setReturnFormat(JSON)
            results_inner = self.sparql.query().convert()

            for inner_res in results_inner["results"]["bindings"]:
                p = inner_res["p"]["value"]
                # cnt = inner_res["cnt"]["value"]
                p_dict[p] = 0
        p_dict_file = open('p_dict.dump', 'w')
        pickle.dump(p_dict, p_dict_file)
        p_dict_file.close()
        print "get p_dict done"
        return p_dict


if __name__ == '__main__':
    quick = True
    # choice = raw_input("quick or full")
    # if choice == "full":
    #     quick = False

    db = DBPEDIA_URL
    # choice = raw_input("dbpedia or small")
    # if choice == "small":
    #     db = SMAL_URL

    # min_pos_th = float(raw_input("enter the th weird rules \n"))
    # positive_total_ratio_th = float(raw_input("enter the th for good rules rules \n"))

    subjectsf = {'person': "http://dbpedia.org/ontology/Person",
                'Event': "http://dbpedia.org/ontology/Event",
                'Location': "http://dbpedia.org/ontology/Location",
                'Organisation': "http://dbpedia.org/ontology/Organisation",
                'Manga': "http://dbpedia.org/ontology/Manga",
                'Animal': "http://dbpedia.org/ontology/Animal",
                'Mammal': "http://dbpedia.org/ontology/Mammal",
                'Eukaryote': "http://dbpedia.org/ontology/Eukaryote",
                'Software': "http://dbpedia.org/ontology/Software",
                'Play': "http://dbpedia.org/ontology/Play"}

    subjects = {'person': "http://dbpedia.org/ontology/Person",
                # 'Manga': "http://dbpedia.org/ontology/Manga",
                # 'Animal': "http://dbpedia.org/ontology/Animal",
                # 'Mammal': "http://dbpedia.org/ontology/Mammal",
                'Software': "http://dbpedia.org/ontology/Software"}
    subjectsPerson = {  # 'personn': "http://dbpedia.org/ontology/Person",
        'politician': "http://dbpedia.org/ontology/Politician",
        # 'soccer_player': "http://dbpedia.org/ontology/SoccerPlayer",
        # 'baseball_players': "http://dbpedia.org/ontology/BaseballPlayer",
        'comedian': "http://dbpedia.org/ontology/Comedian"}
        # 'architectural_structure': "http://dbpedia.org/ontology/ArchitecturalStructure"}
    for s, suri in subjectsPerson.items():
        mm = miner(db,s, suri)
        all_rules = mm.mine_rules( quick,  min_pos_th=0.2, positive_total_ratio_th=0.8)
        GG = mm.RG
        dump_name = s + "/" + s + "_pg.dump"
        g_file = open(dump_name, 'w')
        pickle.dump(GG, g_file)
        g_file.close()
        try:
            fix_graphic(db,s, suri, GG)
        except:
            print "got a problem at: " + s
