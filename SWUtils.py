import re
import time
import subprocess

def gen_timestamp(humanize=False):
    now = int(time.time())
    timeArray = time.localtime(now)
    return time.strftime("%Y-%m-%d %H:%M:%S", timeArray) if humanize else time.strftime("%Y%m%d_%H%M%S", timeArray)

def channel_cmd(cmd, retry=0):
    '''
    Send command to channel, wait for an answer and raise exception if failed.
    '''
    while retry >= 0:
        retry -= 1
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        if p.returncode == 0:
            break
    return p.returncode, p.stdout.read().decode('utf-8'), p.stderr.read().decode('utf-8')

if __name__ == "__main__":
    print("gen_timestamp() = {}".format(gen_timestamp()))
    print("gen_timestamp(True) = {}".format(gen_timestamp(True)))

    print("channel_cmd('uname -a && whoami') = {}".format(channel_cmd('uname -a && whoami')))
    print("channel_cmd('whoami?', 1) = {}".format(channel_cmd('whoami?', 1)))
