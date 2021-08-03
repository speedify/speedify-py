
# rtmp sends 128 byte video chunks, 64 byte audio
# 1-13 byte rtmp header, plus 44 bytes of tcp/ip headers, should be around 178 bytes per packet
speedtests = {
rtmp:{
  levels:[
    {name:"4K / 2160p @60 fps",resolution="3840x2160p","protocol="tcp", up="51M", mss="178" },
    {name:"4K / 2160p @30 fps",resolution="3840x2160p","protocol="tcp", up="34M", mss="178" },
    {name:"1440p @60 fps",resolution="2560x1440","protocol="tcp", up="18M", mss="178" },
    {name:"1440p @30 fps",resolution="2560x1440","protocol="tcp", up="13M", mss="178" },
    {name:"1080p @60 fps",resolution="1920x1080","protocol="tcp", up="9M", mss="178" },
    {name:"1080p @30 fps",resolution="1920x1080","protocol="tcp", up="6M", mss="178" },
    {name:"720p @60 fps",resolution="1280x720","protocol="tcp", up="6M", mss="178" },
    {name:"720p @30 fps",resolution="1280x720","protocol="tcp", up="4M", mss="178" },
    {name:"480p",resolution="854x480","protocol="tcp", up="2M", mss="178" },
    {name:"360p",resolution="854x480","protocol="tcp", up="1M", mss="178" },
    {name:"240p",resolution="426x240","protocol="tcp", up="700K", mss="178" },
}
}

def runTest(testspec):
    protocol = testspec["protocol"]
    proto_flag = ""
    if protocol == "udp":
        proto_flag = "-u"
    else:
        pass
    mss_flag = ""
    if protocol != "udp" and "mss" in testspec:
        mss = "-M " + testspec[mss]
    bandwidth_up = testspec["up"]
    #bandwidth_down = testspec["down"]
    cmd = "iperf3 -c 10.202.0.1 -J -t 10 " + proto_flag + " " +mss + " -b " + bandwidth_up
    print("cmd:" + cmd)



# source https://support.google.com/youtube/answer/2853702?hl=en#zippy=%2Ck-p-fps%2Cp-fps%2Cp
# 4K / 2160p @60 fps
# Resolution: 3840x2160p
# Video Bitrate Range: 20,000-51,000 Kbps
# 4K / 2160p @30 fps
# Resolution: 3840x2160p
# Video Bitrate Range: 13,000-34,000 Kbps
# 1440p @60 fps
# Resolution: 2560x1440
# Video Bitrate Range: 9,000-18,000 Kbps
# 1440p @30 fps
# Resolution: 2560x1440
# Video Bitrate Range: 6,000-13,000 Kbps
# 1080p @60 fps
# Resolution: 1920x1080
# Video Bitrate Range: 4,500-9,000 Kbps
# 1080p
# Resolution: 1920x1080
# Video Bitrate Range: 3,000-6,000 Kbps
# 720p @60 fps
# Resolution: 1280x720
# Video Bitrate Range: 2,250-6,000 Kbps
# 720p
# Resolution: 1280x720
# Video Bitrate Range: 1,500-4,000 Kbps
# 480p
# Resolution: 854x480
# Video Bitrate Range: 500-2,000 Kbps
# 360p
# Resolution: 640x360
# Video Bitrate Range: 400-1,000 Kbps
# 240p
# Resolution: 426x240
# Video Bitrate Range: 300-700 Kbps
