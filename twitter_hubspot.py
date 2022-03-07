import click
import tweepy as tw
import json
from hubspot import HubSpot
from hubspot.auth.oauth import ApiException
from hubspot.crm.contacts import SimplePublicObjectInput
from hubspot.crm.contacts.exceptions import ApiException
#Place all API and Access keys/tokens into a config file and import them into this file
from config import *


@click.group
@click.command
@click.pass_context
def cli():

    pass

@cli.command
def twitter_hubspot():
#Setup a client for the Twitter API v2 and pass it the Bearer Token
    client = tw.Client(bearer_token=BEARER_TOKEN)

    #Ask user for specific query information and number of returned tweets
    query = input('Enter the hashtag to search: ') + ' -is:retweet'
    num_tweets = int(input('How many tweets should be returned?: '))

    #Create a response varaible using the search_recent_tweets method and pass in the user's input parameters
    response = client.search_recent_tweets(
        query=query, 
        max_results=num_tweets, 
        tweet_fields=['lang'], 
        expansions=['author_id']
    )

    #Create a dictionary out of the response variable's "includes" data to make a key value pair of id's and users
    users = {u['id']: u for u in response.includes['users']}
    #Create empty list to append usernames into
    users_list = []

    #Loop through the scraped tweets in the data of the response varaible to append usernames to the users_list
    for tweet in response.data:
        if users[tweet.author_id]:
            user = users[tweet.author_id]
            users_list.append(user.username)


    #Setup client for the Hubspot API
    api_client = HubSpot(api_key=API_KEY)

    #Obtain OAuth2 access token
    try:
        tokens = api_client.auth.oauth.default_api.create_token(
            grant_type="authorization_code",
            redirect_uri='http://localhost',
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            code='code'
        )
            

    except ApiException as e:
        print("Exception when calling create_token method: %s\n" % e)

    #Create HubSpot contact out of the usernames in the users_list
    for user in range(users_list):
        try:
            simple_public_object_input = SimplePublicObjectInput(
            properties={"name": users_list[user]}
        )
            api_response = api_client.crm.contacts.basic_api.create(
                simple_public_object_input=simple_public_object_input
            )
        except ApiException as e:
            print("Exception when creating contact: %s\n" % e)
