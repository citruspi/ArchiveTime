#/usr/bin/python
#
# -*- coding: utf-8 -*-


"""Tumblr Indexing Bot

Usage:
  tumblr.py archive [--verbose]
  tumblr.py export [--new]
  tumblr.py statistics

"""


__title__ = 'donereading.tumblr'
__version__ = '0.0.2'
__author__ = 'Mihir Singh (citruspi)'
__license__ = 'MIT'
__copyright__ = 'Copyright 2013 Mihir Singh <me@mihirsingh.com>'


import beanstalkc
import config
from docopt import docopt
from peewee import *
import re
import requests
from termcolor import cprint
import time


class Tumblr(Model):

    url = CharField()
    parsed = BooleanField()
    queued = BooleanField()
    exported = BooleanField()

    class Meta:

        database = MySQLDatabase(config.tumblr['database']['database'],
                                 host=config.tumblr['database']['host'],
                                 user=config.tumblr['database']['username'],
                                 passwd=config.tumblr['database']['password'])


beanstalk = beanstalkc.Connection(host=config.tumblr['beanstalkd']['host'], port=config.tumblr['beanstalkd']['port'])
beanstalk.use(config.tumblr['beanstalkd']['tube'])
beanstalk.watch(config.tumblr['beanstalkd']['tube'])
beanstalk.ignore('default')


class ArchiveTime(object):

    def __init__(self, verbose=False):

        self.verbose = verbose
            
        if self.verbose: cprint('\n------------- ARCHIVE TIME! -------------\n', 'magenta')
            
        Tumblr.create_table(True)


    def insert(self, url):

        if not self.exists(url):

            data = Tumblr.create(url=url, parsed=False, queued=True)
            data.save()
                
            if self.verbose: cprint('[ADDED] ' + url, 'green')


    def exists(self, url):

        if Tumblr.select().where(Tumblr.url == url).count() == 0:

            return False

        else:

            return True


    def archive(self):

        while True:
            
            try:
                
                job = beanstalk.reserve()    
        
                if self.verbose: cprint('[INDEXING] ' + job.body, 'yellow')
                
                blog = Tumblr.get(Tumblr.url == job.body)
                blog.parsed = self.index(job.body)
                blog.save()
                
                job.delete()
                
            except beanstalkc.CommandFailed:
                
                pass


    def index(self, url):

        try: 

            source = requests.get(url).content.decode('utf-8')
            links = re.findall(r"<a.*?\s*href=\"(https?://(?:[\w\-\d]+).tumblr\.com){1}(?:[\w\-\d/]*)\".*?>(?:.*?)</a>", source)

            for link in links:

                if not ('www' or 'static' or 'assets') in link and\
                   url != link:
                   
                    if not self.exists(link):
                        
                        if self.verbose: cprint('[DISCOVERED] ' + link, 'blue')

                        self.insert(link)
                        beanstalk.put(str(link))
                        

            return True

        except requests.exceptions.ConnectionError:

            if self.verbose: cprint('[ERROR] ' + url, 'red')
            return False
            
    
    def export(self, new=False):
                
        if new:
            
            count = Tumblr.select().where(Tumblr.exported == False).count()
            start = time.time()
            
            with open("%s" % (datetime.datetime.now().strftime('Tumblr %Y-%m-%d %H:%M:%S')), "a+") as f:
            
                for row in Tumblr.select().where(Tumblr.exported == False):
                    
                    f.write(row.url)
                    row.exported = True
                    row.save()
                    
            cprint('Exported %s records in %s seconds.\n' % (count, start-time.time()), 'green') 
            
        else:
            
            count = Tumblr.select().count()
            start = time.time()
                 
            with open("%s" % (datetime.datetime.now().strftime('Tumblr %Y-%m-%d %H:%M:%S')), "a+") as f:
                
                for row in Tumblr.select():

                    f.write(row.url)
                    row.exported = True
                    row.save()
                    
            cprint('Exported %s records in %s seconds.\n' % (count, start-time.time()), 'green')
                        
                
    def statistics(self):
        
        print '%s Queued Jobs' % (str(beanstalk.stats_tube(config.tumblr['beanstalkd']['tube'])['current-jobs-ready']))
        print '%s Recorded Blogs\n' % (str(Tumblr.select().count()))


if __name__ == '__main__':
    
    args = docopt(__doc__)
    
    if args['archive']:
        
        jake = ArchiveTime(verbose=args['--verbose'])
        jake.archive()
        
    elif args['statistics']:
        
        jake = ArchiveTime(verbose=True)
        jake.statistics()
        
    elif args['export']:
        
        jake = ArchiveTime(verbose=True)
        jake.export(new=args['--new'])
