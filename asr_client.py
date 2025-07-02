__author__ = 'tanel'

import argparse
from ws4py.client.threadedclient import WebSocketClient
import threading
import sys
import queue
import json
import json
import time
import os
import codecs

nst = 1

def rate_limited(maxPerSecond):
    minInterval = 1.0 / float(maxPerSecond)

    def decorate(func):
        lastTimeCalled = [0.0]

        def rate_limited_function(*args, **kargs):
            elapsed = time.perf_counter() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait > 0:
                time.sleep(leftToWait)
            ret = func(*args, **kargs)
            lastTimeCalled[0] = time.perf_counter()
            return ret

        return rate_limited_function

    return decorate


class MyClient(WebSocketClient):
    global nsts
    nsts = 1
    def __init__(self, audiofile, out_text,seg_n, url, protocols=None, extensions=None, heartbeat_freq=None, byterate=32000,
                 save_adaptation_state_filename=None, send_adaptation_state_filename=None):
        super().__init__(url, protocols, extensions, heartbeat_freq)
        self.final_hyps = []
        self.audiofile = audiofile
        self.out_text = out_text
        self.seg_n = seg_n
        self.byterate = byterate
        self.final_hyp_queue = queue.Queue()
        self.save_adaptation_state_filename = save_adaptation_state_filename
        #        print(save_adaptation_state_filename)
        self.send_adaptation_state_filename = send_adaptation_state_filename
        self.status = 1
        self.trans_response={}
        self.utt_count=1


    @rate_limited(4)
    def send_data(self, data):
        self.send(data, binary=True)

    def opened(self):
        # print "Socket opened!"
        def send_data_to_ws():
            if self.send_adaptation_state_filename is not None:
                print("Sending adaptation state from %s" % self.send_adaptation_state_filename, file=sys.stderr)
                try:
                    adaptation_state_props = json.load(open(self.send_adaptation_state_filename, "r"))
                    #                    print(json.dumps(dict(adaptation_state=adaptation_state_props)))
                    self.send(json.dumps(dict(adaptation_state=adaptation_state_props)))
                except Exception as e:
                    print("Failed to send adaptation state: ", e, file=sys.stderr)
            with self.audiofile as audiostream:
                for block in iter(lambda: audiostream.read(self.byterate // 4), b""):
                    print(len(block), type(block))
                    self.send_data(block)
            print("Audio sent, now sending EOS", file=sys.stderr)
            self.send(b"EOS")

        t = threading.Thread(target=send_data_to_ws)
        t.start()

    def convertTime(self, inSecs):
        inSecs = round(inSecs, 3)
        m, s = divmod(int(inSecs), 60)
        h, m = divmod(m, 60)
        if '.' in str(inSecs):
            ms = int(str(inSecs).split('.')[1])
        else:
            ms = 0
        return '{:02d}:{:02d}:{:02d},{:03d}'.format(h, m, s, ms)

    def received_message(self, m):
        # fil=open('srts.srt','a')
        out_fil_name = self.out_text
        fil = codecs.open(out_fil_name, "a", "utf-8")
        # dump = codecs.open("response.txt", "a", "utf-8")
        #print(m)
        try:
            json_string = m.data.decode('utf-8')
            response = json.loads(json_string)
            # dump.write(response)
            #print(response)

            if response['status'] == 0:
                if 'result' in response:
                    trans = response['result']['hypotheses'][0]['transcript']
                    if response['result']['final']:
                        # print >> sys.stderr, trans,
                        self.final_hyps.append(trans)
                        startTime = response['segment-start'];
                        startTime = round(startTime, 2)
                        endTime = response['segment-start'] + response['segment-length'];
                        endTime = round(endTime ,2 )
                        utt_no = self.seg_n+"_S" + str(self.utt_count)
                        fil.write(utt_no+'\t'+'spk'+'\t'+str(startTime) + "\t" + str(endTime) +'\t');
                        fil.write(trans.upper()+"۔" + "\n")
                        self.trans_response[utt_no] = {}
                        self.trans_response[utt_no]['startTime'] = str(startTime)
                        self.trans_response[utt_no]['endTime'] = str(endTime)
                        self.trans_response[utt_no]['text'] = trans.upper()
                        self.utt_count +=1

                        #print('trannnnnnnnnnns:1 ' + trans)
                        print(trans.upper())
                        #fil.truncate(0)
                        #fil.write(str(self.trans_response));
                        #json.dump(self.trans_response, fil)
                    else:
                        print_trans = trans.replace("\n", "\\n")
                        if len(print_trans) > 80:
                            print_trans = "... %s" % print_trans[-76:]
                        print_trans = print_trans.upper()
                        # print >> sys.stderr, print_trans,
                elif 'adaptation_state' in response:
                    self.status =0
                    print("adptaion ")


            elif response['status'] == 2:
                if 'result' in response:
                    trans = response['result']['hypotheses'][0]['transcript']
                    if response['result']['final']:
                        self.final_hyps.append(trans)
                        fil.write(trans.upper() + "\n")
                        print('trannnnnnnnnnns:2 ' + trans)
                    else:
                        print_trans = trans.replace("\n", "\\n")
                        if len(print_trans) > 80:
                            print_trans = "... %s" % print_trans[-76:]
                        print_trans = print_trans.upper()
                        # print >> sys.stderr, print_trans,

                elif 'adaptation_state' in response:
                    self.status =0
            else:
                self.status = 0
                print("***************************************************************")
                #print(response)
                print >> sys.stderr, "Received error from server (status %d)" % response['status']
                if 'message' in response:
                    print >> sys.stderr, "Error message:", response['message']
                self.final_hyp_queue.put(" ".join(self.final_hyps))
                self.final_hyp_queue.put(None)
                fil.close()
                self.close()
        except:
            print('****',m)

    def get_status(self):
        return self.status

    def get_full_hyp(self, timeout):
        return self.final_hyp_queue.get(timeout=timeout)


#def main():
    #parser = argparse.ArgumentParser(description='Command line client for kaldigstserver')
    #parser.add_argument('-u', '--uri', default="ws://localhost:8888/client/ws/speech", dest="uri",
                        #help="Server websocket URI")
    #parser.add_argument('-r', '--rate', default=32000, dest="rate", type=int,
                       # help="Rate in bytes/sec at which audio should be sent to the server. NB! For raw 16-bit audio it must be 2*samplerate!")
    #parser.add_argument('--save-adaptation-state', help="Save adaptation state to file")
    #parser.add_argument('--send-adaptation-state', help="Send adaptation state from file")
    #parser.add_argument('-a', '--account', default="", help="Account Key")
    #parser.add_argument('file', help="Audio file to be sent to the server")
    #args = parser.parse_args()

    #audiofile = open('cyberbullyingmeetin1_p2.wav', "rb")
    #ws = MyClient(audiofile, 'ws://localhost:8888/client/ws/speech', byterate=16777216)
    #ws.connect()
   # try:
      #  result = ws.get_full_hyp()
     #   print(result)
   # except:
    #    pass
   # ws.close()


#if __name__ == "__main__":
  #  main()


