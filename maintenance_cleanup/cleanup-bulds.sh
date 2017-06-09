#!/bin/bash

if [ "$#" -gt 1 ]; then
    echo "

      Usage: cleanup-builds.sh  [Dry Run]

      Example: cleanup-builds.sh false

      NOTE: If not specified, Dry Run is assumed true.
    "

    exit 1
fi

#Globals
LEAVE_BUILDS=30

dryrun=true
if [ "$#" -gt 0 ]; then
    dryrun=$1
fi

#Check for the project
project_list=`oc projects -q`
#Check to see that we got a response, if not just die.
if [ -z "$project_list" ]; then

  echo "=====================================================================
No projects found!  This should not happen, so something bad occured.
====================================================================="
  exit 1

fi

#Process the list of projects and export them if they are valid
readarray -t projects <<<"$project_list"
for project in "${projects[@]}"
do

  #check to see if the project is actually validation
  project_exists=`oc projects -q | grep ${project}`
  if [ -n "$project_exists" ]; then

    echo "Found Project: ${project}"

    build_config_list=`oc get bc -n ${project} --no-headers | awk '{print $1}' `
    if [ -n "$build_config_list" ]; then

      readarray -t build_configs <<<"$build_config_list"
      for build_config in "${build_configs[@]}"
      do

        echo "Project: ${project}, build config: ${build_config}"

        #Count the number of dashes in the application name, as we'll need to
        #adjust the position of the array location after the split
        dashCount=`echo $build_config |  awk 'BEGIN{FS="-"} {print NF}'`
        #echo "$dashCount"

        #Set the array position, but adding a default value of 1
        buildNumPos=$(($dashCount + 1))
        #echo "Build number position: $buildNumPos"

        #Get the list of builds
        var=`oc get builds -n ${project} --no-headers -l buildconfig=${build_config} | \
          awk -v buildNumPos="$buildNumPos" '{split($1,a,"-"); print a[buildNumPos]}'`
        #echo $var

        #Set the max build number
        max=0

        #Split the build numbers, to get them as an array
        builds=$(echo $var | tr "\r\n" "\n")

        if [ -n "$builds" ]; then

          #Loop the build numbers and find the most recent (max) build
          for build in $builds
          do
            #Perform the check and set the max number
            if [ $build -gt $max ]; then
              #echo "number: $build"
              max=$build
            fi
          done

          #Echo the max
          echo "Most recent build for $build_config is: $max"

          #Now, reloop the numbers and delete all but the max
          for build in $builds
          do
            #echo "build: $build"
            if [ $build -lt $(($max - $LEAVE_BUILDS)) ]; then

              if [ "$dryrun" = "true" ]; then
                echo "oc delete bulld -n ${project} $build_config-$build"
              fi

              if [ "$dryrun" = "false" ]; then
                oc delete build -n ${project} $build_config-$build
              fi
            fi
          done
        fi
      done
    fi
  fi
done
