from django.shortcuts import render, redirect
from .models import FileDB
from .forms import FileDBForm
import ipcalc

def local(request):
    localnetwork = ['172.27.1.0/24','10.1.1.0/24','10.1.2.0/24']
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR") # get original IP if running Nginx as reverse proxy
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()  
    else:
        ip = request.META.get("REMOTE_ADDR") # get IP if running Django as web server
    for subnet in localnetwork:
        if ip in ipcalc.Network(subnet):
            return True
    return False

def file_list (request, pk=0):
    # Local network will not need user authentication
    if request.user.is_authenticated != True:
        if not local(request):
            return redirect ('/login/?next=/storage/list/')
    if pk !=0:
        file_target = FileDB.objects.get (pk=pk)
        return render(request, 'file_list.html', {'file_target':file_target,'user_auth': True})
    if FileDB.objects.all().count() == 0:
        return render(request, 'file_list.html',{'new':True,'user_auth': True})
    return render(request, 'file_list.html',{'files':FileDB.objects.all(),'user_auth': True})

def file_upload(request):
    # Local network will not need user authentication
    if request.user.is_authenticated != True:
        if not local(request):
            return redirect ('/login/?next=/storage/upload/')
    if request.method == 'POST':
        form = FileDBForm(request.POST, request.FILES)
        if form.is_valid():
            filecache = form.save()
            setattr(filecache, 'file_name', filecache.file_object.name.split('/')[1] )
            filecache.save()
            return redirect ('/storage/list',{'user_auth': True})
    else:
        form = FileDBForm()
        return render(request, 'file_upload.html',{'form': form,'user_auth': True})
    
def file_delete (request, pk):
    # Local network will not need user authentication
    if request.user.is_authenticated != True:
        if not local(request):
            return redirect ('/login/?next=/storage/list/')
    if request.method == 'POST':
        try:
            file_object = FileDB.objects.get(pk=pk)
            file_object.delete()
        except Exception as e:
            print (e)
        return redirect ('/storage/list/',{'user_auth': True})