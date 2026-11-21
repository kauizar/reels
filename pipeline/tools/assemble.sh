#!/usr/bin/env bash
# Junta cenas + narração no arquivo final. uso: assemble.sh <pasta_video> <saida.mp4>
set -e; D="$1"; OUT="$2"
ls "$D"/sc_*.mp4 | grep -v tmp | sort | sed "s#^#file '#; s#\$#'#" > "$D/list.txt"
ffmpeg -v error -y -f concat -safe 0 -i "$D/list.txt" -c copy "$D/video.mp4"
VD=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$D/video.mp4")
ffmpeg -v error -y -i "$D/video.mp4" -i "$D/narr.mp3" -map 0:v -map 1:a -af apad -c:v libx264 -crf 24 -maxrate 1100k -bufsize 2200k \
  -profile:v main -preset veryfast -pix_fmt yuv420p -c:a aac -b:a 128k -t "$VD" -movflags +faststart "$OUT"
ffprobe -v error -show_entries format=duration,size -of csv=p=0 "$OUT"
