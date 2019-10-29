from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from .models import Session, Contact, Message
from .forms import Session_Form, Codice_Form, Chat_id_Form
from django.shortcuts import render, redirect
import os
from django.utils.dateparse import parse_datetime
from getpass import getpass
from telethon import TelegramClient, events
from telethon.network import ConnectionTcpAbridged
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import (
    UpdateShortChatMessage, UpdateShortMessage, PeerUser, PeerChat, PeerChannel, User, UpdateNewMessage, MessageMediaPhoto, MessageMediaDocument
)
from django.utils import timezone
from telethon.utils import get_display_name
from telethon.tl.functions.messages import GetHistoryRequest, GetUnreadMentionsRequest, GetMessagesRequest
from pathlib import Path
import traceback

import RPi.GPIO as GPIO
from time import sleep

dialogs = None
bottone = 0

#coda di stampa per updates
mess = []
scroll = 0
array = []
chatid = 0
photo=[]

robeh=""

#sx dall'alto x 22 27 17 23 x x 14
#dx dall'alto 20 21 12 16 6 19 13 26
#scroll 23 per contatti +-1 per su e giu
pin_bottoni={"20":1, "21":2, "12":3, "16":4, "6":5, "19":6, "13":7, "26":8, "14":23, "22":1, "27":-1}


def update_bottone_function(pin):
    global bottone
    print(str(pin))
    bottone=pin_bottoni[str(pin)]

def scroll_function(pin):
    global scroll
    print(str(pin))
    scroll=pin_bottoni[str(pin)]

GPIO.setmode(GPIO.BCM)
GPIO.setup(14,GPIO.IN)
GPIO.add_event_detect(14,GPIO.FALLING)
GPIO.add_event_callback(14, scroll_function)
GPIO.setup(15,GPIO.IN)
GPIO.add_event_detect(15,GPIO.FALLING)
GPIO.add_event_callback(15, update_bottone_function)
GPIO.setup(18,GPIO.IN)
GPIO.add_event_detect(18,GPIO.FALLING)
GPIO.add_event_callback(18, update_bottone_function)
GPIO.setup(23,GPIO.IN)
GPIO.add_event_detect(23,GPIO.FALLING)
GPIO.add_event_callback(23, update_bottone_function)
GPIO.setup(17,GPIO.IN)
GPIO.add_event_detect(17,GPIO.FALLING)
GPIO.add_event_callback(17, update_bottone_function)
GPIO.setup(27,GPIO.IN)
GPIO.add_event_detect(27,GPIO.FALLING)
GPIO.add_event_callback(27, scroll_function)
GPIO.setup(22,GPIO.IN)
GPIO.add_event_detect(22,GPIO.FALLING)
GPIO.add_event_callback(22, scroll_function)
GPIO.setup(6,GPIO.IN)
GPIO.add_event_detect(6,GPIO.FALLING)
GPIO.add_event_callback(6, update_bottone_function)
GPIO.setup(13,GPIO.IN)
GPIO.add_event_detect(13,GPIO.FALLING)
GPIO.add_event_callback(13, update_bottone_function)
GPIO.setup(19,GPIO.IN)
GPIO.add_event_detect(19,GPIO.FALLING)
GPIO.add_event_callback(19, update_bottone_function)
GPIO.setup(26,GPIO.IN)
GPIO.add_event_detect(26,GPIO.FALLING)
GPIO.add_event_callback(26, update_bottone_function)
GPIO.setup(12,GPIO.IN)
GPIO.add_event_detect(12,GPIO.FALLING)
GPIO.add_event_callback(12, update_bottone_function)
GPIO.setup(16,GPIO.IN)
GPIO.add_event_detect(16,GPIO.FALLING)
GPIO.add_event_callback(16, update_bottone_function)
GPIO.setup(20,GPIO.IN)
GPIO.add_event_detect(20,GPIO.FALLING)
GPIO.add_event_callback(20, update_bottone_function)
GPIO.setup(21,GPIO.IN)
GPIO.add_event_detect(21,GPIO.FALLING)
GPIO.add_event_callback(21, update_bottone_function)


