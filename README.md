## Recommender for Event Based Social Network ##

It is of utmost importance in today's world that an event based social network use recommenders to suggest relevant and interesting events to its users which help them choose between various events. Therefore, this is a system for recommending events to users based on their previous activities. It is based on "Context-Aware Event Recommendation in Event-based Social Networks" paper by Augusto Q. Macedo, Leandro B. Marinho and Rodrygo L. T. Santos. We have collected data from Meetup.com for four cities, namely, SanJose, Phoenix, Chicago and College Station. The main problem in working on event recommendation is the cold-start problem. We do not know which events will the user actually attend. This eliminates the use of simple collaborative filtering and latent factor models.

Hence, we are using the context knowledge to handle the cold start problem. Context knowledge can include temporal preferences, the set of groups the user can join, the users' geographic preferences and textual content of events. More specifically, we have used Social Aware, Content Aware, Location Aware, and Time Aware as features of the algorithm. Based on these we apply a Learning To Rank algorithms to obtain recommendations.

To evaluate our data, we have divided the dataset into two timelines. The first timeline will be used to train the model and the second dataset has been used to test on this data. The prediction have been compared to the actual data using Precision and Recall.

## DataSet ##
We used meetup data for 3 cities, namely, Chicago, Phoenix, and San Jose.

Data is present at following link:-
https://drive.google.com/drive/u/1/folders/0B-pIiXWw_X8RTllOSGtYYXFuSmM