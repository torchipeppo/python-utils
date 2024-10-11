"""
After getting his revenge with his Abyss, the great wizard Zzzyxas
turned to more productive activities.
His arcane power now allows to not only execute tasks in a list in order
(as he does best), but even for YOU to update the queue while he's working!

Yes, while Zzzyxas is working on a thing, you can change the future of the queue
as much as you want! Add that thing you forgot! Redistribute tasks!
Finish implementing task B while Zzzyxas does task A and then add task B to the queue
to begin immediately after task A is completed! The possibilities are limitless. 

Each line in the queue file is interpreted as a shell command.
Tasks are DESTROYED (eliminated) from the list as soon as they are started,
but Zzzyxas will also keep a log of his activity so you don't forget what he's done.

Zzzyxas doesn't care about multiprocessing nonsense.
But you can summon multiple copies of him at the same time if you want.
In that case, just make sure that each gets its own queue.

Provide the name of an existing queue file for Zzzyxas to DESTROY (one task at a time)
and the name of a log file for Zzzyxas to write on.

He will still appear last in (most) alphabetical lists, but he's not the least by any means.
"""

# Translation of the easter-egg-y flavor text:

# This script executes the shell commands in the specified "queue file" (-q option).
# Each line represents a separate task.

# Contrary to just including the list directly in the source code,
# or reading from the queue file all at once,
# this script only consumes the first line of the given file, deleting it,
# and executes that command. Only after it's done, the next line is consumed.

# This means that it is possible to REVISE THE PLAN FOR FUTURE TASKS
# WHILE THE CURRENT ONE IS EXECUTING.
# This is the main feature.
# (The queue file includes only the future commands, not the currently ongoing one,
#  so don't worry about messing up the current task.)

# Because executed commands are removed from the queue file,
# they are logged in a separate file for preservation (-l option).
# This is NOT optional.

# The name of this script is an obscure reference,
# and it has been chosen specifically to appear last alphabetically.

import argparse
import logging
import subprocess
import time

parser = argparse.ArgumentParser(
    description='Execute a list of commands, but you can also update it as you go.'
)
parser.add_argument('-q', '-i', '--queue', required=True, dest='queue_fname')
parser.add_argument('-l', '-o', '--log', required=True, dest='log_fname')

def get_task(queue):
    task = ""
    while task == "":
        try:
            task = queue.pop(0).strip()
        except IndexError:  # pop from empty list
            return None
    return task

args = parser.parse_args()
logging.basicConfig(filename=args.log_fname,
                    filemode='a',
                    format='[%(asctime)s][%(levelname)s] - %(message)s',
                    level=logging.DEBUG)
while True:
    with open(args.queue_fname, "r") as f:
        queue = f.readlines()
    task = get_task(queue) # queue has been side-affected, as its top element(s) have been popped out
    with open(args.queue_fname, "w") as f:
        f.writelines(queue)
    if task is None:
        break
    
    logging.info(f"Starting: {task}")
    completion_info = subprocess.run(task.split(), text=True)
    
    if completion_info.returncode == 0:
        logging.info(f"Completed.")
    else:
        unique_hex = hex(time.time_ns())
        logging.error(f"Exited w/ code {completion_info.returncode}, check files w/ hex {unique_hex}")
        if completion_info.stdout is not None:
            with open(f"stdout_{unique_hex}.txt", "w") as f:
                f.write(completion_info.stdout)
        if completion_info.stderr is not None:
            with open(f"stderr_{unique_hex}.txt", "w") as f:
                f.write(completion_info.stderr)
