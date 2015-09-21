import tweepy
import urllib, cStringIO

from PIL import Image

from django.shortcuts import render_to_response,render,redirect
from django.http.response import HttpResponse
from django.contrib import messages
from django.core.context_processors import csrf
from tweepy.error import TweepError

from collage.settings import consumer_key,consumer_secret,access_token,access_token_secret


def home(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('base.html',c)

def make_collage(request):  
    if request.method == "POST":
        screen_name = request.POST.get('screen_name')
        width = int(request.POST.get('width'))
        height = int(request.POST.get('height'))

        #twi api
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)

        try:
            ids = api.friends_ids(screen_name=screen_name)
        except TweepError:
            return redirect("/")

        urls = []
        for i in xrange(0,len(ids[0:width*height]),100):
            friend_info = api.lookup_users(user_ids=ids[i:i+100])
            for friend in friend_info:
                urls.append(friend.profile_image_url)

        def _images(url_list):
            urls = url_list
            for url in urls:
                try:
                    img = Image.open(cStringIO.StringIO(urllib.urlopen(url).read()))
                    yield img
                except IOError:
                    pass

        images = _images(urls)
        collage = Image.new('RGBA', (48*width,48*height), 'white')
        for row in xrange(height):
            for column in xrange(width):
                try:
                    collage.paste(images.next(),(column*48,row*48))
                except StopIteration:
                    break
        collage.save('collage_app/static/collage.png')
        return redirect("/collage")
    else:
        return redirect("/")

def collage(request):
    return render_to_response('image.html')
