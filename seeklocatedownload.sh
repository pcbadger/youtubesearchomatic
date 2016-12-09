#!/bin/bash
set -x

function sortRawList () {

    INPUT=$1
    OUTPUT=0_sortedList
    TICKER=0
    TOTAL=`cat ${INPUT} | wc -l`
    rm ${OUTPUT}.csv
    touch ${OUTPUT}.csv
        cat ${INPUT} | while read LINE
            do
                LINE=`echo ${LINE} | sed "s/([\',\|])//g" | sed 's/ – /|/g' | sed 's/ –/|/g' | sed 's/– /|/g'`
                TITLE=`echo ${LINE} | rev | cut -d \| -f 2- | rev`
                    if ! [[ ${LINE} =~ '|' ]]; then
                        ARTIST='Unknown'
                    else
                        ARTIST=`echo ${LINE} | rev | cut -d \| -f 1 | rev`
                    fi
                echo "Sorting: ${TICKER} of ${TOTAL}"
                echo ${ARTIST}"|"${TITLE} >> ${OUTPUT}.csv
                ((TICKER++))
            done
        myListFormat ${OUTPUT}.csv
        echo "Sorted!"
    #exit 0
}

function tidyList () {
    listToTidy=${1}.csv
    tidiedList=${1}Long.csv
    touch ${listToTidy}
    echo $'\n' >> ${tidiedList}
    echo "tidied - "${tidiedList}
    cat ${listToTidy} >> ${tidiedList}
    #cat 2_listWithUrlLong.csv | sed "s/\', \"/|/g" |  sed "s/\', \'/|/g" | sed "s/\[\'//g"  | sed "s/\[\"//g"  | sed "s/\'('\'//g"  | sed "s/\'')'//g"  | sed "s/\'\]//g"  | sed "s/\"\]//g" | sort | uniq > tmp;
    cat ${tidiedList} | sort | uniq > bufftmp; mv bufftmp ${tidiedList}
    #rm -rf ${listToTidy}
}

function myListFormat () {
    INPUT=$1
    TICKER=0
    TOTAL=`cat ${INPUT} | wc -l`
    cat ${INPUT} | while read LINE
        do
            echo "Formating the hell out of this list: ${TICKER} of ${TOTAL}"
            URL=`echo ${LINE} | cut -d \| -f 3`
            LINE=`echo ${LINE} | sed "s/Unknown|/|/g" | sed "s/[\[\'\’\‘.)]//g" | sed "s/(/ - /g" \
            | sed 's/]//g' | sed 's/  / /g' | sed 's/&/And/g' | sed "s/[Ö]/O/g" | sed "s/[øöô]/o/g" \
            | sed "s/[é]/e/g" | sed "s/[µ]/u/g" | sed "s/[ç]/c/g"`
            ARTIST=`echo ${LINE} | cut -d \| -f 1 | sed 's/,/ /g' | sed 's/  / /g'`
            TITLE=`echo ${LINE} | cut -d \| -f 2`
            echo ${ARTIST}'|'${TITLE}'|'${URL} >> tmpo
            cat tmpo | sort | uniq >> tmpo2; mv tmpo2 ${INPUT}
        done
    rm -rf tmpo
}

function getYoutubeUrlList () {
    TRACKLIST=$1
    #echo '\n' >> bufferout.csv
    #touch bufferout.csv
    # If previous run was aborted, this will add the output into the working file
        tidylist 2_listWithUrl
    # The search function gets a bit twitchy with apostrophes
    rm -rf tmp
    cat $TRACKLIST | sed "s/Unknown|/|/g" | sed "s/([\',\])//g" >> tmp && mv tmp 1_sortedTrackList.csv
    python seeklocatedownload_geturllist.py 1_sortedTrackList.csv
        tidyList 2_listWithUrl
       myListFormat 2_listWithUrlLong.csv
    exit 1
}

