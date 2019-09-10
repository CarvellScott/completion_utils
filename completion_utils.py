#!/usr/bin/env python3
import abc
import argparse
import json
import os
import pathlib
import shlex
import subprocess
import sys
import unittest


def _helper(completion_function):
    # TODO: Support other shells?
    shell = os.environ.get("SHELL")
    if "bash" not in shell:
        quit("Sorry, only bash supported at the moment!")

    # Get arguments and environment variables
    comp_vars_set = "COMP_LINE" in os.environ and "COMP_POINT" in os.environ

    # if the "COMP" variables aren't set, the script is being executed by
    # something other than complete.
    if not comp_vars_set:
        home = str(pathlib.Path.home())
        comp_exe = str(pathlib.Path(sys.argv[0]).absolute())
        comp_exe = comp_exe.replace(home, "$HOME")
        install_args = ["complete", "-C", comp_exe]
        install_args.extend(sys.argv[1:])
        # Assuming it's the user, we print up
        # some installation instructions that they can evaluate.
        # TODO: Offer to install or run a unit test.

        if sys.stdout.isatty():
            usr_msg = "Redirect this into your .profile to install:"
            print(usr_msg, file=sys.stderr)
        print(" ".join(install_args).strip())
        return

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


class BashCompletion(abc.ABC):
    completion_test_case = None

    @property
    def comp_line(self):
        """
        Convenience method for accessing the "COMP_LINE" env variable.
        """
        return os.environ["COMP_LINE"]

    @property
    def comp_point(self):
        """
        Convenience method for accessing the "COMP_POINT" env variable.
        """
        return os.environ["COMP_POINT"]

    def main(self):
        """
        This function is the entry point of your completion program.
        If the COMP_LINE and COMP_POINT environment variables are set, it will
        call completion hook, passing in the command, current word being
        completed, and the previous word, and expect a set of strings to be
        returned.
        That set of strings will be printed out to be used for completion.
        """
        comp_vars_set = "COMP_LINE" in os.environ and "COMP_POINT" in os.environ
        if not comp_vars_set:
            parser = argparse.ArgumentParser()
            subparsers = parser.add_subparsers()
            parser.set_defaults(func=self._print_install_msg)

            parser_test = subparsers.add_parser("test")
            parser_test.set_defaults(func=self._run_test)

            parser_install = subparsers.add_parser("install")
            parser_install.add_argument(
                "command",
                type=str,
                help="The command that this completion should be applied to"
            )
            parser_install.set_defaults(func=self._print_install_msg)

            args = parser.parse_args()
            args.func(args)
        else:
            results = self.completion_hook(*sys.argv[1:])

            # bash reads stdout for completion. Each entry is on a new line.
            if len(results):
                print("\n".join(results))

    def _run_test(self, args):
        if not self.completion_test_case:
            err = "No unit tests have been assigned to this completion."
            raise NotImplementedError(err)
        if not issubclass(self.completion_test_case, CompletionTestCase):
            err = "completion_test_case must subclass CompletionTestCase"
            raise Exception(err)
        loader = unittest.defaultTestLoader
        suite = loader.loadTestsFromTestCase(self.completion_test_case)
        runner = unittest.TextTestRunner()
        runner.run(suite)

    def _print_install_msg(self, args):
        home = str(pathlib.Path.home())
        comp_exe = str(pathlib.Path(sys.argv[0]).absolute())
        comp_exe = comp_exe.replace(home, "$HOME")
        install_args = ["complete", "-C", comp_exe]
        usr_msg = (
            "Redirect this into your .profile to install"
        )
        if hasattr(args, "command"):
            install_args.append(args.command)
            usr_msg += "completion for {}".format(args.command)
        usr_msg += ":"

        install_cmd = " ".join(install_args).strip()
        if sys.stdout.isatty():
            print(usr_msg, file=sys.stderr)
        print(install_cmd)

    @abc.abstractmethod
    def completion_hook(command: str, curr_word: str, prev_word: str) -> set:
        """
        Overriding this method is required.
        """
        ...


class CompletionTestCase(unittest.TestCase):
    exe = None

    def get_completions(self, comp_line):
        raw_str = bash_complete(comp_line, self.exe)
        return set(raw_str.splitlines())

    def setUp(self):
        if not self.exe:
            err = "Executable to be used for completion has not been assigned"
            raise Exception(err)


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
