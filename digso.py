# -*- coding=UTF-8 -*-
# python3 ./digso.py -p /lib64/libc.so.6 -d 10
import os
import re
import sys
import shutil
import logging
# import xmltodict
from optparse import OptionParser
from SWUtils import channel_cmd

def parseOpt():
    parser = OptionParser()
    parser.add_option("--folder", "-f", dest="folder", default="",
        help="The folder of shared libs. e.g. /usr/lib64/")
    parser.add_option("--path", "-p", dest="path", default="",
        help="The path of a shared lib. e.g. /usr/lib64/libpopt.so.0")
    parser.add_option("--output", "-o", dest="output", default="",
        help="The output of the results. e.g. /tmp/digso.out")
    parser.add_option("--debug", "-d", dest="debug", default=20,
        help="e.g. 50 (FATAL), 40 (ERROR), 30 (WARN), 20 (INFO), 10 (DEBUG), 0 (NOTSET)")    
    (options, args) = parser.parse_args()
    if not os.path.exists(options.folder) and not os.path.exists(options.path):
        logging.error("Must provide libs path or folder!")
        sys.exit(1)
    return options

def parse(stdout):
    libs = set()
    not_found = set()
    others = set()
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        # e.g. libm.so.6 => /lib64/libm.so.6 (0x00007f8519400000)
        m = re.match(r'\s*\S+\s+=>\s+(\S+)\s+\(.+\)\s*', line)
        if m is not None:
            libs.add(m.group(1))
            sub_libs, sub_not_found, sub_others = ldd(m.group(1))
            libs = libs.union(sub_libs)
            not_found = not_found.union(sub_not_found)
            others = others.union(sub_others)
        else:
            # e.g. libjvm.so => not found
            m = re.match(r'\s*\S+\s+=>\s+not found\s*', line)
            if m is not None:
                not_found.add(line)
            else:
                others.add(line)
    return libs, not_found, others
    
def ldd(lib):
    libs = set()
    not_found = set()
    others = set()
    cmd = "ldd {}".format(lib)
    returncode, stdout, stderr = channel_cmd(cmd)
    if returncode == 0:
        libs, not_found, others = parse(stdout)
    else:
        logging.warning("{0} failed: {1}".format(cmd, stderr))
    return libs, not_found, others

if __name__ == '__main__':
    options = parseOpt()
    logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s', level=int(options.debug))
    logging.debug(options)

    libs = set()
    not_found = set()
    others = set()

    if options.folder:
        cmd = "find {} -name \"*.so\"".format(options.folder)
        returncode, stdout, stderr = channel_cmd(cmd)
        if returncode == 0:
            for lib in stdout.splitlines():
                logging.debug("ldd " + lib)
                sub_libs, sub_not_found, sub_others = ldd(lib)
                libs = libs.union(sub_libs)
                not_found = not_found.union(sub_not_found)
                others = others.union(sub_others)
        else:
            logging.warning("{0} failed: {1}".format(cmd, stderr))
    
    if options.path:
        sub_libs, sub_not_found, sub_others = ldd(options.path)
        libs = libs.union(sub_libs)
        not_found = not_found.union(sub_not_found)
        others = others.union(sub_others)

    if options.output:
        with open(options.output, 'w') as f:
            for lib in libs:
                f.write(lib + "\n")

    logging.debug("libs = {}".format(libs))
    logging.debug("not_found = {}".format(not_found))
    logging.debug("libs = {}".format(others))
    logging.info("All Done. Good job!")
