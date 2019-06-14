"""A Yelp-powered Restaurant Recommendation Program"""

from abstractions import *
from data import ALL_RESTAURANTS, CATEGORIES, USER_FILES, load_user_file
from ucb import main, trace, interact
from utils import distance, mean, zip, enumerate, sample
from visualize import draw_map

##################################
# Phase 2: Unsupervised Learning #
##################################


def find_closest(location, centroids):
    """Return the centroid in centroids that is closest to location.
    If multiple centroids are equally close, return the first one.

    >>> find_closest([3.0, 4.0], [[0.0, 0.0], [2.0, 3.0], [4.0, 3.0], [5.0, 5.0]])
    [2.0, 3.0]
    """
    # BEGIN Question 3
    "*** YOUR CODE HERE ***"
    def distances_of_centroids(x):
        return distance(location, x) #get the distance

    return min(centroids, key=distances_of_centroids) #distances_of_centroids is applied onto each separate element of centroids
        #get the minimum distance at the end
    # END Question 3


def group_by_first(pairs):
    """Return a list of lists that relates each unique key in the [key, value]
    pairs to a list of all values that appear paired with that key.

    Arguments:
    pairs -- a sequence of pairs

    >>> example = [ [1, 2], [3, 2], [2, 4], [1, 3], [3, 1], [1, 2] ]
    >>> group_by_first(example)  # Values from pairs that start with 1, 3, and 2 respectively
    [[2, 3, 2], [2, 1], [4]]
    """
    keys = []
    for key, _ in pairs:
        if key not in keys:
            keys.append(key)
    return [[y for x, y in pairs if x == key] for key in keys]


def group_by_centroid(restaurants, centroids):
    """Return a list of clusters, where each cluster contains all restaurants
    nearest to a corresponding centroid in centroids. Each item in
    restaurants should appear once in the result, along with the other
    restaurants closest to the same centroid.
    """
    # BEGIN Question 4
    "*** YOUR CODE HERE ***"

    rest_locations = [restaurant_location(x) for x in restaurants] #get the restaurant locations
    closest_locations = [find_closest(k, centroids) for k in rest_locations] #get the closest centroids for each restaurant location

#NOTE: use ZIP to combine the closest_locations and restaurants to get a list of lists, that I will group_by_centroid
    combined_list = zip(closest_locations, restaurants)#look out: match up closest_locations with restaurant
    grouped_list = group_by_first(combined_list) # group_by_first helps me group the list of restuarants that share the same centroid

    return grouped_list
    # END Question 4


def find_centroid(cluster):
    """Return the centroid of the locations of the restaurants in cluster."""
    # BEGIN Question 5
    "*** YOUR CODE HERE ***"

    x_values = [restaurant_location(x)[0] for x in cluster] #BE AWARE OF ABSTRACTION BARRIERS!!!
    y_values = [restaurant_location(y)[1] for y in cluster]

    latitude = mean(x_values)
    longitude = mean(y_values)

    return [latitude, longitude]
    # END Question 5


def k_means(restaurants, k, max_updates=100):
    """Use k-means to group restaurants by location into k clusters."""
    assert len(restaurants) >= k, 'Not enough restaurants to cluster'
    old_centroids, n = [], 0

    # Select initial centroids randomly by choosing k different restaurants
    centroids = [restaurant_location(r) for r in sample(restaurants, k)]

    while old_centroids != centroids and n < max_updates:
        old_centroids = centroids
        # BEGIN Question 6
        "*** YOUR CODE HERE ***"
        rest_clusters = group_by_centroid(restaurants, old_centroids)
        centroids = [find_centroid(c) for c in rest_clusters] #find_centroid takes in 1 cluster, apply it to each element in rest_clusters
        # END Question 6
        n += 1
    return centroids


################################
# Phase 3: Supervised Learning #
################################


def find_predictor(user, restaurants, feature_fn):
    """Return a rating predictor (a function from restaurants to ratings),
    for a user by performing least-squares linear regression using feature_fn
    on the items in restaurants. Also, return the R^2 value of this model.

    Arguments:
    user -- A user
    restaurants -- A sequence of restaurants
    feature_fn -- A function that takes a restaurant and returns a number
    """
    xs = [feature_fn(r) for r in restaurants]
    ys = [user_rating(user, restaurant_name(r)) for r in restaurants]

    # BEGIN Question 7
    "*** YOUR CODE HERE ***"
    S_xx = sum([(x - mean(xs))**2 for x in xs]) #get the summation of mse's for each x in xs
    S_yy = sum([(y - mean(ys))**2 for y in ys])#get the summation of mse's for each y in ys
    x_y_mse_list = zip([x - mean(xs) for x in xs], [y - mean(ys) for y in ys]) #create a new list that combines the x and y errors from zip
    S_xy = sum(x*y for x,y in x_y_mse_list) #extract the x and y values from each list element in x_y_mse_list and multiply them together

    b =  S_xy / S_xx
    a = mean(ys) - b * mean(xs)
    r_squared = S_xy**2 / (S_xx * S_yy)

    # END Question 7

    def predictor(restaurant):
        return b * feature_fn(restaurant) + a

    return predictor, r_squared #returns a tuple of predictor, r_squared