# api_id = 177278, api_hash = '62e51931235b8de1ffabcb0657b6edf7'
# api_id = 185076, api_hash = 'ebf355bfe316cc22179d48ea13b4f727'
### MESSAGE UPDATE HANDLER
def message_handler(update):
    print("messagehandler richiamato")
    print(str(update))
    if isinstance(update, UpdateShortMessage):
            #m=Message(message_id=update.id, testo=update.message, date=update.date, from_id=update.user_id, to_id=update.user_id)
            #m.save()
            print("Shortmessage "+str(update))
            try:
                ore = ("%s:%s %s/%s/%s" % ( \
                    timezone.localtime(update.date).hour, \
                    timezone.localtime(update.date).minute, \
                    #get_message_info(message)['date'].second, \
                    timezone.localtime(update.date).day, \
                    timezone.localtime(update.date).month, \
                    timezone.localtime(update.date).year, \
                    ))
                if update.out:
                    mess.append({"y":"right", "media":None, "text":update.message, "date":ore, "chat_id": update.user_id})
                    print("messaggiunto: "+str(mess))
                else:
                    mess.append({"y":"left", "media":None, "text":update.message, "date":ore, "chat_id": update.user_id})
                    print("messaggiunto: "+str(mess))

            except Exception as e:
                print(str(e))
                traceback.print_exc()

    if isinstance(update, UpdateNewMessage):
            #m=Message(message_id=update.id, testo=update.message, date=update.date, from_id=update.user_id, to_id=update.user_id)
            #m.save()
            print("UpdateNewMessage"+str(update))
            try:
                ore = ("%s:%s %s/%s/%s" % ( \
                    timezone.localtime(update.message.date).hour, \
                    timezone.localtime(update.message.date).minute, \
                    timezone.localtime(update.message.date).day, \
                    timezone.localtime(update.message.date).month, \
                    timezone.localtime(update.message.date).year, \
                    ))
                #document_downloaded=download_media_by_message(update.message, update.message.id)
                document_downloaded="usermedia/no_user_image.png"
                print(type(document_downloaded))
                if update.message.out:
                    mess.append({"y":"right", "media":document_downloaded, "text":update.message.message, "date":ore, "chat_id": update.message.to_id.user_id})
                    print("messaggiunto: "+str(mess))
                else:
                    mess.append({"y":"left", "media":document_downloaded, "text":update.message.message, "date":ore, "chat_id": update.message.from_id})
                    print("messaggiunto: "+str(mess))

            except Exception as e:
                print(str(e))
                traceback.print_exc()

###CREATE Tel INSTANCE IF SESSION EXIST
if len(Session.objects.all()) == 1:
    Tel = TelegramClient(str(Session.objects.all()[0].session_id), 185076, 'ebf355bfe316cc22179d48ea13b4f727',connection=ConnectionTcpAbridged)
    print('Connecting to Telegram servers...')
    try:
        Tel.connect()
    except IOError:
        # We handle IOError and not ConnectionError because
        # PySocks' errors do not subclass ConnectionError
        # (so this will work with and without proxies).
        print('Initial connection failed. Retrying...')
        Tel.connect()
    Tel.add_event_handler(message_handler)
else:
    Tel=None

#!!! aggiungere Tel.connect()
def index(request):
    global Tel
    if Tel!=None:
        #Tel = TelegramClient(str(Session.objects.all()[0].session_id), 185076, 'ebf355bfe316cc22179d48ea13b4f727',connection_mode=ConnectionMode.TCP_ABRIDGED,update_workers=1)
        if Tel.is_user_authorized():
            return HttpResponseRedirect('contatti')
        else:
            form = Codice_Form(request.POST)
            if form.is_valid():
                #form with done
                #!!!controllare che il codice inserito sia giusto
                self_user =\
                        Tel.sign_in(code=form.cleaned_data['codice'])
                if Tel.is_user_authorized():
                    Tel.add_event_handler(message_handler)
                    return HttpResponseRedirect('contatti')
                else:
                    #!!! print "codice errato"
                    return render(request,'aTelegram/InserisciCodice.html', {"form": str(Session.objects.all()[0].phone_number)})
                return HttpResponseRedirect("/aTelegram/")
            else:
                Session.objects.all().delete()
                return HttpResponseRedirect("/aTelegram/")
            return HttpResponse('/aTelegram/')
    elif len(Session.objects.all()) == 0:
        form = Session_Form(request.POST)
        if form.is_valid():
            form.save(commit=True)
            Tel = TelegramClient(session = str(Session.objects.all()[0].session_id), \
                api_id = 185076, api_hash = 'ebf355bfe316cc22179d48ea13b4f727', \
                connection=ConnectionTcpAbridged)
            try:
                Tel.connect()
            except IOError:
                # We handle IOError and not ConnectionError because
                # PySocks' errors do not subclass ConnectionError
                # (so this will work with and without proxies).
                print('Initial connection failed. Retrying...')
                if not Tel.connect():
                    return HttpResponse('Connession failed')
            Tel.sign_in(form.save(commit=False).phone_number)
            return render(request,'aTelegram/InserisciCodice.html', {"form": form.save(commit=False).phone_number})
        else:
            return render(request,'aTelegram/InserisciNumero.html', {"form":form})
    else:
        return HttpResponse('Scegli quale numero dei tanti')

