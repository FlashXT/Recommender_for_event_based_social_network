from preprocessing import *
import argparse
from partition import *
from content.content_recommender import ContentRecommender
from temporal.time_recommender import TimeRecommender
from location.location_recommender import LocationRecommender
from group_frequency.grp_freq_recommender import GrpFreqRecommender
from hybrid.learning_to_rank import LearningToRank
import datetime
import time
import numpy as np

train_data_interval = ((364 / 2) * 24 * 60 * 60)

def content_classifier(repo, timestamp, simscores, test_members):
    #Wrapper for content classification.
    #call train and test for all member and
    #events and print the results

    training_events_dict = get_member_events_dict_in_range(repo, timestamp - train_data_interval, timestamp)

    potential_events = filter_events_by_time_range(repo, list(repo['events_info'].keys()), timestamp,
                                                   timestamp + train_data_interval)

    contentRecommender = ContentRecommender()
    contentRecommender.train(training_events_dict, repo)

    test_events_vec = contentRecommender.get_test_events_wth_description(repo, potential_events)

    for member in test_members:
    #TEST: Call test only for member_id 12563492
        contentRecommender.test(member, potential_events, test_events_vec, simscores)

    # for member_id in repo['members_info']:
    #     contentRecommender.test(member_id, potential_events, test_events_vec, simscores)

def get_json_file(filename):

    if not os.path.exists(filename):
        return {}

    json_file = open(filename)
    json_str = json_file.read()
    return json.loads(json_str)

def time_classifier(repo, timestamp, simscores, test_members):

    training_events_dict = get_member_events_dict_in_range(repo, timestamp - train_data_interval, timestamp)

    timeRecommender = TimeRecommender()
    timeRecommender.train(training_events_dict, repo)

    potential_events = filter_events_by_time_range(repo, list(repo['events_info'].keys()), timestamp,
                                                   timestamp + train_data_interval)

    test_events_vec = timeRecommender.get_test_event_vecs_with_time(repo, potential_events)

    #TEST: Call test only for member_id 12563492
    timeRecommender.test('12563492', potential_events, test_events_vec, simscores)
    # for member_id in repo['members_info']:
    #     timeRecommender.test(member_id, potential_events, test_events_vec, simscores)

def loc_classifier(repo, timestamp, simscores, test_members):
    training_events_dict = get_member_events_dict_in_range(repo, timestamp - train_data_interval, timestamp)
    locationRecommender = LocationRecommender()
    locationRecommender.train(training_events_dict, repo)
    potential_events = filter_events_by_time_range(repo, list(repo['events_info'].keys()), timestamp,
                                                   timestamp + train_data_interval)

    #TEST: Call test only for memeber_id 12563492
    locationRecommender.test('12563492', potential_events, repo, simscores)
    # for member_id in repo['members_info']:
    #     locationRecommender.test(member_id, potential_events, repo, simscores)

def grp_freq_classifier(repo, timestamp, simscores, test_members):
    training_events_dict = get_member_events_dict_in_range(repo, timestamp - train_data_interval, timestamp)
    grp_freq_recommender = GrpFreqRecommender()
    grp_freq_recommender.train(training_events_dict, repo)
    potential_events = filter_events_by_time_range(repo, list(repo['events_info'].keys()), timestamp,
                                                   timestamp + train_data_interval)
    #TEST: Call test only for memeber_id 12563492
    grp_freq_recommender.test('12563492', potential_events, repo, simscores)
    # for member_id in repo['members_info']:
    #     grp_freq_recommender.test(member_id, potential_events, repo, simscores)

def learning_to_rank(simscores_across_features, events, members, hybrid_simscores):
    learningToRank = LearningToRank()

    learningToRank.learning_to_rank(simscores_across_features, events, members, hybrid_simscores)

def create_json_file(dictionary, filename):
    json_repr = json.dumps(dictionary)
    f = open(filename, "w+")
    f.write(json_repr)
    f.close()

def main():
    parser = argparse.ArgumentParser(description='Run Event Recommender')
    parser.add_argument('--city', help='Enter the city name')
    args = parser.parse_args()

    city = args.city
    group_members, group_events, event_group = load_groups("../crawler/cities/" + city + "/group_members.json",
                                                            "../crawler/cities/" + city + "/group_events.json")
    events_info = load_events("../crawler/cities/" + city + "/events_info.json")
    members_info = load_members("../crawler/cities/" + city + "/members_info.json")
    member_events = load_rsvps("../crawler/cities/" + city + "/rsvp_events.json")

    repo = dict()
    repo['group_events'] = group_events
    repo['group_members'] = group_members
    repo['events_info'] = events_info
    repo['members_info'] = members_info
    repo['members_events'] = member_events
    repo['event_group'] = event_group

    #simscores_across_features is a dictionary to store similarity score obtained for each feature
    #for each member and for a given event. For example in case of content classifer we will
    #access the similarity score as follows: simscores['content_classifier'][member_id][event_id].
    #We will pass only a specific subdictionary (Ex: simscores['content_classifier']) to the
    #classifier functions, which will work on them and populate them.
    simscores_across_features = defaultdict(lambda :defaultdict(lambda :defaultdict(lambda :0)))
    hybrid_simscores = defaultdict(lambda :defaultdict(lambda :0))

    start_time = 1262304000 # 1st Jan 2010
    end_time = 1388534400 # 1st Jan 2014
    timestamps = get_timestamps(start_time, end_time)
    timestamps = sorted(timestamps, reverse=True)

    for t in timestamps:
        start_time = t - train_data_interval
        end_time = t + train_data_interval
        test_members = []
        f = open("scripts/"+city + "_best_users_" + str(start_time) + "_" + str(end_time) + ".txt", "r")
        for id in f:
            test_members.append(id)
        f.close()

        print "Partition at timestamp ", datetime.datetime.fromtimestamp(t), " are : "
        partitioned_repo = get_partitioned_repo(t, repo)

        print "Partitioned Repo retrieved for timestamp : ", datetime.datetime.fromtimestamp(t)

        #Call content based classifer train and test functions from here. Pass the repo
        #as an argument to these functions.
        start = time.clock()
        print "Starting Content Classifier"
        content_classifier(partitioned_repo, t, simscores_across_features['content_classifier'], test_members)
        print "Completed Content Classifier in ", time.clock() - start, " seconds"

        start = time.clock()
        print "Starting Time Classifier"
        time_classifier(partitioned_repo, t, simscores_across_features['time_classifier'], test_members)
        print "Completed Time Classifier in ", time.clock() - start, " seconds"

        start = time.clock()
        print "Starting Location Classifier"
        loc_classifier(partitioned_repo, t, simscores_across_features['location_classifier'], test_members)
        print "Completed Location Classifier in ", time.clock() - start, " seconds"

        start = time.clock()
        print "Starting Group Frequency Classifier"
        grp_freq_classifier(partitioned_repo, t, simscores_across_features['grp_freq_classifier'], test_members)
        print "Completed Group Frequency Classifier in ", time.clock() - start, " seconds"

        learning_to_rank(simscores_across_features, partitioned_repo["events_info"].keys(), partitioned_repo["members_info"].keys(), hybrid_simscores)


if __name__ == "__main__":
    main()