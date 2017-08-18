/*本代码实现的功能 
获取一个输入文件的参数信息*/
#include "libavformat/avformat.h"
#include "libavutil/pixdesc.h"
#include "libavutil/avutil.h"
#include "libavutil/time.h"
#include "Python.h"

#define BUFFER_SIZE 1024
//static int BufferCnt;
static int audio_st = -1;
static int video_st = -1;
int64_t lastTryTime ;
static int TimeOut = 10;
static int timeOutFlag = 0;

typedef struct stream_info{
	int64_t bitrate;
	AVRational framerate;
	int sample_rate;
	int channels;
    int width, height;
	int channel_layout;
    char *codec_type; 
	char *codec_name;
	char *profile;
	char *pix_fmt;
	char *sample_fmt;

}stream_info_t;
typedef struct input_info{
	AVDictionary *metadata;
    struct {
	int hours, mins, secs, us;
	}duration;
    int64_t bit_rate;
	char *format;
    unsigned int nb_streams;
	stream_info_t **stream;
}input_info_t;
int FF_init()
{
	int ret;
	av_register_all();
	ret = avformat_network_init();
	av_log_set_level(AV_LOG_ERROR); //AV_LOG_FATAL
	return ret;
}
void FF_log_set_level(int level)
{
	av_log_set_level(level);
}
void FF_set_timeout(int time)
{
	TimeOut = time;
}
static char *FF_memcpy(const char *s)
{
    char *ptr = NULL;
    if (s) {
        size_t len = strlen(s) + 1;
        ptr = av_mallocz(len);
        if (ptr)
            memcpy(ptr, s, len);
    }
    return ptr;
}
static char* FF_strncat(char * dst, const char * src, size_t size)
{
	return strncat(dst, src, size);
}
static void FF_get_metadata(AVDictionary *metadata,char *str)
{
	char buf_title[128]={0};
	char buf_artist[128]={0};
	int have_title = 0;
	int have_artist = 0;
	AVDictionaryEntry *tmp = NULL;
	//Buffer format must be started with {title:&title}{artist:&artist}...
	while ((tmp = av_dict_get(metadata, "", tmp, AV_DICT_IGNORE_SUFFIX))) {  
    	if(!strcmp(tmp->key,"title")&& !have_title){
			have_title = 1;
			sprintf(buf_title,"{%s:%s}",tmp->key,tmp->value);
			FF_strncat(str,buf_title, strlen(buf_title)+1);
		}
	}	
	if(!have_title)
		FF_strncat(str,"{}", 2);
	while ((tmp = av_dict_get(metadata, "", tmp, AV_DICT_IGNORE_SUFFIX))) {  
    	if(!strcmp(tmp->key,"artist")&& !have_artist){
			have_artist = 1;
			sprintf(buf_artist,"{%s:%s}",tmp->key,tmp->value);
			FF_strncat(str,buf_artist, strlen(buf_artist)+1);
		}
	}	

	if(!have_artist)
		FF_strncat(str,"{}", 2);

}
static int64_t FF_get_bitrate(AVCodecContext *ctx)
{
	int64_t bit_rate;
	int bits_per_sample;
		
	switch (ctx->codec_type) {
	case AVMEDIA_TYPE_VIDEO:
	case AVMEDIA_TYPE_DATA:
	case AVMEDIA_TYPE_SUBTITLE:
	case AVMEDIA_TYPE_ATTACHMENT:
		bit_rate = ctx->bit_rate;
		break;
	case AVMEDIA_TYPE_AUDIO:
		bits_per_sample = av_get_bits_per_sample(ctx->codec_id);
		bit_rate = bits_per_sample ? ctx->sample_rate * (int64_t)ctx->channels * bits_per_sample : ctx->bit_rate;
		break;
	default:
		bit_rate = 0;
		break;
		}
	return bit_rate;
}
static stream_info_t* FF_get_stream_info(AVCodecContext *codec_ctx,stream_info_t **stream)
{
	(*stream)=av_mallocz(sizeof(stream_info_t));
	const char *codec_type= NULL;
	codec_type = av_get_media_type_string(codec_ctx->codec_type);
	(*stream)->codec_type = FF_memcpy(codec_type);
	const char *codec_name= NULL;
	codec_name = avcodec_get_name(codec_ctx->codec_id);
	(*stream)->codec_name = FF_memcpy(codec_name);
	const char *profile = NULL;
	profile = avcodec_profile_name(codec_ctx->codec_id, codec_ctx->profile);
	if(profile)
		(*stream)->profile = FF_memcpy(profile);
	const char *pix_fmt = NULL;
	if(codec_ctx->pix_fmt != AV_PIX_FMT_NONE){
		pix_fmt = av_get_pix_fmt_name(codec_ctx->pix_fmt);
		(*stream)->pix_fmt = FF_memcpy(pix_fmt);
	}
	(*stream)->bitrate = FF_get_bitrate(codec_ctx);
	if (codec_ctx->codec_type == AVMEDIA_TYPE_VIDEO){
		//resolution ratio
		if (codec_ctx->width) {
			(*stream)->width = codec_ctx->width;
			(*stream)->height = codec_ctx->height;
		}	

	}else if(codec_ctx->codec_type == AVMEDIA_TYPE_AUDIO){
			(*stream)->sample_rate = codec_ctx->sample_rate;
			(*stream)->channels = codec_ctx->channels;
			(*stream)->channel_layout = codec_ctx->channel_layout;

			const char *sample_fmt;
		if (codec_ctx->sample_fmt != AV_SAMPLE_FMT_NONE) {
				sample_fmt = av_get_sample_fmt_name(codec_ctx->sample_fmt);
				(*stream)->sample_fmt = FF_memcpy(sample_fmt);
		}
	}				

	return (*stream);
}

