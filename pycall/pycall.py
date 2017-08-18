import FFmpeg
FFmpeg.init()
url='https://www.indiamp3.com/audio/Indian Movies/Indian Movies Hindi Mp3 Songs/Aashiqui 2 (2013)/songs/Aasan Nahin Yahan @ IndiaMp3.Com.mp3'
url = 'https://www.indiamp3.com/audio/Indian Movies/Indian Movies Hindi Mp3 Songs/Military Raaj (1998)/songs/Aagey Se Dekha Piche Se Dekha @ IndiaMp3.Com.mp3'
url = 'https://www.indiamp3.com/audio/Indian%20Movies/Indian%20Movies%20Hindi%20Mp3%20Songs/Mismatch%20(2009)/songs/Its%20A%20Mismatch%20(Remix)%20@%20IndiaMp3.Com.mp3'
url = 'https://www.indiamp3.com/audio/Indian%20Movies/Indian%20Movies%20Hindi%20Mp3%20Songs/Laadla/songs/Dhik%20Ta%20Na%20Na%20(IndiaMp3.com).mp3'
url = 'https://www.indiamp3.com/audio/Indian Movies/Indian Movies Hindi Mp3 Songs/Hulchal/songs/Dekho Zara .mp3'
url = url.replace(' ','%20')
url2='https://www.indiamp3.com/audio/Tamil Songs/Tamil Mp3 Songs/A Aa (2016)/A Aa (2016)/Anasuya Kosam @ IndiaMp3.Com.mp3'
url3='rtmp://51.254.198.119/live/?sn=1234/FR_FRANCE_3'
url4=''
#FFmpeg.setLogLevel(8)
#FFmpeg.setTimeout(1)
msg=FFmpeg.getMp3Info(url)
ret=FFmpeg.getLiveStatus(url3)
retstr=FFmpeg.err2str(ret)
print(msg)
#print(ret)
print(retstr)

