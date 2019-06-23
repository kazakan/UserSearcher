from gevent.pool import Pool
from gevent import monkey
monkey.patch_all()

import requests
import sys
from functools import partial


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

def username_exist_in_service(service,username,link=None):

    _link = None
    if link is not None:
        _link = link.format(username = username)
    else :
        _link = services[service]
        _link = _link.format(username = username)

    # services should be determined by using tricks
    # services which redirect to other page when there's no userinfo
    if service in ['wordpress','weibo']:
        response = requests.get(_link,allow_redirects = False)
        return response.status_code is 200

    elif service is 'steam':
        return False

    elif service is 'pinterest':
        return False

    elif service is 'ebay':
        return False

    elif service is 'wikipedia':
        return False

    # service can be determined by http status code
    else :
        response = requests.get(_link)
        return response.status_code is 200
        

def username_exist_in_services(username,use_gevent=False,service_names = services.keys(),include_none=False):
    result = {}
    if not len(username):
        print("username length is 0")
        return None
        
    # do faster by using gevent
    if use_gevent:
        uei = partial(username_exist_in_service,username = username)

        pol = Pool(len(service_names))
        exists = pol.map(uei, service_names)
        
        i = 0
        for service in service_names:
            if exists[i]:
                result[service] = services[service].format(username = username)
            else:
                if include_none :
                    result[service] = None
            i+=1

    else:
        for service, link in list(filter(lambda x:x[0] in service_names , services.items())):

            exist = False

            try:
                exist = username_exist_in_service(service,username,link)

            except KeyboardInterrupt:
                print("Keyboard Interrupt detected")
                sys.exit()
            except:
                print(service, " Error occured!")
                continue

            if exist:
                result[service]=link.format(username = username)
            else:
                if include_none :
                    result[service]=None

    return result


if __name__ == "__main__":
    username = "dojh99"
    result = username_exist_in_services(username,use_gevent=True)

    print("Search result with username ",username)
    for service, url in result.items():
        print(service, " : ",url)
    