static int interrupt_cb(void *ctx)
{
	int  time  = TimeOut;
	if(av_gettime() - lastTryTime > time *1000 *1000)
	{
		timeOutFlag = 1;
		av_log(NULL, AV_LOG_INFO, "Time out...!\n");
		return 1;
	}
	return 0;
}
int get_Mp3_info(const char* url,input_info_t **info)
{
	int ret;
	unsigned int i;
	AVFormatContext *fmt_ctx = NULL;
	fmt_ctx = avformat_alloc_context();
	lastTryTime = av_gettime();
	fmt_ctx->interrupt_callback.callback = interrupt_cb;
	if ((ret = avformat_open_input(&fmt_ctx, url, NULL, NULL)) < 0) {
			av_log(NULL, AV_LOG_ERROR, "Cannot open input file!\n");
			return ret;
		}
	if(fmt_ctx->iformat->name){
			(*info)->format = FF_memcpy(fmt_ctx->iformat->name);
	}
	if ((ret = avformat_find_stream_info(fmt_ctx, NULL)) < 0) {
			av_log(NULL, AV_LOG_ERROR, "Cannot find stream information!\n");
			return ret;
		}
	(*info)->nb_streams = fmt_ctx->nb_streams;
	(*info)->bit_rate = fmt_ctx->bit_rate;

	if (fmt_ctx->duration != AV_NOPTS_VALUE) {
		int hours, mins, secs, us;
		int64_t duration = fmt_ctx->duration + (fmt_ctx->duration <= INT64_MAX - 5000 ? 5000 : 0);
		secs  = duration / AV_TIME_BASE;
		us	  = duration % AV_TIME_BASE;
		mins  = secs / 60;
		secs %= 60;
		hours = mins / 60;
		mins %= 60;
		(*info)->duration.hours = hours;
		(*info)->duration.mins = mins;
		(*info)->duration.secs = secs;
		(*info)->duration.us = (100 * us) / AV_TIME_BASE;		
	}

	AVDictionaryEntry *tmp = NULL;
	while ((tmp = av_dict_get(fmt_ctx->metadata, "", tmp, AV_DICT_IGNORE_SUFFIX))) {  
 	//  av_log(NULL, AV_LOG_INFO, "%s: %s\n", tmp->key, tmp->value);  
		av_dict_set(&((*info)->metadata),tmp->key, tmp->value,0);
	}  
	(*info)->stream = av_mallocz(sizeof(stream_info_t *) * (*info)->nb_streams);
	for (i = 0; i < fmt_ctx->nb_streams; i++) {
		AVStream *stream = fmt_ctx->streams[i];
		AVCodec *dec = avcodec_find_decoder(stream->codecpar->codec_id);
		AVCodecContext *codec_ctx;
		if (!dec) {
			av_log(NULL, AV_LOG_ERROR, "Failed to find decoder for stream #%u\n", i);
			return AVERROR_DECODER_NOT_FOUND;
		}
		codec_ctx = avcodec_alloc_context3(dec);
		if (!codec_ctx) {
			av_log(NULL, AV_LOG_ERROR, "Failed to allocate the decoder context for stream #%u\n", i);
			return AVERROR(ENOMEM);
		}
		
		ret = avcodec_parameters_to_context(codec_ctx, stream->codecpar);
		if (ret < 0) {
			av_log(NULL, AV_LOG_ERROR, "Failed to copy decoder parameters to input decoder context "
					   "for stream #%u\n", i);
			return ret;
		}
		if (codec_ctx->codec_type == AVMEDIA_TYPE_VIDEO
					|| codec_ctx->codec_type == AVMEDIA_TYPE_AUDIO) {
			stream_info_t *st=NULL;	

			(*info)->stream[i]=FF_get_stream_info(codec_ctx,&st);
			(*info)->stream[i]->framerate.num = stream->avg_frame_rate.num;
			(*info)->stream[i]->framerate.den = stream->avg_frame_rate.den;
			if(codec_ctx->codec_type == AVMEDIA_TYPE_VIDEO)
				video_st = i;
			else
				audio_st = i;
			avcodec_close(codec_ctx);
		}
		
	}
	avformat_close_input(&fmt_ctx);

	return 0;
}
static int FF_uninit(input_info_t *info)
{
	int i;
	for(i = 0;i < info->nb_streams;i ++){
		av_free(info->stream[i]->codec_type);
		av_free(info->stream[i]->codec_name);
		av_free(info->stream[i]->profile);
		av_free(info->stream[i]->pix_fmt);
		av_free(info->stream[i]->sample_fmt);
		av_free(info->stream[i]);
	}
	av_free(info->format);
	av_dict_free(&(info->metadata));
	av_free(info);
	return 0;
}

