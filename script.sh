#!/bin/sh
# Purpose: Clone and parse as XML a list of Github repositories
# Author: Elder Cirilo
# ------------------------------------------
# ./script.sh [Path to Github repos CSV file] [Path to save projects]
# ------------------------------------------

INPUT=$1
WORKING_DIR=$2
OLDIFS=$IFS
IFS=','

[ ! -f $INPUT ] && { echo "$INPUT file not found"; exit 99; }

source .venv/bin/activate

while read project url
do
    PROJECT_DIRECTORY="$WORKING_DIR/$project"
    #[ -d $PROJECT_DIRECTORY ] && { 
    #    echo "Skipping '$project'";         
    #    echo "";
    #    continue; 
    #}

    echo "Creating directory ['$PROJECT_DIRECTORY']" 
    #mkdir $PROJECT_DIRECTORY
    cd $PROJECT_DIRECTORY
    mkdir repo 
    #mkdir srcml    

    cd "$PROJECT_DIRECTORY/repo"
    git clone $url
    
    echo "Getting project stats ['$PROJECT_DIRECTORY']" 
    cd $PROJECT_DIRECTORY
    cloc "$PROJECT_DIRECTORY/repo/$project" --csv --csv-delimiter=, --quiet > stats.csv
    
    #echo "Parsing '$project' ... "
    #cd "$PROJECT_DIRECTORY/srcml"
    #srcml "$PROJECT_DIRECTORY/repo/$project" -o "$project.xml"
        
    echo "Cleaning up '$project' ..."
    cd $PROJECT_DIRECTORY
    rm -rf repo

    #echo "Extracting names from '$PROJECT_DIRECTORY/srcml/$project.xml'..."
    #cd "$PROJECT_DIRECTORY/srcml"
    #python3 "../../../../cpp-names-extractor.py"
        
    echo "Done!"
    echo "----------------------------------"
    echo ""
done < $INPUT
IFS=$OLDIFS
