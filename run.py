#!/usr/bin/env python

import os
import subprocess

if __name__ == '__main__':
    servers = [
        ["python", "manage.py", "runserver", "0.0.0.0:8000"],
    ]
    procs = []
    for server in servers:
        proc = subprocess.Popen(server)
        procs.append(proc)
    for proc in procs:
        proc.wait()
        if proc.poll():
            exit(0)
