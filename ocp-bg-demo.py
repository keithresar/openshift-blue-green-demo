#!/usr/bin/env python
from __future__ import division

import re
import sys
import time
import Queue
import urllib2
from threading import Thread


# TODO - store in yaml file
TARGET_URL="http://104.238.162.143/images/bgtest.php"
STATS_FREQ_SECS=5
THREAD_COUNT=10
PROGRESS_BAR_CHARS_WIDTH=100



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
                
                m = re.search("([^\s\.]+)\.(jpg|png)",html)
                response_key = m.group(1)

            except urllib2.HTTPError as e:
                response_duration = time.time()-start
                response_size = 0
                response_key = "-"

            finally:
                self.results_queue.put({'key': response_key, 
                                        'size': response_size, 
                                        'duration_ms': int(response_duration*1000),
                                        'time': int(time.time())})



if __name__ == "__main__":

    # TODO - load yaml config
    # TODO - output configuration

    try:
        data = {}
        results_queue = Queue.Queue()

        # start threads
        for _ in range(THREAD_COUNT):  Worker(results_queue)

        last_sec_report = int(time.time())
        last_five_sec_report = int(time.time())
        while True:
            try:
                o = results_queue.get(True,1)
                if o['time'] not in data:  data[o['time']] = [o,]
                else:  data[o['time']].append(o)
            except Queue.Empty:
                pass

            now = int(time.time())
            if now>last_sec_report and last_sec_report in data:
                # TODO - every 1 second output progress bar
                #print data
                data_keys = {}
                for item in data[last_sec_report]:
                    if item['key'] not in data_keys:  data_keys[item['key']] = 1
                    else:  data_keys[item['key']] += 1
                i = 40
                for k in sorted(data_keys):
                    if k == '-':  continue
                    i += 1
                    sys.stdout.write("\x1b[0;37;%sm%s\x1b[0m" % (i,' ' * int(round( (data_keys[k]/sum(data_keys.values()))*(PROGRESS_BAR_CHARS_WIDTH )))) )
                sys.stdout.write("\r")
                sys.stdout.flush()
                last_sec_report = now
            elif now>last_five_sec_report+5:
                sys.stdout.write("xx%s\r" % ' '*(PROGRESS_BAR_CHARS_WIDTH+1))
                sys.stdout.flush()

                last_five_sec_report = now
                # TODO - every 5 seconds output a summary onto a new line

    except (KeyboardInterrupt, SystemExit):
        print("\n")
        # TODO - summarize results
        #   TODO - output total request count
        #   TODO - output total request bytes xfered
        #   TODO - output # of requests by response type
        #   TODO - output # of requests by key
        sys.exit()


    except:
        raise