def best_predictor(user, restaurants, feature_fns):
    """Find the feature within feature_fns that gives the highest R^2 value
    for predicting ratings by the user; return a predictor using that feature.

    Arguments:
    user -- A user
    restaurants -- A list of restaurants
    feature_fns -- A sequence of functions that each takes a restaurant
    """
    reviewed = user_reviewed_restaurants(user, restaurants)
    # BEGIN Question 8
    "*** YOUR CODE HERE ***"
    tuple_list = []
    for f in feature_fns:
        tuple_list.append(find_predictor(user, reviewed, f)) #create a list of tuples

    highest_tuple = max(tuple_list, key=lambda x: x[1]) #extract the max tuple that contains the highest [predictor, r_squared_value]

    return highest_tuple[0] #get the predictor item
    # END Question 8


def rate_all(user, restaurants, feature_fns):
    """Return the predicted ratings of restaurants by user using the best
    predictor based on a function from feature_fns.

    Arguments:
    user -- A user
    restaurants -- A list of restaurants
    feature_fns -- A sequence of feature functions
    """
    predictor = best_predictor(user, ALL_RESTAURANTS, feature_fns)
    reviewed = user_reviewed_restaurants(user, restaurants)
    # BEGIN Question 9
    "*** YOUR CODE HERE ***"
    dictionary = {}
    for restaurant in restaurants: #analyze all the restuarants
        if restaurant in reviewed: #look for restuarants reviewed by the user
            dictionary[restaurant_name(restaurant)] = user_rating(user, restaurant_name(restaurant))
        else:           #append onto the dictionary by extracting the element and setting it equal to a value
            dictionary[restaurant_name(restaurant)] = predictor(restaurant)

    return dictionary
    # END Question 9


def search(query, restaurants):
    """Return each restaurant in restaurants that has query as a category.

    Arguments:
    query -- A string
    restaurants -- A sequence of restaurants
    """
    # BEGIN Question 10
    "*** YOUR CODE HERE ***"

    query_restaurants = []
    for r in restaurants: #analyze each restaurant
        if query in restaurant_categories(r): #if my query matches with a category per restaurant
            query_restaurants.append(r) 

    return query_restaurants
    # END Question 10


def feature_set():
    """Return a sequence of feature functions."""
    return [lambda r: mean(restaurant_ratings(r)),
            restaurant_price,
            lambda r: len(restaurant_ratings(r)),
            lambda r: restaurant_location(r)[0],
            lambda r: restaurant_location(r)[1]]


@main
def main(*args):
    import argparse
    parser = argparse.ArgumentParser(
        description='Run Recommendations',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-u', '--user', type=str, choices=USER_FILES,
                        default='test_user',
                        metavar='USER',
                        help='user file, e.g.\n' +
                        '{{{}}}'.format(','.join(sample(USER_FILES, 3))))
    parser.add_argument('-k', '--k', type=int, help='for k-means')
    parser.add_argument('-q', '--query', choices=CATEGORIES,
                        metavar='QUERY',
                        help='search for restaurants by category e.g.\n'
                        '{{{}}}'.format(','.join(sample(CATEGORIES, 3))))
    parser.add_argument('-p', '--predict', action='store_true',
                        help='predict ratings for all restaurants')
    parser.add_argument('-r', '--restaurants', action='store_true',
                        help='outputs a list of restaurant names')
    args = parser.parse_args()

    # Output a list of restaurant names
    if args.restaurants:
        print('Restaurant names:')
        for restaurant in sorted(ALL_RESTAURANTS, key=restaurant_name):
            print(repr(restaurant_name(restaurant)))
        exit(0)

    # Select restaurants using a category query
    if args.query:
        restaurants = search(args.query, ALL_RESTAURANTS)
    else:
        restaurants = ALL_RESTAURANTS

    # Load a user
    assert args.user, 'A --user is required to draw a map'
    user = load_user_file('{}.dat'.format(args.user))

    # Collect ratings
    if args.predict:
        ratings = rate_all(user, restaurants, feature_set())
    else:
        restaurants = user_reviewed_restaurants(user, restaurants)
        names = [restaurant_name(r) for r in restaurants]
        ratings = {name: user_rating(user, name) for name in names}

    # Draw the visualization
    if args.k:
        centroids = k_means(restaurants, min(args.k, len(restaurants)))
    else:
        centroids = [restaurant_location(r) for r in restaurants]
    draw_map(centroids, restaurants, ratings)