function downloadAllTheThings () {
        #| sed "s/'('/\ \-\ /g" | sed "s/')'//g" | sed "s/  / /g"
    #rm -rf files/*
    #rm -rf artbuffer/*
    #rm -rf filebuffer/*
    INPUT=S{1}
    OUPUT=${2}
    downloadAllTheThingsCounter=1
    tidyList 3_listWithUrlFiles
    TOTAL=`cat 2_listWithUrlLong.csv | wc -l`
    cat 2_listWithUrlLong.csv | while read LINE
      do
        echo "Downloading "$downloadAllTheThingsCounter " of ${TOTAL} \n "
        ARTIST=`echo "${LINE}" | cut -d \|  -f 1`
        TITLE=`echo "${LINE}" | cut -d \|  -f 2`
        URL=`echo "${LINE}" | cut -d \|  -f 3`
        if [[ -z ${URL} ]]; then
            URL=${TITLE}
            TITLE=${ARTIST}
            ARTIST="Unknown"
        fi
        #NAME=`echo "${LINE}" | cut -d \|  -f 1 | sed 's/(/ - /g' | sed 's/)//g' | sed 's/  / /g'`
        youtube-dl "${URL}" --no-playlist -o "files/%(title)s.mp3" -x --embed-thumbnail 
       
        echo "ARTIST - ###############" $ARTIST
        echo "TITLE - ###############" $TITLE
        echo "URL - ###############" $URL

        #ARTIST=`echo $NAME | sed 's/ - /-/g' | cut -d - -f 1 | sed 's/-/ - /g' | sed 's/  / /g'`
        #TITLE=`echo $NAME |sed 's/ - /-/g' | cut -d - -f 2-20 | sed 's/-/ - /g' | sed 's/  / /g'`
        

        #>> downloadAllTheThingsOutput.log    
        
        mv files/*.jpg artbuffer/"${downloadAllTheThingsCounter}".jpg
        SOURCE_DETAIL=`ls files/*   `
        SOURCE_DETAIL=`echo ${SOURCE_DETAIL} | cut -d \/ -f 2-`
        mv files/* filebuffer/"${downloadAllTheThingsCounter}.mp3"
        #renameAllTheThings2 'files/*' 'ytb'
        #renameAllTheThings2 'artbuffer/*' 'jpg'
        
        echo ${downloadAllTheThingsCounter}'|'${ARTIST}'|'${TITLE}'|'${SOURCE_DETAIL} >> 3_listWithUrlFiles.csv


        #sleep 2
#FILO=`ls files/`
#        ffmpeg -i "files/${FILO}" -vn -ab 192k -ar 44100 -metadata title="${TITLE}" -metadata ARTIST="${ARTIST}" -metadata COMMENT="${SOURCE_DETAIL}" -y "output/${NAME}.mp3"
        #rename -x files/* files/${downloadAllTheThingsCounter}
        #ls files/;
        #pwd
        #ls
        #sleep 17
        #read -p "Press any key to continue... ffmpeg -i ${FILE} -vn -ab 192k " -n1 -s
        #ffmpeg -i "files/${downloadAllTheThingsCounter}" -vn -ab 192k -ar 44100 -metadata title="${TITLE}" -metadata ARTIST="${ARTIST}" -metadata COMMENT="${COMMENT}" -y "files/tmp2.mp3"
        #ls files/;
        #ffmpeg -i "tmp" -i "artbuffer/${downloadAllTheThingsCounter}.jpg" -c copy -map 0 -map 1 -metadata:s:v title="Cover (front)" -y "output/${NAME}.mp3"

        #rm -rf artbuffer/*
        #read -p "Press any key to continue... renameAllTheThings 1"
           # renameAllTheThings2
        #read -p "Press any key to continue... renameAllTheThings 2"
           # renameAllTheThings2
        #read -p "Press any key to continue... convertAllTheThings ytb ${SOURCE_DETAIL}"
            #convertAllTheThings ytb "${NAME}" "${SOURCE_DETAIL}"
        ((downloadAllTheThingsCounter++))
      done
      #cat downloadAllTheThingsOutput.log | grep -v  >> tmp && mv tmp downloadAllTheThingsOutput.log
}

function convertAllTheThings () {
    INPUT=${1}
    SRC_FORMAT=$1
    NAME=$2
    #TICKER=0
    TOTAL=`cat ${INPUT} | wc -l`
    cat ${INPUT} | while read LINE
        do
            TICKER=`${LINE} | cut -d \| -f 1`
            ARTIST=`${LINE} | cut -d \| -f 2`
            TITLE=`${LINE} | cut -d \| -f 3`
            COMMENT=`${LINE} | cut -d \| -f 4`

            if [[ -z ${ARTIST} ]]; then
                ARTIST=`Unknown`
            fi
            if [[ -n ${COMMENT} ]]; then
                IMAGE=artbuffer/${TICKER}.jpg
                if [[ -e ${IMAGE} ]]; then
                    IMAGE='mystery.gif'
                fi

                echo "Converting: ${TICKER} of ${TOTAL}"

                ffmpeg -i "filebuffer/${TICKER}.mp3" -vn -ab 192k -ar 44100 -y "tmp.mp3"
                echo "Adding metadata: ${TICKER} of ${TOTAL}"
                ffmpeg -i "tmp.mp3" -i '${IMAGE}' -c copy -map 0 \
                -map 1 -metadata:s:v title="Cover (front)" -metadata title='${TITLE}'\
                 -metadata ARTIST='${ARTIST}' -metadata COMMENT='${COMMENT}' -y "output/${TITLE} - ${ARTIST}.mp3"
        
            else
                echo '${TICKER} - ${TITLE} - ${ARTIST} not downloaded' >> error.log
                echo '${TICKER} - ${TITLE} - ${ARTIST} not downloaded'
            fi
        done
            #rename -x ${FILE} tmp1
            #read -p "Press any key to continue... ffmpeg -i ${FILE} -vn -ab 192k " -n1 -s
            #ffmpeg -i "filebuffer/${TICKER}.mp3" -vn -ab 192k -ar 44100 -metadata title="${TITLE}" -metadata ARTIST="${ARTIST}" -metadata COMMENT="${COMMENT}" -y "output/${TICKER}.mp3"
            #ffmpeg -i "files/tmp" -i artbuffer/*.jpg -c copy -map 0 -map 1 -metadata:s:v title="Cover (front)" -y "output/${NAME}.mp3"




    #COMMENT="fish"
    #for FILE in files/*.$SRC_FORMAT; do
        #echo $convertAllTheThingsCounter ' ########## \n ' >> convertAllTheThingsOutput.log
        #echo -e "Processing video '$FILE'"
        #sleep 5
        #ARTIST=`echo $NAME | cut -d - -f 1`
        #TITLE=`echo $NAME | cut -d - -f 2`
        #ARTIST=`echo $FILE | cut -d - -f 1 | rev | cut -d \. -f 2 | rev`
        #TITLE=`echo $FILE | cut -d - -f 2 | rev | cut -d \. -f 2-40 | rev`
        #COMMENT=`echo $FILE | cut -d - -f 3,20 | rev | cut -d \. -f 2 | rev`
        #echo "comment " $COMMENT
        #echo
     #       if [[ $FILE != *\-* ]]; then
     #           TITLE=$ARTIST;
     #           ARTIST="Unknown";
     #           COMMENT="";
     #           echo "who dat?"
     #       fi

        #rm -rf files/*.ytb
        #>> convertAllTheThingsOutput.log;
       # for FILE2 in files/*; do
       #     read -p "Press any key to continue...  for FILE in files/*; do" -n1 -s
#
       #     ls file/
       #     ffmpeg -i "${FILE2}" -i artbuffer/*.jpg -c copy -map 0 -map 1 -metadata:s:v title="Cover (front)" -y "output/${FILE2}"
       #     #rm -rf "${FILE}"  >> convertAllTheThingsOutput.log
       # done
        #rm -rf files/*
        #rm -rf artbuffer/*
        #sleep 5
        # >> convertAllTheThingsOutput.log
        #((convertAllTheThingsCounter++))
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

#convertAllTheThingsCounter=0
#downloadAllTheThingsCounter=0

rm -rf files/*
rm -rf output/*
rm -rf artbuffer/*
rm -rf filebuffer/*

mkdir filebuffer
mkdir files/
mkdir artbuffer/
mkdir -p output/files/



while test $# -gt 0; do
        case "$1" in
                -h|--help)
                        echo "$package - attempt to capture frames"
                        echo " "
                        echo "$package [options] application [arguments]"
                        echo " "
                        echo "options:"
                        echo "-h, --help                show brief help"
                        echo "-a, --action=ACTION       specify an action to use"
                        echo "-o, --output-dir=DIR      specify a directory to store output in"
                        exit 0
                        ;;
                -f)
                    #file name
                        shift
                        if test $# -gt 0; then
                                export fileIn=$1
                                    if [[ -n ${fileIn} && -n ${trackIn} ]]; then
                                        echo "can't have a filez and track"
                                        echo "f $fileIn"
                                        echo "t $trackin"
                                        break
                                    fi
                                cat $fileIn > rawTrack.csv
                                export fileOut='rawTrack.csv'
                        else
                                echo "no filename specified"
                                break
                        fi
                        shift
                        ;;
                -t)
                    #single track
                        shift
                        if test $# -gt 0; then
                                export trackIn=$1
                                    if [[ -n ${fileIn} && -n ${trackIn} ]]; then
                                        echo "can't have a file and track"
                                        break
                                    fi
                                echo $trackIn > rawTrack.csv
                                export fileOut='rawTrack.csv'
                        else
                                echo "no track specified"
                                break
                        fi
                        shift
                        ;;
                -S)
                    #sortlist
                        shift
                        if [[ -n ${fileOut} ]]; then
                            export sortingList="true"
                        else
                            echo "no list or track specified"
                            break
                        fi
                        shift
                        ;;
                -G*)
                    #Get URL List
                        shift
                        #if [[ -n ${fileOut} ]]; then
                            export gettingList="true"
                        #    echo "GET IT"
                        #else
                        #    echo "no list or track specified"
                        #    break
                        #fi
                        shift
                        ;;
                -D*)
                    #Downloadfiles
                        shift
                            export downloadingFiles="true"
                        ;;
                -C*)
                    #ConvertFiles
                        shift
                            export convertingFiles="true"
                        ;;
                *)
                        break
                        ;;
        esac
done


    if [[ -n ${sortingList} ]]; then
        sortRawList rawTrack.csv
        rm rawTrack.csv
    fi

    if [[ -n ${gettingList} ]]; then
        echo "get it"
        getYoutubeUrlList 0_sortedList.csv
    fi


    if [[ -n ${downloadingFiles} ]]; then
        echo "Downloading"
        downloadAllTheThings 
        #3_listWithUrlFiles.csv
    fi

    if [[ -n ${convertingFiles} ]]; then
        echo "Converting"
        convertAllTheThings 3_listWithUrlFiles.csv
    fi


#getYoutubeUrlList $1

#downloadAllTheThings

#cp -pr files files-bak

#rm -rf files/*.jpg

#renameAllTheThings 
#renameAllTheThings 
#convertAllTheThings ytb

#mv *.csv files/
#mv *.log files/

#mv files files-`date +%Y%m%d%H%M`