def contatti(request):
    global dialogs, bottone
    dialog_count = 30
    dialogs = Tel.get_dialogs(limit=dialog_count)
    photo=[]
    nome_contatto=[]
    id=[]
    numero=range(1, dialog_count+1)
    for contact in Contact.objects.all().order_by('num_bottone'):
        dialog=Tel.get_entity(contact.contact_id)
        if isinstance(dialog, User):
            if len(Contact.objects.filter(contact_id = dialog.id)) == 0:
                if isinstance(dialog.photo, type(None)):
                    st_photo=""
                else:
                    st_photo=str(dialog.photo.photo_big.local_id)
                c=Contact(contact_id=dialog.id, \
                    name=dialog.first_name, \
                    num=dialog.phone, \
                    session_id=Session.objects.all()[0], \
                    path=("usermedia/"+st_photo+".jpg"), \
                    num_bottone=0)
                print(">>>"+dialog.first_name)
            phone=dialog.phone
            nome_contatto.append(str(dialog.first_name))
            if isinstance(phone, type(None)):
                phone=""

            if dialog.photo is None:
                photo.append("usermedia/no_user_image.png")

            else:
                download_profile_picture(dialog)
                photo.append("usermedia/"+str(dialog.photo.photo_big.local_id)+".jpg")

            id.append(dialog.id)
    #return HttpResponse(str(id)+str(nome_contatto)+str(photo))
    array = list(zip(id, nome_contatto, photo))
    #if output["bottone"]!=0:
        #Contact.objects.filter(num_bottone = bottone)
    #return HttpResponse("Oh cazzo")
    if len(array)==0:
        return HttpResponse("associare contatti")
    rispos=">>>array: "+str((array))
    print(str(rispos))
    #return HttpResponse(rispos)
    return render(request, 'aTelegram/Contatti.html', {'array': list(array)})

def contattidebug(request):
    global dialogs, bottone, robeh
    dialog_count = 10
    dialogs = Tel.get_dialogs(limit=dialog_count)
    photos=[]
    nome_contatto=[]
    id=[]
    numero=range(1, dialog_count+1)
    for i, dialog in enumerate(dialogs):
        if isinstance(dialog.entity, User):
            phone=dialog.entity.phone
            nome_contatto.append(str(dialog.name))
            if isinstance(phone, type(None)):
                phone=""
            robeh=robeh+"<br><br><br>"+str(i)+" "+phone+"<br>"+str(dialog.name)+"<br>"+str(dialog)
            if dialog.entity.photo is None:
                robeh=robeh+"<br>no foto"
                photos.append("usermedia/no_user_image.png")
            else:
                robeh=robeh+"<br>retrieving photo"
                download_profile_picture(dialog.entity)
                photos.append("usermedia/"+str(dialog.entity.photo.photo_big.local_id)+".jpg")

            id.append(dialog.entity.id)
    array = zip(numero, id, nome_contatto, photos)
    #if output["bottone"]!=0:
        #Contact.objects.filter(num_bottone = bottone)
    return render(request, 'aTelegram/Chatdebug.html', {'dati': robeh})

def download_profile_picture (entity):
    # Download profile photo
    global robeh
    robeh=robeh+('<br>Downloading profile picture to usermedia/...')
    photo = Path("/home/pi/myTelegram/aTelegram/static/usermedia/"+str(entity.photo.photo_big.local_id)+".jpg")
    robeh=robeh+"<br>"+"photo: "+str(photo)
    if not photo.is_file():
        robeh=robeh+"<br>photo doesn't exist, trying to download"
        try:
            output = Tel.download_profile_photo(entity, ("/home/pi/myTelegram/aTelegram/static/usermedia/"+str(entity.photo.photo_big.local_id)+".jpg"))
        except TypeError:
            robeh=robeh+"<br>TypeError"
        return False
        if output:
            print('Profile picture downloaded to {}'.format(output))
            robeh=robeh+"<br>"+('Profile picture downloaded to {}'.format(output))
            return output
        else:
            print('No profile picture found for this user.')
            robeh=robeh+"<br>"+('No profile picture found for this user.')
            return False
    else:
        print ("File già scaricato")
        robeh=robeh+"<br>"+"File gia scaricato"

