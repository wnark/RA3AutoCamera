## 将视频转化为图片
[如何使用 ffmpeg 从视频文件中提取高质量的 JPEG 图像？](https://stackoverflow.com/questions/10225403/how-can-i-extract-a-good-quality-jpeg-image-from-a-video-file-with-ffmpeg)
[How to Install Latest FFMPEG 5.0 in CentOS 8/7 Ubuntu 20.04/18.04 CWP/Cpanel/Plesk/Ispconfig](https://www.mysterydata.com/how-to-install-latest-ffmpeg-4-in-centos-8-7-ubuntu-20-04-18-04-cwp-cpanel-plesk-ispconfig/)

[How can I use ffmpeg to split MPEG video into 10 minute chunks?](https://unix.stackexchange.com/questions/1670/how-can-i-use-ffmpeg-to-split-mpeg-video-into-10-minute-chunks)
### 以无损格式输出图像，例如 PNG：
不太好用，输出画面模糊

### 直接输出jpg

ffmpeg -i "Y:\cut_video\output000000001.mp4" -q:v 1 "Y:\cut_jpg\out-%09d.jpg"

### 切割视频

ffmpeg -i "Z:\xiaochangxin\video\ra3_shenmiao.mp4" -c copy -map 0 -segment_time 00:10:00 -f segment -reset_timestamps 1 "Z:\xiaochangxin\cut_video\output%09d.mp4"


