import argparse
import requests
import sys
from functools import partial
from multiprocessing import Pool
import asyncio
import time

# 'service name' : "link"
services = {
    'facebook': "https://www.facebook.com/{username}/",
    'instagram': "https://www.instagram.com/{username}",
    'twitter': "https://www.twitter.com/{username}",
    'youtube': "https://www.youtube.com/{username}",
    'blogger': "https://{username}.blogspot.com",
    'gooogle_plus': "https://plus.google.com/+{username}/posts",
    'reddit': "https://www.reddit.com/user/{username}",  
    'wordpress': "https://{username}.wordpress.com", # not 404, redirected
    'github': "https://www.github.com/{username}",
    'bitbucket': "https://bitbucket.org/{username}/",
    'tumblr': "https://{username}.tumblr.com",  
    'steam': "https://steamcommunity.com/id/{username}", # not 404
    'naver': "https://blog.naver.com/{username}",
    'pinterest': "https://www.pinterest.com/{username}",  # return 404 at different link
    'flicker': "https://www.flickr.com/people/{username}",
    'vimeo': "https://vimeo.com/{username}",
    'soundcloud': "https://soundcloud.com/{username}",
    'disqus': "https://disqus.com/{username}",
    'medium': "https://medium.com/@{username}",
    'devianart': "https://{username}.deviantart.com",
    'vk': "https://vk.com/{username}",
    'imgur': "https://imgur.com/user/{username}",
    #'flipboard': "https://flipboard.com/@{username}",
    'slideshare': "https://slideshare.net/{username}",
    'spotify': "https://open.spotify.com/user/{username}",
    'badoo': "https://www.badoo.com/en/{username}",
    'patreon': "https://www.patreon.com/{username}",
    'dailymotion': "https://www.dailymotion.com/{username}",
    'etsy': "https://www.etsy.com/shop/{username}",
    'cashme': "https://cash.me/{username}",
    'behance': "https://www.behance.net/{username}",
    'goodreads': "https://www.goodreads.com/{username}",
    'instructable': "https://www.instructables.com/member/{username}",
    'keybase': "https://keybase.io/{username}", 
    'roblox': "https://www.roblox.com/user.aspx?username={username}",
    'wikipedia': "https://www.wikipedia.org/wiki/User:{username}", # not 404
    'ebay': "https://www.ebay.com/usr/{username}",  # not 404
    'slack': "https://{username}.slack.com",
    'okcupid': "https://www.okcupid.com/profile/{username}",
    'weibo': "https://www.weibo.com/{username}"  # not 404
}

def get(link,allow_redirects = True):
    return requests.get(link,allow_redirects=allow_redirects)

async def username_exist_in_service(service,username,link=None):

    _link = None
    if link is not None:
        _link = link.format(username = username)
    else :
        _link = services[service]
        _link = _link.format(username = username)

    loop = asyncio.get_running_loop()

    # services should be determined by using tricks
    # services which redirect to other page when there's no userinfo
    if service in ['wordpress','weibo']:
        response = await loop.run_in_executor(None,get,_link, False)
        return response.status_code == 200

    elif service == 'steam':
        return False

    elif service == 'pinterest':
        return False

    elif service == 'ebay':
        return False

    elif service == 'wikipedia':
        return False

    # service can be determined by http status code
    else :
        response = await loop.run_in_executor(None,get,_link)
        return response.status_code == 200
        

async def username_exist_in_services(username,service_names = services.keys(),include_none=False):
    result = {}
    if not len(username):
        print("username length is 0")
        return None
        
    uei = partial(username_exist_in_service,username = username)

    exists_future = [asyncio.ensure_future(uei(service_name)) for service_name in service_names]
    exists = await asyncio.gather(*exists_future)
    
    for i, service in enumerate(service_names):
        if exists[i]:
            result[service] = services[service].format(username = username)
        else:
            if include_none :
                result[service] = None

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='UserSearcher')
    parser.add_argument('username',help='Username to search.')
    args = parser.parse_args()

    username = args.username

    t1 = time.time()
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(username_exist_in_services(username))
    loop.close()

    print("Search result with username ",username)
    for service, url in result.items():
        print(service, " : ",url)

    t2 = time.time()
    print("Done in : " ,t2-t1)
    