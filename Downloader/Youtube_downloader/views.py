from django.shortcuts import render, redirect, HttpResponse
from django.http import FileResponse, Http404
from .forms import YouTubeURLForm
from yt_dlp import YoutubeDL
import re, os, logging
import ipcalc, unicodedata, urllib.parse


logger = logging.getLogger('Youtube_downloader_log')
                           
def local(request): #bypass authentication if request is from local network
    localnetwork = ['10.0.0.0/8','172.16.0.0/12','192.168.0.0/16']
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR") # get original IP if running Nginx as reverse proxy
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()  
    else:
        ip = request.META.get("REMOTE_ADDR") # get IP if running Django as web server
    for subnet in localnetwork:
        if ip in ipcalc.Network(subnet):
            return True
    return False

def sanitize_filename(title, max_length=40):
    # Normalize to NFKC form (standardizes characters without removing non-ASCII)
    title = unicodedata.normalize('NFKC', title)
    # Remove unsafe characters (preserves Chinese/Unicode word characters)
    title = re.sub(r'[^\w\s_.-]', '', title, flags=re.UNICODE)
    # Replace spaces with underscores
    title = re.sub(r'\s+', '_', title)
    # Truncate and clean edges
    return title[:max_length].strip('_')

def sanitize_youtube_url(url):
    """Removes playlist and other extra params to force single video download"""
    parsed_url = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed_url.query)
    video_id = query.get("v", [None])[0]
    if video_id:
        return f"https://www.youtube.com/watch?v={video_id}"
    return url

def download_youtube(request):
    if request.user.is_authenticated != True:
        if not local(request):
            return redirect ('/login/?next=/youtube_downloader')
    if request.method == 'POST':
        form = YouTubeURLForm(request.POST)
        if form.is_valid():
            input_url = sanitize_youtube_url(form.cleaned_data["url"])
            action = request.POST.get('action')
            if 'video' in action: #download MP4
                try:
                    with YoutubeDL({'quiet': True}) as ydl: #set quiet to False for debug
                        info_dict = ydl.extract_info(input_url, download=False)
                        raw_title = info_dict.get('title', 'Video')
                        safe_title = sanitize_filename(raw_title)
                    output_template = f'/tmp/{safe_title}.%(ext)s'
                    filepath = f"/tmp/{safe_title}.mp4"
                    
                    if '480' in action:
                        ydl_opts = {
                            'format': 'bestvideo[height<=480]+bestaudio/best/best[height<=480]',
                            'merge_output_format': 'mp4',
                            'outtmpl': output_template,
                            'postprocessors': [
                                {
                                    'key': 'FFmpegVideoConvertor',
                                    'preferedformat': 'mp4',
                                },
                            ],
                            'postprocessor_args': [
                                '-vf', 'scale=640:480',      # Resize to iPod
                                '-r', '30',                  # Frame rate
                                '-vcodec', 'libx264',        # H.264 codec
                                '-profile:v', 'baseline',        # for ipod touch
                                '-level', '3.0',
                                '-b:v', '1500k',              # Video bitrate
                                '-acodec', 'aac',
                                '-b:a', '128k',              # Audio bitrate
                                '-ar', '44100',
                                '-ac', '2'
                            ],
                            'quiet': True,
                            'verbose': True,
                            'noplaylist': True,
                            'user_agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                        '(KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                        }
                    elif '720' in action:
                        ydl_opts = {
                            'quiet': True,
                            'verbose': True,
                            'noplaylist': True,
                            'format': 'bestvideo[height<=720]+bestaudio/best',  # download 720p video
                            'merge_output_format': 'mp4',
                            'outtmpl': output_template,
                            'user_agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                        '(KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                        }
                    else:
                        ydl_opts = {
                            'quiet': True, 
                            'verbose': True,
                            'noplaylist': True,
                            'format': 'bestvideo[height<=1080]+bestaudio/best', #download 1080p HD video
                            'merge_output_format': 'mp4',
                            'outtmpl': output_template,
                            'user_agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                        '(KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                        }
                    with YoutubeDL(ydl_opts) as ydl:
                        ydl.download([input_url])
                    # Save path and title to session
                    request.session['downloaded_filepath'] = filepath
                    request.session['video_title'] = raw_title
                    return render(request, 'Youtube_downloader.html', {
                        'download_ready': True,
                        'video_title': raw_title,
                        'user_auth': True,
                    })
                except Exception as e:
                    return HttpResponse(f"An error occurred: {e}", status=500)
            
            elif action == 'mp3': # download MP3
                try:
                    with YoutubeDL({'quiet': True}) as ydl:
                        info_dict = ydl.extract_info(input_url, download=False)
                        raw_title = info_dict.get('title', 'audio')

                    safe_title = sanitize_filename(raw_title)
                    output_path = f"/tmp/{safe_title}.%(ext)s"  # Used by yt-dlp
                    mp3_path = f"/tmp/{safe_title}.mp3"
                    ydl_opts = {
                        'quiet': True,
                        'format': 'bestaudio/best',
                        'outtmpl': output_path,
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                    }
                    with YoutubeDL(ydl_opts) as ydl:
                        ydl.download([input_url])
                    request.session['downloaded_filepath'] = mp3_path
                    request.session['video_title'] = raw_title
                    return render(request, 'Youtube_downloader.html', {
                        'download_ready': True,
                        'video_title': raw_title,
                        'user_auth': True,
                    })
                except Exception as e:
                    return HttpResponse(f"An error occurred: {e}", status=500)
    return render(request, 'Youtube_downloader.html',{ 'input_url': YouTubeURLForm(), 'user_auth': True})

class DeletableFileResponse(FileResponse):
    def __init__(self, file, filepath, *args, **kwargs):
        self.filepath = filepath
        super().__init__(file, *args, **kwargs)

    def close(self):
        super().close()
        try:
            os.remove(self.filepath)
        except Exception as e:
            logger.debug(f"Error deleting file: {e}")

def serve_download(request):
    filepath = request.session.get('downloaded_filepath')
    if not filepath or not os.path.exists(filepath):
        raise Http404("File not found or download not ready.")
    filename = os.path.basename(filepath)
    response = DeletableFileResponse(open(filepath, 'rb'), filepath, as_attachment=True, filename=filename)
    # Clean up session data immediately (safe)
    request.session.pop('downloaded_filepath', None)
    request.session.pop('video_title', None)
    return response
