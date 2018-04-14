@echo off

docker run --rm -it -v %cd%:/data record_casts --width 120 --height 40
docker run --rm -it -v %cd%:/data convert_casts
