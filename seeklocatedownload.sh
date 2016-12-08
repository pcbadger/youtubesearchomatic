#!/bin/bash
set -x

function getYoutubeUrlList () {
    TRACKLIST=$1
    touch getUrlListOutput.csv
    # If previous run was aborted, this will add the output into the working file
    cat getUrlListOutputBuffer.csv >> getUrlListOutputCombined.csv
    # The search function gets a bit twitchy with apostrophes
    cat $TRACKLIST | sed "s/\'//g"  | sed "s/\,/ /g" >> tmp && mv tmp $TRACKLIST
    python seeklocatedownload_geturllist.py $TRACKLIST
    #cat getUrlListOutputBuffer.csv >> getUrlListOutputCombined.csv
}

function downloadAllTheThings () {
    cat getUrlListOutputCombined.csv | sed 's/\[//g' | sed "s/\'//g" | sed "s/\]//g" | sed 's/\"//g' | sed "s/\,//g" | sort | uniq >> tmp && mv tmp getUrlListOutputCombined.csv
        #| sed "s/'('/\ \-\ /g" | sed "s/')'//g" | sed "s/  / /g" 
    cat getUrlListOutputCombined.csv | while read LINE1
      do
        #rm -rf files/*
        echo $downloadAllTheThingsCounter ' ########## \n ' >> downloadAllTheThingsOutput.log
        URL=`echo "${LINE1}" | cut -d \|  -f 2`
        NAME=`echo "${LINE1}" | cut -d \|  -f 1 | sed 's/(/ - /g' | sed 's/)//g' | sed 's/  / /g'`
       # youtube-dl "${URL}" --no-playlist -o "files/%(title)s.mp3" -x --embed-thumbnail 
       

        echo "URL - ###############" $URL
        echo "NAME - ###############" $NAME
        ARTIST=`echo $NAME | sed 's/ - /-/g' | cut -d - -f 1 | sed 's/-/ - /g' | sed 's/  / /g'`
        TITLE=`echo $NAME |sed 's/ - /-/g' | cut -d - -f 2-20 | sed 's/-/ - /g' | sed 's/  / /g'`
        

        #>> downloadAllTheThingsOutput.log    
        ((downloadAllTheThingsCounter++))
        mv files/*.jpg artbuffer/"${downloadAllTheThingsCounter}".jpg
        SOURCE_DETAIL=`ls files/*`
        #mv files/* files/"${downloadAllTheThingsCounter}"
        #renameAllTheThings2 'files/*' 'ytb'
        #renameAllTheThings2 'artbuffer/*' 'jpg'



        sleep 2
#FILO=`ls files/`
#        ffmpeg -i "files/${FILO}" -vn -ab 192k -ar 44100 -metadata title="${TITLE}" -metadata ARTIST="${ARTIST}" -metadata COMMENT="${SOURCE_DETAIL}" -y "output/${NAME}.mp3"
        rename -x files/* files/${downloadAllTheThingsCounter}
        ls files/;
        pwd
        ls
        sleep 17
        read -p "Press any key to continue... ffmpeg -i ${FILE} -vn -ab 192k " -n1 -s
        ffmpeg -i "files/${downloadAllTheThingsCounter}" -vn -ab 192k -ar 44100 -metadata title="${TITLE}" -metadata ARTIST="${ARTIST}" -metadata COMMENT="${COMMENT}" -y "files/tmp2.mp3"
        ls files/;
        ffmpeg -i "tmp" -i "artbuffer/${downloadAllTheThingsCounter}.jpg" -c copy -map 0 -map 1 -metadata:s:v title="Cover (front)" -y "output/${NAME}.mp3"

        #rm -rf artbuffer/*
        #read -p "Press any key to continue... renameAllTheThings 1"
           # renameAllTheThings2
        #read -p "Press any key to continue... renameAllTheThings 2"
           # renameAllTheThings2
        #read -p "Press any key to continue... convertAllTheThings ytb ${SOURCE_DETAIL}"
            #convertAllTheThings ytb "${NAME}" "${SOURCE_DETAIL}"

      done
      cat downloadAllTheThingsOutput.log | grep -v  >> tmp && mv tmp downloadAllTheThingsOutput.log
}

function convertAllTheThings () {
    SRC_FORMAT=$1
    NAME=$2

    COMMENT="fish"
    for FILE in files/*.$SRC_FORMAT; do
        echo $convertAllTheThingsCounter ' ########## \n ' >> convertAllTheThingsOutput.log
        echo -e "Processing video '$FILE'"
        sleep 5
        ARTIST=`echo $NAME | cut -d - -f 1`
        TITLE=`echo $NAME | cut -d - -f 2`
        #ARTIST=`echo $FILE | cut -d - -f 1 | rev | cut -d \. -f 2 | rev`
        #TITLE=`echo $FILE | cut -d - -f 2 | rev | cut -d \. -f 2-40 | rev`
        #COMMENT=`echo $FILE | cut -d - -f 3,20 | rev | cut -d \. -f 2 | rev`
        echo "comment " $COMMENT
        echo
     #       if [[ $FILE != *\-* ]]; then
     #           TITLE=$ARTIST;
     #           ARTIST="Unknown";
     #           COMMENT="";
     #           echo "who dat?"
     #       fi
        rename -x ${FILE} tmp1
        read -p "Press any key to continue... ffmpeg -i ${FILE} -vn -ab 192k " -n1 -s
        ffmpeg -i "${FILE}" -vn -ab 192k -ar 44100 -metadata title="${TITLE}" -metadata ARTIST="${ARTIST}" -metadata COMMENT="${COMMENT}" -y "files/tmp2.mp3"
        ffmpeg -i "files/tmp" -i artbuffer/*.jpg -c copy -map 0 -map 1 -metadata:s:v title="Cover (front)" -y "output/${NAME}.mp3"

        #rm -rf files/*.ytb
        #>> convertAllTheThingsOutput.log;
       # for FILE2 in files/*; do
       #     read -p "Press any key to continue...  for FILE in files/*; do" -n1 -s
#
       #     ls file/
       #     ffmpeg -i "${FILE2}" -i artbuffer/*.jpg -c copy -map 0 -map 1 -metadata:s:v title="Cover (front)" -y "output/${FILE2}"
       #     #rm -rf "${FILE}"  >> convertAllTheThingsOutput.log
       # done
        rm -rf files/*
        rm -rf artbuffer/*
        sleep 5
        # >> convertAllTheThingsOutput.log
        ((convertAllTheThingsCounter++))
    done;
}

function renameAllTheThings2 () {
    RENAME_PATH=$1
    SUFFIX=$2
    rename  -x \
            -S "." " " \
        "${RENAME_PATH}"

    #SUFFIX=$1
    rename  -a TOASTMAN -c "${RENAME_PATH}"
    rename  -D "toastman" \
            -a GOATARSE --camelcase \
        "${RENAME_PATH}"

    rename  -D "GOATARSE" \
            -D "Goatarse" \
            -D "goatarse" \
        "${RENAME_PATH}"

    rename  -S _ - \
            -S "(" - \
            -D ")" \
            -S _ " " \
            -S - " - " \
            -S "- -" - \
            -S "--" - \
            -S '   ' ' ' \
            -S '  ' ' ' \
        "${RENAME_PATH}"
    rename  -D "toastman" "${RENAME_PATH}"
    rename  -a ".$SUFFIX" "${RENAME_PATH}"
    }


function renameAllTheThings () {
    rename  -x \
            -S "." " " \
            files/*

    #SUFFIX=$1
    rename  -a TOASTMAN -c files/*
    rename  -D "toastman" \
            -a GOATARSE --camelcase \
            files/*

    rename  -D "GOATARSE" \
            -D "Goatarse" \
            -D "goatarse" \
        files/*

    rename  -S _ - \
            -S "(" - \
            -z  \
            -S _ " " \
            -S " Ft " " Feat " \
            -D "Official Music Video" \
            -D "Full Song" \
            -D "Officialvideo" \
            -D "Official Video" \
            -D "Official Music Video" \
            -D "Music Video" \
            -D "Officialaudio" \
            -D "Official Audio" \
            -D "Best Quality" \
            -D "High Quality" \
            -D "Hd 720P" \
            -D "Hd720P" \
            -D "720P" \
            -D "- Hq" \
            -D "Hd 1080P" \
            -D "Hd1080P" \
            -D "1080P" \
            -D "Wmv" \
            -D "Hd Audio" \
            -D "Hdaudio" \
            -D "Audioonly" \
            -D "Audio Only" \
            -D "Audio Stream" \
            -D "With Lyrics" \
            -S - " - " \
            -S "- -" - \
            -S "--" - \
            -S "[" - \
            -D "]" \
            -S ' S ' 's ' \
            -S ' T ' 't ' \
            -S 'Aint' ' Aint ' \
            -S " Re " "re" \
            -S "Dont" "Dont " \
            -S "Ii" "GOATARSEII" \
            -S "Iii" "GOATARSEIII" \
            -S "  " " " \
        files/*

    rename  -D "GOATARSE" \
            -D "Goatarse" \
            -D "goatarse" \
        files/*

    cd files;
    rename  -e 's/(Hq)$//' \
            -e 's/(Hd)$//' \
            -e 's/(Lyrics)$//' \
            -e 's/[. -]$//' \
            -e 's/^[0-9]+//' \
            -e 's/^[. -]+//' \
            -e 's/^(Giant Leap - )+/1 Giant Leap - /' \
            -e 's/^(State - )+/808 State - /' \
            -e 's/^(Symmetry - )+/2Symmetry - /' \
            -e 's/^(Hero - )+/4Hero - /' \
            *
    cd ../;

    rename  -S "Rem " "REM " \
            -S "R E M " "REM " \
            -S " Vs " "VS " \
            -S "X - Press" "X-Press" \
            -S "N - Trance" "N-Trance" \
            -S "Deee - Lite" "Deee-Lite" \
            -S '   ' ' ' \
            -S '  ' ' ' \
        files/*

    rename  -a ".ytb" files/*


    rename -S " ." "." \
           -S "-." "." \
           -S '  ' ' ' \
        files/*   
    }

echo > downloadAllTheThingsOutput.log
echo > convertAllTheThingsOutput.log

convertAllTheThingsCounter=0
downloadAllTheThingsCounter=0

rm -rf files/*
rm -rf output/*
rm -rf artbuffer/*

mkdir files/
mkdir artbuffer/
mkdir -p output/files/





#getYoutubeUrlList $1

downloadAllTheThings

#cp -pr files files-bak

#rm -rf files/*.jpg

#renameAllTheThings 
#renameAllTheThings 
#convertAllTheThings ytb

#mv *.csv files/
#mv *.log files/

#mv files files-`date +%Y%m%d%H%M`
