#!/usr/bin/env python3
import os
import pathlib
import shlex
import subprocess
import sys


def _helper(completion_function):
    # TODO: Support other shells?
    shell = os.environ.get("SHELL")
    if "bash" not in shell:
        quit("Sorry, only bash supported at the moment!")

    comp_exe = str(pathlib.Path(sys.argv[0]).absolute())
    # Get arguments and environment variables
    comp_vars_set = "COMP_LINE" in os.environ and "COMP_POINT" in os.environ

    # if the "COMP" variables aren't set, the script is being executed by
    # a non-completion utility.
    if not comp_vars_set:
        args = ["complete", "-C", comp_exe]
        args.extend(sys.argv[1:])
        # Assuming it's the user, we print up
        # some installation instructions that they can evaluate.
        if sys.stdout.isatty():
            usr_msg = "Redirect this into your .profile to install:"
            print(usr_msg, file=sys.stderr)
        print(" ".join(args).strip())
        return

    cmd, curr_word, prev_word = sys.argv[1:]

    # Build up a dict of parameters for the completion function.
    if completion_function:
        results = completion_function(*sys.argv[1:])

    # bash reads stdout for completion. Each entry is on a new line.
    if len(results):
        print("\n".join(results))


def bash_completion_decorator(func):
    """
    This decorator will call ``func`` with three positional arguments:
    command - The command the completion should be run for.
    current_word - The current word being typed at the terminal.
    previous_word - The previous word in the line.

    ``func`` should return an array of strings. Abnormal
    behavior may result if those strings contain newline characters.
    """
    def wrapper():
        _helper(func)

    return wrapper


class CompletionError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def bash_complete(comp_line, comp_exe):
    """
    This is an approximation of how bash's complete function generates matches.
    ``comp_line`` Is the line assumed to be at the terminal.
    ``comp_exe`` is the path to an executable file that will generate matches.
    Returns the stdout of comp_exe after running with parameters normally
    supplied by complete.
    """
    cmd_line_args = shlex.split(comp_line)
    cmd = cmd_line_args[0]
    comp_point = str(len(comp_line))
    curr_word = ""
    prev_word = cmd
    if comp_line.endswith(" "):
        curr_word = ""
        prev_word = cmd_line_args[-1]
    else:
        curr_word = cmd_line_args[-1]
        prev_word = cmd_line_args[-2] if len(cmd_line_args) >= 2 else ""

    os.environ.update({"COMP_LINE": comp_line, "COMP_POINT": comp_point})
    finished_process = subprocess.run(
        [comp_exe, cmd, curr_word, prev_word],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    if finished_process.stderr:
        raise CompletionError(finished_process.stderr)
    return finished_process.stdout.strip()


if __name__ == "__main__":
    if len(sys.argv) > 1 and pathlib.Path(sys.argv[1]).exists():
        print(bash_complete(" ".join(sys.argv[2:]), sys.argv[1]))
    else:
        stem = str(pathlib.Path(__file__).stem)
        usage_fmt = (
            "usage: {} executable line_to_complete\n"
            "See README.md for a thorough tutorial on using this file to "
            "write completions!"
        )
        print(
            usage_fmt.format(stem),
            file=sys.stderr
        )
