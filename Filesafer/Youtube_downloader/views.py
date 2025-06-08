from django.shortcuts import render, redirect, HttpResponse
from django.http import FileResponse, Http404
from .forms import YouTubeURLForm
from yt_dlp import YoutubeDL
import re, os, logging
import unicodedata
import ipcalc

logger = logging.getLogger('Youtube_downloader_log')
                           
def local(ip='0'): #bypass authentication if request is from local network
    localnetwork = ['10.0.0.0/8','172.16.0.0/12','192.168.0.0/16']
    if ip != '0':
        for subnet in localnetwork:
            if ip in ipcalc.Network(subnet):
                return True
    return False
def sanitize_filename(title, max_length=40):
    # Normalize and remove non-ASCII characters
    title = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode('ascii')
    # Remove non-word characters (keep alphanumeric, dash, underscore)
    title = re.sub(r'[^\w\-_. ]', '', title)
    # Replace spaces with underscores
    title = re.sub(r'\s+', '_', title)
    # Truncate if too long
    return title[:max_length].strip('_')

def download_youtube(request):
    if request.user.is_authenticated != True:
        if not local(request.META.get('REMOTE_ADDR')):
            return redirect ('/login/?next=/youtube_downloader')
    if request.method == 'POST':
        form = YouTubeURLForm(request.POST)
        if form.is_valid():
            input_url = form.cleaned_data["url"]
            action = request.POST.get('action')
            if action == 'video': #download MP4
                try:
                    with YoutubeDL({'quiet': True}) as ydl:
                        info_dict = ydl.extract_info(input_url, download=False)
                        raw_title = info_dict.get('title', 'Video')
                        safe_title = sanitize_filename(raw_title)
                    output_template = f'/tmp/{safe_title}.%(ext)s'
                    filepath = f"/tmp/{safe_title}.mp4"
                    
                    ydl_opts = {
                        'quiet': True, 
                        'format': 'bestvideo[height<=1080]+bestaudio/best', #download 1080p HD video
                        'merge_output_format': 'mp4',
                        'outtmpl': output_template,
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

def serve_download(request):
    filepath = request.session.get('downloaded_filepath')
    print (filepath)
    if not filepath or not os.path.exists(filepath):
        raise Http404("File not found or download not ready.")

    filename = os.path.basename(filepath)
    response = FileResponse(open(filepath, 'rb'), as_attachment=True, filename=filename)

    os.remove(filepath)
    del request.session['downloaded_filepath']
    del request.session['video_title']

    return response
