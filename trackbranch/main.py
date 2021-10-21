import argparse
import json
import os
import shlex
import sys
from pathlib import Path
from subprocess import PIPE, Popen


def check_profile(args: argparse.ArgumentParser) -> bool:
    ok = args.profile is not None
    if not ok:
        args.parser.print_help()
        print("\nerror: --profile is required "
              f"with the '{args.command}' command")
    return ok


def find_file(basename: str):
    d = Path.cwd()
    root = Path(d.root)

    while d != root:
        filename = f"{d}/.trackbranch.json"
        if os.path.exists(filename):
            return filename
        d = d.parent


def find_json_file(basename: str):
    filename = find_file(basename)
    if filename:
        with open(filename) as f:
            return json.load(f)


def find_json_storage():
    json_file = find_json_file(".trackbranch.json")

    if not json_file:
        with open(".trackbranch.json", "w") as f:
            f.write("{}")
        return {}
    return json_file


def write_json_storage(data: dict):
    json_file = find_file(".trackbranch.json")
    with open(json_file, "w") as f:
        json.dump(data, f)


def run_add(args: argparse.ArgumentParser):
    if not check_profile(args):
        return 1

    data = find_json_storage()

    branches = data.get(args.profile, [])
    for branch in args.branches:
        if branch in branches:
            print(f"error: branch '{branch}' is already in this profile")
        else:
            print(f"added '{branch}' to '{args.profile}'")
            branches.append(branch)
    data[args.profile] = sorted(branches)

    write_json_storage(data)

    return 0


def run_ls(args: argparse.ArgumentParser):
    data = find_json_storage()

    if args.profile:
        branches = data.get(args.profile, [])
        if branches:
            print(" ".join(branches))
    else:
        output = list(sorted([(k, v) for k, v in data.items()]))
        for profile, branches in output:
            print(f"{profile}: {branches}")

    return 0


def run_exec(args: argparse.ArgumentParser):
    if not check_profile(args):
        return 1

    data = find_json_storage()
    branches = data.get(args.profile, [])
    for branch in branches:
        cmdline = shlex.split(args.cmd.format(br=branch))

        # Get absolute path to argv[0] with /usr/bin/which.
        executable = None
        proc = Popen(["/usr/bin/which", cmdline[0]], stdout=PIPE)
        proc.wait()
        if not proc.returncode:
            out, err = proc.communicate()
            executable = out.decode().rstrip()
        else:
            print(f"error: failed to find absolute path to '{cmdline[0]}'")
            return proc.returncode

        proc = Popen([executable, *cmdline[1:]])
        proc.wait()

        if proc.returncode:
            print("error: unsuccessful return code "
                  f"'{proc.returncode}' from --cmd")
            return proc.returncode

    return 0


def run_rm(args: argparse.ArgumentParser):
    if not check_profile(args):
        return 1

    data = find_json_storage()

    branches = data.get(args.profile, [])
    for branch in args.branches:
        if branch not in branches:
            print(f"error: branch '{branch}' is not in this profile")
        else:
            branches.remove(branch)
            print(f"removed '{branch}' from '{args.profile}'")

    data[args.profile] = sorted(branches)

    write_json_storage(data)

    return 0


def run_clear(args: argparse.ArgumentParser):
    if not check_profile(args):
        return 1

    data = find_json_storage()
    if args.profile in data:
        del data[args.profile]
        print(f"profile '{args.profile}' has been removed")
    else:
        print(f"error: profile '{args.profile}' could not be found")
        return 1

    write_json_storage(data)

    return 0


def parse_args():
    epilog = """
examples:
  # Add branch1 and branch2 to my-profile.
  $ trackbranch -p my-profile add branch1 branch2

  # List branches in the my-profile collection.
  $ trackbranch -p my-profile ls

  # Execute -c for each branch found in my-profile. The {br} specifier
  # will be substituted with the name of the branch.
  $ trackbranch -p my-profile exec -c 'git checkout {br}; git rebase -i base'

  # Remove branch1 from my-profile; branch2 remains.
  $ trackbranch -p my-profile rm branch1

  # Clear my-profile.
  $ trackbranch -p my-profile clear

persistence:
  trackbranch will use the first .trackbranch.json file it finds from
  the current directory or upwards. If none can be found, .trackbranch.json
  will be automatically created on first command usage in the working
  directory.
"""
    parser = argparse.ArgumentParser(
        formatter_class=lambda prog: argparse.RawDescriptionHelpFormatter(
            prog, max_help_position=80),
        epilog=epilog
    )
    parser.add_argument("-p", "--profile", metavar="profile",
                        type=str, help="profile name")

    choices = ["add", "rm", "exec", "ls", "clear"]
    parser.add_argument("command", choices=choices, help="primary command")
    parser.add_argument("-c", "--cmd", metavar="cmd", type=str,
                        help="shell command format string (required by exec)")

    parser.add_argument("branches", metavar="branch", type=str, nargs="*",
                        help="branches used with <command>")

    args = parser.parse_args()
    args.parser = parser
    return args


commands = {
    "add": run_add,
    "ls": run_ls,
    "exec": run_exec,
    "rm": run_rm,
    "clear": run_clear,
}


def main():
    args = parse_args()
    fn = commands.get(args.command)
    return fn(args)


if __name__ == "__main__":
    e = main()
    sys.exit(e)
