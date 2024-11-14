#!/bin/sh

# while true; do
OUTPUT_FILE="output_$(date +'%Y%m%d_%H%M%S').mp4"
# Inicie o ffmpeg com o vídeo especificado e transmita para o servidor RTSP
ffmpeg -i "$VIDEO_PATH" -r 25 -c:v copy -c:a aac "$OUTPUT_FILE" -f rtsp rtsp://mediamtx:8554/mystream

ffplay rtsp://mediamtx:8554/mystream

# Aguarde até que o ffmpeg termine de executar
wait
# done