def chat(request, id):
    entity = Tel.get_entity(PeerUser(id))
    testi=[]
    ore=[]
    y=[]
    photos=[]
    for i, message in enumerate(Tel.get_messages(entity, 10)):
        #print(str(message))
        testi.append("%s" % ( \
            get_message_info(message)['message']))
        ore.append("%s:%s %s/%s/%s" % ( \
            get_message_info(message)['date'].hour, \
            get_message_info(message)['date'].minute, \
            get_message_info(message)['date'].day, \
            get_message_info(message)['date'].month, \
            get_message_info(message)['date'].year, \
            ))
        if get_message_info(message)["media"]:
            media_location=download_media_by_message(message, get_message_info(message)["media_id"])
            print(str(media_location))
            photos.append(str(media_location)[len("/home/pi/myTelegram/aTelegram/static/"):])
        else:
            photos.append(False)
        if message.out:
            y.append("right")
        else:
            y.append("left")
    messaggi=zip(testi, ore, y, photos)
    #!!!Tel.send_read_acknowledge(entity, message=None, max_id=None, clear_mentions=False)
    return render(request, 'aTelegram/Chat.html', {'dati_contatti': list(messaggi), 'user': id})

def chatdebug(request, id, idm=0):
    entity = Tel.get_entity(PeerUser(id))
    robeh=""
    for i, message in enumerate(Tel.get_messages(entity, 10)):
            robeh=robeh+("<br>"+str(i)+" "+str(message))
            robeh=robeh+("<br>%s:%s %s/%s/%s" % ( \
                get_message_info(message)['date'].hour, \
                get_message_info(message)['date'].minute, \
                get_message_info(message)['date'].day, \
                get_message_info(message)['date'].month, \
                get_message_info(message)['date'].year, \
                ))
            robeh=robeh+("<br>Has file? "+str(get_message_info(message)["media"]))
            if get_message_info(message)["media"]:
                robeh=robeh+"<br>calling download media"
                media_location=download_media_by_message(message, get_message_info(message)["media_id"])
                print(str(media_location))
                robeh=robeh+"<br>media location: "+str(media_location)
                robeh=robeh+"<br><img src=\""+str(media_location)+".jpg\" alt=\"Smiley face\" height=\"42\" width=\"42\">"
            else:
                robeh=robeh+("<br>not tried to download")
            robeh=robeh+"<br><br><br>"
    return render(request, 'aTelegram/Chatdebug.html', {'dati': str(robeh), 'user': id})

def setcontatti(request, num=None, id_contatto=None):
    global dialogs, bottone
    pagecontent=""
    if num=="delete":
        Contact.objects.all().delete()
        return HttpResponse("Contacts deleted")
    elif (num==None):
        dialog_count = 50
        dialogs = Tel.get_dialogs(limit=dialog_count)
        nome_contatto=[]
        id=[]
        pagecontent=pagecontent+"setcontatti/numbottone/id_contatto<br>setcontatti/delete<br><br>Contatti salvati<br>"
        for i, saved_contact in enumerate(Contact.objects.all()):
            pagecontent=pagecontent+"<br>"+str(i+1)+" "+str(saved_contact.name)
            pagecontent=pagecontent+"<br>Contact id "+str(saved_contact.contact_id)+"<br>contact phone_number "+str(saved_contact.num)
            pagecontent=pagecontent+"<br>Num bottone "+str(saved_contact.num_bottone)+"<br><br><br>"

        pagecontent=pagecontent+"<br><br>Elenco contatti"

        for i, dialog in enumerate(dialogs):
            if isinstance(dialog.entity, User):
                phone=dialog.entity.phone
                pagecontent=pagecontent+"<br><br>"+str(i+1)+" "+str(dialog.name)
                pagecontent=pagecontent+"<br>Contact id "+str(dialog.entity.id)+"<br>contact phone_number "+str(phone)
    elif num and id_contatto:
        if len(Contact.objects.filter(num_bottone = num))==1:
            Contact.objects.filter(num_bottone = num).delete()
            pagecontent=pagecontent+"Vecchio contatto cancellato<br>"
        else:
            pagecontent=pagecontent+"Non esiste ancora un contatto con questo numero<br>"
        dialogs = Tel.get_dialogs(limit=50)
        for i, dialog in enumerate(dialogs):
            if isinstance(dialog.entity, User) and dialog.entity.id==id_contatto:
                if isinstance(dialog.entity.photo, type(None)):
                    c=Contact( \
                        contact_id=dialog.entity.id, \
                        name=dialog.name, \
                        num=dialog.entity.phone, \
                        path="usermedia/no_user_image.jpg", \
                        session_id=Session.objects.all()[0], \
                        num_bottone=num
                        )
                else:
                    c=Contact( \
                        contact_id=dialog.entity.id, \
                        name=dialog.name, \
                        num=dialog.entity.phone, \
                        path="usermedia/"+str(dialog.entity.photo.photo_big.local_id)+".jpg", \
                        session_id=Session.objects.all()[0], \
                        num_bottone=num
                        )
                pagecontent=pagecontent+"<br>Saving:<br>"+str(c)
                c.save()
    else:
        return HttpResponse("Parametri sbagliati")
    #Contact.objects.filter(num_bottone = bottone)

    return HttpResponse(pagecontent)

