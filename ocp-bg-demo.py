#!/usr/bin/env python
from __future__ import division

import re
import sys
import time
import Queue
import socket
import urllib2
import threading


# TODO - store in yaml file
TARGET_URL="http://web-simple-php.ocp.vultr.lab.422long.com/bgtest.php"
STATS_FREQ_SECS=5
THREAD_COUNT=1
PROGRESS_BAR_CHARS_WIDTH=100



class Worker(threading.Thread):
    def __init__(self, results_queue):
        threading.Thread.__init__(self)
        self.results_queue = results_queue
        self.daemon = True
        self.start()

    def run(self):
        while True:
            start = time.time()
            #print threading.current_thread() 
            try:
                response = urllib2.urlopen(TARGET_URL, timeout=3)
                html = response.read()
                response_duration = time.time()-start
                response_size = len(html)
                
                m = re.search("([a-z]+)\.(jpg|png)",html)
                response_key = m.group(1)

            except (urllib2.HTTPError, urllib2.URLError, socket.timeout, socket.error) as e:
                continue
                print e
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
                # every 1 second output progress bar
                data_keys = {}
                for item in data[last_sec_report]:
                    if item['key'] not in data_keys:  data_keys[item['key']] = 1
                    else:  data_keys[item['key']] += 1
                i = 40
                for k in sorted(data_keys):
                    #if k == '-':  continue
                    i += 1
                    sys.stdout.write("\x1b[0;37;%sm%s\x1b[0m" % (i,' ' * int(round( (data_keys[k]/sum(data_keys.values()))*(PROGRESS_BAR_CHARS_WIDTH )))) )
                sys.stdout.write("\r")
                sys.stdout.flush()
                last_sec_report = now
            elif now>last_five_sec_report+5 and last_five_sec_report in data:
                # every 5 seconds output a summary
                data_keys = {}
                sys.stdout.write(' '*(PROGRESS_BAR_CHARS_WIDTH+1)+"\r")
                sys.stdout.flush()
                for sec in range(last_five_sec_report,now-1):
                    if sec not in data: continue
                    for item in data[sec]:
                        if item['key'] not in data_keys:  data_keys[item['key']] = 1
                        else:  data_keys[item['key']] += 1
                i = 40
                for k in sorted(data_keys):
                    #if k == '-':  continue
                    i += 1
                    sys.stdout.write("\x1b[0;37;%sm%s: %s%% (%s reqs)\x1b[0m\t" % (i,k,int(round((data_keys[k]/sum(data_keys.values()))*100 )),data_keys[k]))
                sys.stdout.write("\n")
                sys.stdout.flush()
                last_five_sec_report = now

    except (KeyboardInterrupt, SystemExit):
        """
        data_keys = {}
        for sec,item in data.iteritems():
            if item[0]['key'] not in data_keys:  data_keys[item[0]['key']] = 1
            else:  data_keys[item[0]['key']] += 1

        print "%s total requests in %s seconds" % (sum(data_keys.values()),max(data.keys())-min(data.keys()))
        """

        print "\n------------\n"
        sys.exit()


    except:
        raise