int FF_detect_Live(const char *url)
{
	int ret;
	AVFormatContext *fmt_ctx = NULL;

	fmt_ctx = avformat_alloc_context();
	lastTryTime = av_gettime();
	fmt_ctx->interrupt_callback.callback = interrupt_cb;

	if ((ret = avformat_open_input(&fmt_ctx, url, NULL, NULL)) < 0) {
			av_log(NULL, AV_LOG_ERROR, "Cannot open input file!\n");
			return ret;
		}
	if ((ret = avformat_find_stream_info(fmt_ctx, NULL)) < 0) {
			av_log(NULL, AV_LOG_ERROR, "Cannot find stream information!\n");
			return ret;
		}
	if(fmt_ctx->nb_streams < 1)
		return AVERROR_STREAM_NOT_FOUND;
	avformat_close_input(&fmt_ctx);
	return 0;
}

int  struct_to_str(const char *url,char *buf)//covert the struct to string format
{
	input_info_t *info = NULL;
	int ret;
	info = av_mallocz(sizeof(input_info_t));
    if (!info)
        return -1;
	ret = get_Mp3_info(url,&info);
	if(ret < 0)
		return ret;
	FF_get_metadata(info->metadata,buf);
	FF_uninit(info);//free malloced memory
	return 0;
}

//python interface
static PyObject* FFmpeg_init(PyObject*self,PyObject* args){
	int ret;
	PyObject* retval;
	retval = (PyObject*)Py_BuildValue("i",ret=FF_init());
	return retval;
}
static PyObject* FFmpeg_setLogLevel(PyObject*self,PyObject* args){
	int ret = 0;
	int level;
	PyObject* retval;
	if (!PyArg_ParseTuple(args, "i", &level))
		return NULL;
	FF_log_set_level(level);
	retval = (PyObject*)Py_BuildValue("i",ret);
	return retval;
}
static PyObject* FFmpeg_setTimeout(PyObject*self,PyObject* args){
	int time;
	int ret = 0;
	PyObject* retval;
	if (!PyArg_ParseTuple(args, "i", &time))
		return NULL;
	FF_set_timeout(time);
	retval = (PyObject*)Py_BuildValue("i",ret);
	return retval;
}

static PyObject *FFmpeg_getMp3Info(PyObject *self, PyObject *args) {
	char *url_str; 
	int ret;
	PyObject* retval;
	if (!PyArg_ParseTuple(args, "s", &url_str))
		return NULL;
	char buf[BUFFER_SIZE]={0};
	ret = struct_to_str(url_str,buf);
	retval = (PyObject*)Py_BuildValue("s",buf);
	return retval;
}
static PyObject *FFmpeg_getLiveStatus(PyObject *self, PyObject *args) {
	char *url_str; 
	int ret;
	PyObject* retval;
	if (!PyArg_ParseTuple(args, "s", &url_str))
		return NULL;
	ret = FF_detect_Live(url_str);
	retval = (PyObject*)Py_BuildValue("i",ret);
	return retval;
}
static PyObject *FFmpeg_err2str(PyObject *self, PyObject *args) {
	int error;
	PyObject* retval;
	if (!PyArg_ParseTuple(args, "i", &error))
		return NULL;
	retval = (PyObject*)Py_BuildValue("s",av_err2str(error));
	return retval;
}

static PyMethodDef FFmpegMethods[] = {
	{ "init", FFmpeg_init, METH_VARARGS },
	{ "getMp3Info", FFmpeg_getMp3Info, METH_VARARGS },
	{ "getLiveStatus", FFmpeg_getLiveStatus, METH_VARARGS },
	{ "setLogLevel", FFmpeg_setLogLevel, METH_VARARGS },
	{ "setTimeout", FFmpeg_setTimeout, METH_VARARGS },
	{ "err2str", FFmpeg_err2str, METH_VARARGS },
	{ NULL, NULL },
};
void initFFmpeg() {
	Py_InitModule("FFmpeg", FFmpegMethods);
}


