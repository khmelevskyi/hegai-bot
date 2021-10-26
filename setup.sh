# use dev arg to use pre-commit

RED="\033[0;31m"
GREEN="\033[0;32m"
ENDCOLOR="\033[0m"


echo -e "\n${RED}Deleting old environment${ENDCOLOR}\n"
deactivate
rm -rf venv

echo -e "\n${RED}Creating new environment${ENDCOLOR}\n"
python3 -m venv venv
. venv/bin/activate

echo -e "\n${RED}Updating packages${ENDCOLOR}\n"
pip3 install --upgrade pip
pip3 install wheel
pip3 install poetry

# check if command line argument is dev or empty
if [[ "$1" = "--dev" || "$1" = "-d" ]]
	then
	echo -e "\n${GREEN}Installing dependencies for development${ENDCOLOR}\n"
	poetry install
	pre-commit install --install-hooks
else
	echo -e "\n${GREEN}Installing dependencies${ENDCOLOR}\n"
	pip3 install --no-dev
	pre-commit uninstall
fi

echo -e "\n${RED}Installed${ENDCOLOR}\n"
poetry show --tree
