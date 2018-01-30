#!/bin/bash

BASE_DIR="$HOME/.tctools"
REPO_DIR="$BASE_DIR/repo"
VENV_DIR="$BASE_DIR/env"

unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)
        MACHINE="Linux"
        INSTALL_PIP="sudo apt-get install python-pip"
        ;;
    Darwin*)
        MACHINE="Mac"
        INSTALL_PIP="sudo easy_install pip"
        ;;
    *)
        echo "UNKNOWN MACHINE: ${unameOut}" && exit 1
esac

echo $MACHINE

mkdir -p "$BASE_DIR"
rm -rf "$REPO_DIR"
git clone --depth 1 "git@github.com:ToucanToco/tctools.git" "$REPO_DIR"
# sudo cp "$REPO_DIR/install.sh" "/usr/local/bin/tctools-update"
# sudo chmod +x "/usr/local/bin/tctools-update"


# ~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~ frontserver ~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~

_=$(which pip)
[[ $? -ne 0 ]] && $INSTALL_PIP

_=$(which virtualenv)
[[ $? -ne 0 ]] && sudo pip install virtualenv

rm -rf "$VENV_DIR"
virtualenv "$VENV_DIR"
"$VENV_DIR/bin/pip" install -r "$REPO_DIR/frontserver/requirements.txt"

echo -e "#!/usr/bin/env bash\n$VENV_DIR/bin/python $REPO_DIR/frontserver/frontserver.py \$@" | sudo tee /usr/local/bin/frontserver
sudo chmod +x /usr/local/bin/frontserver