def update(request):
    global bottone, scroll, mess, chatid, photo
    form = Chat_id_Form(request.GET)
    if form.is_valid():
        #!!!!controllare che il codice inserito sia giutttto
        chatid = int(form.cleaned_data['chatid'])
    else:
        chatid=1
    temp_mess = []
    temp_photo = []
    #print("mia "+str(chatid))
    print("mess "+str(mess))
    for m in mess:
        #print(m["chat_id"])
        if m["chat_id"]==chatid:
            temp_mess.append("\n<div class=\"alert alert-primary\" role=\"alert\" align=\""+m["y"]+"\"><font size=\"12\" color=\"black\">"+m["text"]+"</font><div><font size=\"3\" color=\"black\" style=\"font-family:Avenir\">"+m["date"]+"</font></div></div>")
            temp_photo.append(m["media"])
    mess = [x for x in mess if not x["chat_id"]==chatid]
    #!!!!!
    temp_bott=bottone
    new_url=""
    print(">>>>scroll: "+str(scroll))
    if bottone != 0:
        print(">>>>bottone: "+str(bottone))
        if len(Contact.objects.filter(num_bottone = bottone))==1:
            new_url = "/aTelegram/chat/"+str(Contact.objects.filter(num_bottone = bottone)[0].contact_id)
            print(">>>>m rul: "+str(new_url))
    sleep(0.1)
    bottone = 0
    temp_scroll = scroll
    scroll = 0
    return JsonResponse({"bottone": temp_bott, "new_url": new_url, "scroll": temp_scroll, "messaggi": temp_mess, "photo":temp_photo})

def download_media_by_message(message, msg_media_id):
        """Given a message, finds the media this message contained and
               downloads it.
        """
        robeh=""
        global Tel
        robeh=robeh+("<br>trying to find "+str(msg_media_id)+".jpg")
        photo = Path("/home/pi/myTelegram/aTelegram/static/usermedia/"+str(msg_media_id)+".jpg")
        if not photo.is_file():
            robeh=robeh+("<br>File not found: trying to download "+str(msg_media_id))
            output = Tel.download_media(
                get_message_info(message)['media_object'],
                file='/home/pi/myTelegram/aTelegram/static/usermedia/'+str(msg_media_id)+'.jpg',
            )
            robeh=robeh+('<br>Media downloaded to {}!'.format(output))
            return output
        else:
            robeh=robeh+"<br>file gia scaricato"
            print("file gia scaricato")
            return "/home/pi/myTelegram/aTelegram/static/usermedia/"+str(msg_media_id)+".jpg"

def get_message_info(message):
    if getattr(message, 'media', None)==None or (type(message.media)!=MessageMediaPhoto and type(message.media)!=MessageMediaDocument):
        return {'to_id': message.to_id.user_id, 'media':False, 'id':message.id, 'from_id':message.from_id, 'date':timezone.localtime(message.date), 'message':message.message}
    elif type(getattr(message, 'media', None))==MessageMediaPhoto:
        return {'to_id': message.to_id.user_id, 'media':True, 'media_id':message.media.photo.id, 'media_object':message.media, 'id':message.id, 'from_id':message.from_id, 'date':timezone.localtime(message.date), 'message':message.message}
    elif type(getattr(message, 'media', None))==MessageMediaDocument:
        return {'to_id': message.to_id.user_id, 'media':True, 'media_id':message.media.document.id, 'media_object':message.media, 'id':message.id, 'from_id':message.from_id, 'date':timezone.localtime(message.date), 'message':message.message}
    else:
        return None
