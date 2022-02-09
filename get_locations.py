import argparse
import emoji
import json
import re


def match_locations(users2match, location_2match):
    users_found = dict()
    users_notfound = dict()
    for u in users2match:
        found = 0
        end = 0
        while found == 0 and end == 0:
            for k in location_2match:
                if k != '':
                    if found == 0:
                        if type(users2match[u]) != list:
                            if k in users2match[u].lower():                     
                                found = 1                           
                                users_found[u] = location_2match[k]
            end = 1

        if found == 0:
            users_notfound[u] = users2match[u]

    return(users_found, users_notfound)

def remove_accents(name):
    name = re.sub('á','a', name)
    name = re.sub('é','e', name)
    name = re.sub('í','i', name)
    name = re.sub('ó','o', name)
    name = re.sub('ú','u', name)
    name = re.sub('ý','y', name)
    name = re.sub('à','a', name)
    name = re.sub('è','e', name)
    name = re.sub('ì','i', name)
    name = re.sub('ò','o', name)
    name = re.sub('ù','u', name)
    name = re.sub('ä','a', name)
    name = re.sub('ë','e', name)
    name = re.sub('ï','i', name)
    name = re.sub('ö','o', name)
    name = re.sub('ü','u', name)
    name = re.sub('ÿ','y', name)
    name = re.sub('â','a', name)
    name = re.sub('ê','e', name)
    name = re.sub('î','i', name)
    name = re.sub('ô','o', name)
    name = re.sub('û','u', name)
    name = re.sub('ã','a', name)
    name = re.sub('õ','o', name)
    name = re.sub('ñ','n', name)
        
    return name

def annotate_locations(input_filepath):
    index = 0
    found = dict()
    allusers = dict()

    # Read input json lines
    with open(input_filepath, 'r') as f:
        for line in f:
            line = line.replace("\n", "")
            line = line.strip()
            a = json.loads(line)
            allusers[a['user']['id_str']] = a['user']['location']

            if 'retweeted_status' in a:
                allusers[a['retweeted_status']['user']['id_str']] = a['retweeted_status']['user']['location']
            if 'quoted_status' in a:
                allusers[a['quoted_status']['user']['id_str']] = a['quoted_status']['user']['location']   

    # Create lists of places in dicts where key is the name of the place and the state code is the value 
    # of the corresponding dict. For cities you can adjust the threshold of inhabitants instead
    countries = dict()
    with open("resources/country_acronyms.tsv", 'r') as f:
        for line in f:
            line = line.replace("\n", "")
            line = line.strip()
            parts = line.split('\t')
            countries[parts[1].lower()] = parts[3].lower()
            countries[parts[0].lower()] = parts[3].lower()
    countries['deutschland'] = 'de'
    countries['italia'] = 'it'
    countries['españa'] = 'es'
    countries['bayern'] = 'de'
    countries['suisse'] = 'ch'
    countries['belgique'] = 'be'

    cities = dict()
    first = 0
    with open("resources/world_cities.csv", 'r') as f:
        for line in f:
            line = line.replace("\n", "")
            line = line.strip()
            parts = line.split('","')   

            if first == 0:
                first = 1
                continue

            try:
                if (int(parts[9])) > 500000: 
                    cities[parts[0].lower().replace('"', '')] = parts[5].lower()
                    cities[parts[1].lower().replace('"', '')] = parts[5].lower()
                    cities[parts[7].lower().replace('"', '')] = parts[5].lower()
            except:
                pass

    try:                
        del cities['']
    except:
        pass

    with open("resources/other_places.tsv", 'r') as f:
        for line in f:
            line = line.replace("\n", "")
            line = line.strip()
            parts = line.split('\t')    
            cities[parts[0].lower().replace('"', '')] = parts[1]

    # Do the matches: look first for state (more reliable due to the fact that there are no synonyms), 
    # than cities. After that, transform emojis and look again for states and countries
    print('tot users: '+str(len(allusers)))

    users_found_firstit, users_notfound_firstit = match_locations(allusers, countries)
    print('users found by matching states: ' + str(len(users_found_firstit)))
    print('users still missing: ' + str(len(users_notfound_firstit)))

    users_found_secondit, users_notfound_secondit = match_locations(users_notfound_firstit, cities)
    print('users found by matching cities+others: ' + str(len(users_found_secondit)))
    print('users still missing: ' + str(len(users_notfound_secondit)))

    # Try the same on remaining users after transforming emojis
    users_notfound_secondit_emoji = dict()
    for u in users_notfound_secondit:
        users_notfound_secondit_emoji[u] = emoji.demojize(users_notfound_secondit[u])
        users_notfound_secondit_emoji[u] = users_notfound_secondit_emoji[u].replace('_', ' ')
        users_notfound_secondit_emoji[u] = remove_accents(users_notfound_secondit_emoji[u])

    users_found_thirdit_emoji, users_notfound_thirdit_emoji = match_locations(
        users_notfound_secondit_emoji, countries)
    users_found_forthit_emoji, users_notfound_forthit_emoji = match_locations(
        users_notfound_thirdit_emoji, cities)
    print('users found by transforming emoji and removing accents: ' + 
        str(len(users_found_thirdit_emoji) + len(users_found_forthit_emoji)))
    print('users still missing: ' + str(len(users_notfound_forthit_emoji)))

    f_out = open('results.tsv', 'w')
    for u in users_found_firstit:
        f_out.write(u + '\t' + allusers[u].rstrip("\n") + '\t' + users_found_firstit[u] + '\tfirstit\n')
    for u in users_found_secondit:
        f_out.write(u + '\t'+ allusers[u].rstrip("\n") + '\t' + users_found_secondit[u] + '\tsecit\n')
    for u in users_found_thirdit_emoji:
        f_out.write(u + '\t' + allusers[u].rstrip("\n") + '\t' + users_found_thirdit_emoji[u] + '\tthirdit\n')
    for u in users_found_forthit_emoji:
        f_out.write(u + '\t' + allusers[u].rstrip("\n") + '\t' + users_found_forthit_emoji[u] + '\tfourthit\n')
    f_out.close()

    # Counts and statistics
    population = dict()
    first = 1
    with open("resources/country_population_statistics.csv", 'r') as f:
        for line in f:
            line = line.replace("\n", "")
            line = line.strip()
            parts = line.split(',')
            parts_2 = line.split('"')
            if first == 1:
                first = 0
                continue
            population[parts[2].lower()] = parts_2[1].replace(",", '')
    
    count = dict()
    with open("results.tsv", 'r') as f:
        for line in f:
            line = line.replace("\n", "")
            line = line.strip()
            parts = line.split('\t')
            try:
                count[parts[2]] = count[parts[2]] + 1
            except:
                count[parts[2]] = 1

    countries = dict()
    with open("resources/country_acronyms_transform.tsv", 'r') as f:
        for line in f:
            line = line.replace("\n", "")
            line = line.strip()
            parts = line.split('\t')
            countries[parts[3].lower()] = parts[5]

    f_out_pop = open('results_weighted.tsv', 'w')
    f_out = open('results_absolute.tsv', 'w')
    for c in count:
        try:
            f_out_pop.write(str(countries[c]) + '\t' + 
                str(round(int(count[c]) / int(population[c]) * 10000000)) + '\n')
            f_out.write(str(countries[c]) + '\t' + str(round(int(count[c]))) + '\n')
        except:
            pass
    f_out.close()
    f_out_pop.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-I", "--input_filepath", type=str, required=True, 
        help="The path to the json line file with tweets.")
    args = parser.parse_args()

    annotate_locations(args.input_filepath)
