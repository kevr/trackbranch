# trackbranch

`trackbranch` is a tool for developers that can be used to store
collections of branches in the form of profiles. This can be useful
for situations where you have multiple branches to group into the
same action.

### Installation

Users can install the `trackbranch` package via PyPi:

    $ pip install trackbranch

Or, clone the repository, build it and install it with pip:

    $ poetry lock
    $ poetry update
    $ poetry build
    $ pip install dist/*.whl

### Getting Started

Create a branch profile `my-profile` consisting of `branch1` and `branch2`:

    # Add branch1 and branch2 to my-profile.
    $ trackbranch -p my-profile add branch1 branch2

This will automatically create a `.trackbranch.json` file if one
cannot be found in the current directory or upwards.

List all profiles:

    $ trackbranch ls

List specific branches by providing `-p|--profile`:

    # List branches in the my-profile collection.
    $ trackbranch -p my-profile ls

For each branch in `my-profile`, execute the command `-c`. Each `{br}` string
format piece is replaced by the branch name.

    # Execute -c for each branch found in my-profile.
    $ trackbranch -p my-profile exec -c 'bash -c "git checkout {br}; git rebase -i base"'

Remove `branch1` from `my-profile`.

    # Remove branch1 from my-profile; branch2 remains.
    $ trackbranch -p my-profile rm branch1

Completely clear out `my-profile`.

    # Clear my-profile.
    $ trackbranch -p my-profile clear

### License

This project operates under The MIT [License](./LICENSE).

### Authors

| Name         | Email          |
|--------------|----------------|
| Kevin Morris | kevr@0cost.org |
