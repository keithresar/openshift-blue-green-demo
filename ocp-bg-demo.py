#!/usr/bin/env python

import re
import sys
import time
import Queue
import urllib2
from threading import Thread


# TODO - store in yaml file
TARGET_URL="http://104.238.162.143/images/bgtest.php"
STATS_FREQ_SECS=5
THREAD_COUNT=1



class Worker(Thread):
    def __init__(self, results_queue):
        Thread.__init__(self)
        self.results_queue = results_queue
        self.daemon = True
        self.start()

    def run(self):
        while True:
            start = time.time()
            try:
                response = urllib2.urlopen(TARGET_URL)
                html = response.read()
                response_duration = time.time()-start
                response_size = len(html)
                
                m = re.search("([^\s\.]+\.(jpg|png))",html)
                response_key = m.group(0)

            except urllib2.HTTPError as e:
                response_duration = time.time()-start
                response_size = 0
                response_key = "-"

            finally:
                self.results_queue.put({'key': response_key, 'size': response_size, 'duration_ms': int(response_duration*1000)})



if __name__ == "__main__":

    # TODO - load yaml config
    # TODO - output configuration

    try:
        results_queue = Queue.Queue()

        # start threads
        for _ in range(THREAD_COUNT):  Worker(results_queue)

        while True:
            try:
                o = results_queue.get(True,1)
                print o
            except Queue.Empty:
                pass

            # TODO - process results
            # TODO - every 5 seconds output a summary onto a new line

    except (KeyboardInterrupt, SystemExit):
        print "\n"
        # TODO - summarize results
        sys.exit()


    except:
        raise




