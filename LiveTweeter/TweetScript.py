import sys
import base64
try:
    import requests # pip install requests
except:
    print(encodeBlueprint({
        "scriptStatus": "Error",
        "statusCode": -2}))
    sys.exit(0)
try:
    from requests_oauthlib import OAuth1 # pip install requests_oauthlib
except:
    print(encodeBlueprint({
        "scriptStatus": "Error",
        "statusCode": -3}))
    sys.exit(0)
import zlib, json
import collections
import os

path = os.path.dirname(__file__)

def decodeBlueprint(blueprintString):
    version_byte = blueprintString[0]
    decoded = base64.b64decode(blueprintString[1:])    
    # json_str = zlib.decompress(decoded) # python 2 version
    json_str = zlib.decompress(decoded).decode('utf-8') # python 2 and 3 version
    data = json.loads(json_str, object_pairs_hook=collections.OrderedDict)
    return data

def encodeBlueprint(data, level=6):
    json_str = json.dumps(data, ensure_ascii=False)
    encoded = zlib.compress(json_str.encode('utf-8'), level)
    blueprintString = base64.b64encode(encoded)
    return "0" + blueprintString


if __name__ == "__main__":
    # read arguments from commandline
    encodedTweetData = "".join(sys.argv[1:])
    tweetData = decodeBlueprint(encodedTweetData)


    # postUrl = "https://api.twitter.com/1.1/statuses/update.json"
    # removeUrl = "https://api.twitter.com/1.1/statuses/destroy/{}.json"
    auth = OAuth1(
        tweetData["consumer_key"].strip(),
        tweetData["consumer_secret"].strip(), 
        tweetData["access_token"].strip(),
        tweetData["access_token_secret"].strip())
    
    if tweetData["action"] == "SendTweet":
        r = requests.post(tweetData["url"], auth=auth, data={"status": tweetData["tweetText"]})   
    elif tweetData["action"] == "RemoveTweet":
        r = requests.post(tweetData["url"], auth=auth, data={})    

    try:
        if r.status_code == 200:
            response = r.json()
            response["scriptStatus"] = "Success"
            response["statusCode"] = r.status_code
            print(encodeBlueprint(response))
        else:        
            response = {
                "scriptStatus": "Error",
                "statusCode": r.status_code, 
            }
            print(encodeBlueprint(response))
    except Exception as e:
        response = {
                "scriptStatus": "Error",
                "statusCode": -4, 
                "statusText": e, 
            }
        # with open(os.path.join(path, "tempTweetScriptOutput.json"), mode="w") as f:
        #     json.dump(response, f, indent=4)
        print(encodeBlueprint(response))

    sys.exit(0)










