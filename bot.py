# -*- coding: utf-8 -*-
import redis
import os
import telebot
import math
import random
import threading
import info
import test
from telebot import types
from emoji import emojize
from pymongo import MongoClient
token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(token)

from requests.exceptions import ReadTimeout
from requests.exceptions import ConnectionError

games={}

client1=os.environ['database']
client=MongoClient(client1)
db=client.god
user=db.users
token=db.tokens
mob=db.mobs

def medit(message_text,chat_id, message_id,reply_markup=None,parse_mode='Markdown'):
    return bot.edit_message_text(chat_id=chat_id,message_id=message_id,text=message_text,reply_markup=reply_markup,
                                 parse_mode=parse_mode)


@bot.message_handler(commands=['info'])
def infom(m):
    x=user.find_one({'id':m.from_user.id})
    if x!=None:
        bot.send_message(m.chat.id, 'Статистика пользователя '+m.from_user.first_name+':\n'+
                     '*Статистика по цветам:*\n'+
                         'Синий: '+str(x['blue'])+' игр\n'+
                         'Красный: '+str(x['red'])+' игр\n'+
                         'Жёлтый: '+str(x['yellow'])+' игр\n\n'+
                         '*Статистика по персонажам:*\n'+
                         'Агент: '+str(x['agent'])+' игр\n'+
                         'Киллер: '+str(x['killer'])+' игр\n'+
                         'Главарь: '+str(x['glavar'])+' игр\n'+
                         'Прохожий: '+str(x['prohojii'])+' игр\n'+
                         'Приманка: '+str(x['primanka'])+' игр\n'+
                         'Миротворец: '+str(x['mirotvorets'])+' игр\n'+
                         'Гангстер: '+str(x['gangster'])+' игр\n'+
                         'Подрывник: '+str(x['podrivnik'])+' игр\n'+
                         'Красная приманка: '+str(x['redprimanka'])+' игр\n'+
                         'Телохранитель: '+str(x['telohranitel'])+' игр', parse_mode='markdown')

@bot.message_handler(commands=['stats'])
def stats(m):
    x=user.find_one({'id':m.from_user.id})
    if x!=None:
        try:
            vinrate=round((x['win']/x['games'])*100, 1)
        except:
            vinrate=0
        user.update_one({'id':m.from_user.id}, {'$set':{'name':m.from_user.first_name}})
        bot.send_message(m.chat.id, 'Статистика пользователя '+m.from_user.first_name+':\n'+
                     '*Игр сыграно:* '+str(x['games'])+'\n*Победы:* '+str(x['win'])+'\n*Поражения:* '+str(x['loose'])+
                     '\n*Винрейт:* '+str(vinrate)+'%', parse_mode='markdown')
    else:
        bot.send_message(m.chat.id, 'Сначала напишите боту /start!')
    
@bot.message_handler(commands=['update'])
def update(m):
    if m.from_user.id==441399484:
        user.update_many({},{'$set':{'detective':0}})
        bot.send_message(441399484, 'yes')
    
@bot.message_handler(commands=['start'])
def start(m):
    x=user.find_one({'id':m.from_user.id})
    if x==None:      
        user.insert_one({'id':m.from_user.id,
                         'name':m.from_user.first_name,
                         'win':0,
                         'loose':0,
                         'games':0,
                         'red':0,
                         'blue':0,
                         'yellow':0,
                         'agent':0,
                         'killer':0,
                         'glavar':0,
                         'prohojii':0,
                         'primanka':0,
                         'mirotvorets':0,
                         'gangster':0,
                         'podrivnik':0,
                         'redprimanka':0,
                         'telohranitel':0,
                         'detective':0,
                         'alive':0
                        })
    x=m.text.split('/start')
    if len(x)==2:
       try:
        if m.from_user.id==m.chat.id:
         if m.from_user.id not in games[int(x[1])]['players']:
          if len(games[int(x[1])]['players'])<10:
           if int(x[1])<0:
            i=0              
            if games[int(x[1])]['play']==0:
                games[int(x[1])]['players'].update(createuser(m.from_user.id, m.from_user.first_name))
                text=''           
                for ids in games[int(x[1])]['players']:
                    if games[int(x[1])]['players'][ids]['id']==m.from_user.id:
                        player=games[int(x[1])]['players'][ids]
                bot.send_message(m.from_user.id, 'Вы успешно присоединились!')
                b=0
                for g in games[int(x[1])]['players']:
                    text+=games[int(x[1])]['players'][g]['name']+'\n'
                    b+=1
                medit('Игроки: '+str(b)+'\n\n*'+text+'*', games[int(x[1])]['id'], games[int(x[1])]['users'])
                games[int(x[1])]['userlist']+=text+'\n'
                bot.send_message(games[int(x[1])]['id'], player['name']+' присоединился!')
          else:
            bot.send_message(m.from_user.id, 'Слишком много игроков! Мест не осталось!')
       except:
        if m.chat.id==m.from_user.id:
            bot.send_message(m.from_user.id, 'Игра crossfire')

            
@bot.message_handler(commands=['extend']) 
def extendd(m):
    if m.chat.id in games:
        if games[m.chat.id]['play']!=1:
            if m.from_user.id in games[m.chat.id]['players']:
                x=m.text.split('/extend')
                if len(x)==2:
                    try:
                        if int(x[1])>=1:
                            games[m.chat.id]['timebeforestart']+=int(x[1])
                            if games[m.chat.id]['timebeforestart']>=300:
                                games[m.chat.id]['timebeforestart']=300
                                bot.send_message(m.chat.id, 'Время до начала перестрелки увеличено! Осталось 5 минут.')
                            else:
                                bot.send_message(m.chat.id, 'Время до начала перестрелки увеличено на '+x[1]+'! Осталось '+str(games[m.chat.id]['timebeforestart'])+' секунд.')
                        else:
                            x=bot.get_chat_administrators(m.chat.id)
                            i=10
                            for z in x:       
                                if m.from_user.id==z.user.id:
                                    i=1
                                else:
                                    if i!=1:
                                        i=10
                            if i==1:
                                games[m.chat.id]['timebeforestart']+=int(x[1])
                                a=x[1]
                                if games[m.chat.id]['timebeforestart']<=0:
                                    pass
                                else:
                                    bot.send_message(m.chat.id,'Время до начала перестрелки увеличено на '+a+'! Осталось '+str(games[m.chat.id]['timebeforestart'])+' секунд.')
                            else:
                                bot.send_message(m.chat.id, 'Только администратор может использовать эту команду!')
                    except:
                        games[m.chat.id]['timebeforestart']+=30
                        if games[m.chat.id]['timebeforestart']>=300:
                            games[m.chat.id]['timebeforestart']=300
                        bot.send_message(m.chat.id, 'Время до начала перестрелки увеличено на 30! Осталось '+str(games[m.chat.id]['timebeforestart'])+' секунд.')
                else:
                    games[m.chat.id]['timebeforestart']+=30
                    if games[m.chat.id]['timebeforestart']>=300:
                            games[m.chat.id]['timebeforestart']=300
                    bot.send_message(m.chat.id, 'Время до начала перестрелки увеличено на 30! Осталось '+str(games[m.chat.id]['timebeforestart'])+' секунд.')
    
            
@bot.message_handler(commands=['flee'])
def flee(m):
    if m.chat.id in games:
     if games[m.chat.id]['play']!=1:
      if m.from_user.id in games[m.chat.id]['players']:
        del games[m.chat.id]['players'][m.from_user.id]
        text=''
        for g in games[m.chat.id]['players']:
            text+=games[m.chat.id]['players'][g]['name']+'\n'
        bot.send_message(m.chat.id, m.from_user.first_name+' сбежал!')
        medit('Игроки: \n\n*'+text+'*', m.chat.id, games[m.chat.id]['users'])
  

@bot.message_handler(commands=['help'])
def help(m):
    if m.chat.id<0:
        try:
            bot.send_message(m.chat.id, 'Отправил помощь тебе в личку')
        except:
            bot.send_message(m.chat.id, 'Начни диалог с ботом (@crossfirebot), чтобы я мог отправить тебе помощь!')
    try:
        bot.send_message(m.from_user.id, '*Правила игры "Crossfire*"\n'+
'"Crossfire" или "Перекрёстный огонь" - настольная игра, которая была перенесена в telegram. Суть её заключается в том, чтобы выполнить'+
                     'цель своей роли. Об этом позже.\nИгра основана на блефе и логике, почти как мафия. Но отличие заключается в том, '+
                     'что все участники начинают играть одновременно, и заканчивают тоже. Игра длится 5 минут, не дольше. \n\n'+
                     
                     '*Процесс игры*\nИгра начинается с того, что всем игрокам раздаются роли.\n\n'+
                     '*Роли*\n'+
                     



'*🔵Агент* - выигрывает, если выживает *Главарь*. Стреляет раньше *Убийцы*.\n'+

'*🔵Главарь* - выигрывает, если выживает. Не может стрелять.\n'+

'*🔴Убийца* - выигрывает, если *Главарь* погибает. Если был убит *агентом*, не стреляет.\n'

'*🌕Приманка* - выигрывает, если умирает. Не может стрелять.\n'+

'*🌕Прохожий* - выигрывает, если выживает. Если умер, проигрывает, а вместе с ним проигрывает и тот, кто его убил. Не может стрелять.\n'+

'*🔵Телохранитель* - выигрывает, если *Главарь* выживает. Вместо атаки защищает выбранную цель.\n'+

'*🌕Миротворец* - выигрывает, если ни один *прохожий* не был убит. Защищает выбранную цель.\n'+

'*🌕Подрывник* - выигрывает, если остается в живых. Если это происходит, все остальные проигрывают.\n'+

'*🔵Гангстер* - *агент*, но с двумя пулями.\n'+

'*🔴Красная приманка* - выигрывает, если умер *Главарь*; либо если его убил *Агент*.\n\n'+

'*По-настоящему выстрелившие*\n'+
'Не все роли в игре могут стрелять, но все роли могут выбрать цель. Строка "По-настоящему выстрелившие" показывает тех, кто выпустил пулю, а не просто выбрал цель.\n'+

'*Как убивать?*\n'+
'В конце обсуждения каждому в ЛС придет сообщение от бота с вариантом выбора цели. Но стрелять могут не все, поэтому выбрав цель, не факт, что вы кого-то убьете/защитите. Все роли, которые могут убивать/защищать или ничего не делать, описаны выше.\n\n'+
                     

'*Цвета*\n'+
'В игре есть 3 цвета:\n'+
'🔴🔵🌕\n'+
'*Красный*:\n'+
'Выигрывает, когда Главарь убит(не считая доп.Условий)\n'+
'*Синий*:\n'+
'Выигрывает, когда Главарь выживает(не считая доп.условий)\n'+
'*Желтый*:\n'+
'Выигрыш зависит только от доп.условий (все они описаны выше)', parse_mode='markdown')
    except:
        pass
@bot.message_handler(commands=['players'])
def playerss(m):
    if m.chat.id in games:
        bot.send_message(m.chat.id, 'Вот список игроков', reply_to_message_id=games[m.chat.id]['users'])

            
def secnd(id):
    games[id]['timebeforestart']-=1
    if games[id]['timebeforestart']<=0:
        begin(id)
    else:
        Keyboard=types.InlineKeyboardMarkup()
        Keyboard.add(types.InlineKeyboardButton(text='Присоединиться', url='telegram.me/crossfirebot?start='+str(id)))
        if games[id]['timebeforestart']==180:
            msg=bot.send_message(id, 'Осталось 3 минуты! Жмите "Присоединиться", чтобы поучаствовать в перестрелке!', reply_markup=Keyboard)
            games[id]['todel'].append(msg.message_id)
        elif games[id]['timebeforestart']==60:
            msg=bot.send_message(id, 'Осталось 60 секунд! Жмите "Присоединиться", чтобы поучаствовать в перестрелке!', reply_markup=Keyboard)
            games[id]['todel'].append(msg.message_id)
        elif games[id]['timebeforestart']==30:
            msg=bot.send_message(id, 'Осталось 30 секунд! Жмите "Присоединиться", чтобы поучаствовать в перестрелке!', reply_markup=Keyboard)
            games[id]['todel'].append(msg.message_id)
        elif games[id]['timebeforestart']==10:
            msg=bot.send_message(id, 'Осталось 10 секунд! Жмите "Присоединиться", чтобы поучаствовать в перестрелке!', reply_markup=Keyboard)
            games[id]['todel'].append(msg.message_id)
        t=threading.Timer(1, secnd, args=[id])
        t.start()
            
            
@bot.message_handler(commands=['startgame'])
def startgame(m):
  if m.chat.id<0:
    if m.chat.id not in games:
        games.update(creategame(m.chat.id))  
        tt=threading.Timer(1, secnd, args=[m.chat.id])
        tt.start()
        Keyboard=types.InlineKeyboardMarkup()
        Keyboard.add(types.InlineKeyboardButton(text='Присоединиться', url='telegram.me/crossfirebot?start='+str(m.chat.id)))
        msg=bot.send_message(m.chat.id, m.from_user.first_name+' Начал(а) игру! Жмите кнопку ниже, чтобы присоединиться', reply_markup=Keyboard)
        msg2=bot.send_message(m.chat.id, 'Игроки:\n', parse_mode='markdown')
        games[m.chat.id]['users']=msg2.message_id
        for ids in games:
            if games[ids]['id']==m.chat.id:
                game=games[ids]
        game['todel'].append(msg.message_id)
    else:
      if games[m.chat.id]['play']==0:
        Keyboard=types.InlineKeyboardMarkup()
        Keyboard.add(types.InlineKeyboardButton(text='Присоединиться', url='telegram.me/crossfirebot?start='+str(m.chat.id)))
        msg=bot.send_message(m.chat.id, 'Игра уже запущена! Жмите "присоединиться"!', reply_markup=Keyboard)
        for ids in games:
            if games[ids]['id']==m.chat.id:
                game=games[ids]
        game['todel'].append(msg.message_id)
  else:
    bot.send_message(m.chat.id, 'Играть можно только в группах!')
    
   
def begin(id):
  if id in games:
   if games[id]['play']==0:
    if len(games[id]['players'])>=4:
        for ids in games[id]['todel']:
            try:
                bot.delete_message(id, ids)
            except:
                pass
        i=1
        for ids in games[id]['players']:
            games[id]['players'][ids]['number']=i
            i+=1
        bot.send_message(id, 'Игра начинается!')
        games[id]['play']=1
        xod(games[id])
    else:
        for ids in games[id]['todel']:
            try:
                bot.delete_message(id, ids)
            except:
                pass
        bot.send_message(id, 'Недостаточно игроков!')
        try:
            del games[id]
        except:
            pass

        
@bot.message_handler(commands=['forcestart'])
def forcem(m):
  if m.chat.id in games:
    i=0
    x=bot.get_chat_administrators(m.chat.id)
    for z in x:       
        if m.from_user.id==z.user.id:
           i=1
        else:
            if i!=1:
                i=10
    if i==1 or m.from_user.id==441399484:
        if m.chat.id in games:
            games[m.chat.id]['timebeforestart']=1
    else:
        bot.send_message(m.chat.id, 'Только администратор может использовать эту команду!')
        
        

def xod(game):
    gangster=0
    prohojii=0
    primanka=0
    mirotvorets=0
    podrivnik=0
    telohranitel=0
    detective=0
    agent=0
    killer=0
    list2=[]
    if len(game['players'])==2:
        roless=['glavar','killer']
    elif len(game['players'])==3:
        roless=['gangster','killer', 'glavar']
    elif len(game['players'])==4:
        prohojii=75
        primanka=75
        killer=100
        roless=['agent','killer', 'glavar', 'primanka']       
    elif len(game['players'])==5:
        agent=20
        killer=20
        prohojii=50
        primanka=50
        detective=50
        roless=['agent','killer', 'glavar']
    elif len(game['players'])==6:
        mirotvorets=40
        killer=75
        podrivnik=15
        primanka=30
        telohranitel=60
        detective=50
        roless=['agent','killer', 'glavar', 'prohojii']
    elif len(game['players'])==7:
        agent=50
        killer=75
        primanka=50
        telohranitel=50
        prohojii=50
        mirotvorets=50
        podrivnik=25
        detective=50
        roless=['agent','killer', 'glavar']
    elif len(game['players'])>=8:
        gangster=35
        prohojii=65
        primanka=50
        mirotvorets=25
        podrivnik=35
        telohranitel=40
        agent=25
        killer=25
        detective=50
        roless=['glavar','killer', 'killer','agent']
    #elif len(game['players'])==9:
    #    roless=['glavar', 'prohojii', 'podrivnik','agent','killer', 'killer', 'agent','killer', 'agent'] #'loialistblue','povstanetsred'
    #elif len(game['players'])==10:
    #    roless=['glavar', 'prohojii', 'mirotvorets','agent','killer', 'killer', 'agent','killer', 'agent', 'podrivnik'] 
        
    while len(roless)<len(game['players']):
        toadd=[]
        if random.randint(1,100)<=agent:
            toadd.append('agent')
        if random.randint(1,100)<=killer:
            toadd.append('killer')
        if random.randint(1,100)<=gangster:
            toadd.append('gangster')
        if random.randint(1,100)<=prohojii:
            toadd.append('prohojii')
        if random.randint(1,100)<=primanka:
            toadd.append('primanka')
        if random.randint(1,100)<=mirotvorets:
            toadd.append('mirotvorets')
        if random.randint(1,100)<=podrivnik:
            toadd.append('podrivnik')
        if random.randint(1,100)<=telohranitel:
            toadd.append('telohranitel')
        if random.randint(1,100)<=detective:
            toadd.append('detective')
        if len(toadd)>0:
            x=random.choice(toadd)
            roless.append(x)
            
        
        
    pick=[]
    for g in game['players']:
        x=random.randint(0, len(game['players'])-1)
        while x in pick:
            x=random.randint(0, len(game['players'])-1)
        game['players'][g]['role']=roless[x]
        pick.append(x)
    roletext=[]
    players=[]
    roletext1=[]
    numbers=[]
    roletextfinal=''
    while len(roletext1)<len(roletext):
        i=random.randint(0, len(roletext)-1)
        if i not in numbers:
            roletext1.append(roletext[i])
            numbers.append(i)
    for bb in roletext1:
        roletextfinal+=bb+'\n'     
    text=''
    for g in game['players']:
        players.append(game['players'][g]['name'])
    for gg in players:
        text+=gg+'\n'
    try:
      #bot.send_message(game['id'], 'Роли: \n*'+roletextfinal+'*', parse_mode='markdown')
      bot.send_message(game['id'], 'Игроки: \n'+'*'+text+'*', parse_mode='markdown')
    except:
        pass
    for gg in game['players']:
        #bot.send_message(game['players'][gg]['id'], 'Роли: \n*'+roletextfinal+'*', parse_mode='markdown')
        bot.send_message(game['players'][gg]['id'], 'Игроки: \n'+'*'+text+'*', parse_mode='markdown')
    t=threading.Timer(1, shuffle1, args=[game])
    t.start()
            
 
def shuffle1(game):
    roles=[]
    for ids in game['players']:
        roles.append(game['players'][ids]['role'])
    i=0
    for ids in game['players']:
        try:
            game['players'][ids]['role']=roles[i+1]
            i+=1
        except:
            game['players'][ids]['role']=roles[0]
    #bot.send_message(game['id'], 'Ваши роли были переданы человеку над вами! Теперь посмотрите свои новые роли.')
    #for g in game['players']:
    #    if game['players'][g]['role']=='agent':
    #        text='Ты агент'
    #    elif game['players'][g]['role']=='killer':
    #        text='Ты киллер'
    #    elif game['players'][g]['role']=='prohojii':
    #        text='Ты прохожий'
    #    elif game['players'][g]['role']=='primanka':
    #        text='Ты приманка'
    #    elif game['players'][g]['role']=='glavar':
    #        text='Ты главарь'
    #    elif game['players'][g]['role']=='telohranitel':
    #        text='Ты телохранитель'
    #    elif game['players'][g]['role']=='podrivnik':
    #        text='Ты подрывник'
    #    elif game['players'][g]['role']=='mirotvorets':
    #        text='Ты миротворец'
    #    elif game['players'][g]['role']=='gangster':
    #        text='Ты гангстер'
    #    elif game['players'][g]['role']=='redprimanka':
    #        text='Ты красная приманка'
    #    try:
    #      bot.send_message(game['players'][g]['id'], text)
    #    except:
    #        pass
    t=threading.Timer(1, shuffle2, args=[game])
    t.start()
        
    
 
def roletotext(x):
        if x=='agent':
            text='Ты агент! Твоя цель - убить всех киллеров!'
        elif x=='killer':
            text='Ты киллер! Твоя цель - убить главаря!'
        elif x=='prohojii':
            text='Ты прохожий! Твоя цель - выжить! У тебя нет оружия.'
        elif x=='primanka':
            text='Ты приманка! Твоя цель - быть убитым(ой)! У тебя нет оружия.'
        elif x=='glavar':
            text='Ты главарь! Твоя цель - выжить! У тебя нет оружия.'
        elif x=='telohranitel':
            text='Ты телохранитель! Твоя цель - защитить главаря!'
        elif x=='podrivnik':
            text='Ты подрывник! Твоя цель - выжить! Если это произойдет, все остальные проиграют! У тебя нет оружия.'
        elif x=='mirotvorets':
            text='Ты миротворец! Твоя цель - спасти прохожих!'
        elif x=='gangster':
            text='Ты гангстер! Твоя цель - убить всех киллеров! У тебя 2 патрона.'
        elif x=='redprimanka':
            text='Ты красная приманка! Твоя цель - быть убитым одним из "синих"! У тебя нет оружия.'
        elif x=='detective':
            text='Ты детектив! Раз за раунд ты можешь проверить роль любого игрока в игре. Играешь за синих. У тебя нет оружия.'
        return text

def shuffle2(game):
    roles=[]
    for ids in game['players']:
        roles.append(game['players'][ids]['role'])
    first=random.randint(1, len(game['players']))
    shuffles=len(game['players'])/3
    if shuffles<1:
        shuffles=1
    i=0
    centers=[]
    while i<shuffles:
        for ids in game['players']:
            if game['players'][ids]['number']==first:
                mid=game['players'][ids]
                centers.append(mid['name'])
            if first+1<=len(game['players']):
                if game['players'][ids]['number']==first+1:
                    bottom=game['players'][ids]
            else:
                if game['players'][ids]['number']==1:
                    bottom=game['players'][ids]
            if first-1>=1:                
                if game['players'][ids]['number']==first-1:
                    top=game['players'][ids]
            else:
                if game['players'][ids]['number']==len(game['players']):
                    top=game['players'][ids]            
        users=[]
        roles=[]
        users.append(mid)
        users.append(bottom)
        users.append(top)
        roles.append(bottom['role'])
        roles.append(mid['role'])
        roles.append(top['role'])
        pick=[]
        for g in users:
            x=random.randint(0, 2)
            while x in pick:
                x=random.randint(0, 2)
            g['role']=roles[x]
            pick.append(x)
            #bot.send_message(g['id'], roletotext(roles[x]))
        if first==len(game['players']):
            first=3
        elif first==len(game['players'])-1:
            first=2
        elif first==len(game['players'])-2:
            first=1
        else:
            first+=3
        i+=1
    text2=''
    #for ids in centers:
    #    text2+=ids+'\n'
    #bot.send_message(game['id'], 'Ваши роли были перемешаны по 3 штуки! Центры перемешивания: *\n'+text2+'*', parse_mode='markdown')
    #for g in game['players']:
    #    try:
    #      bot.send_message(game['players'][g]['id'], 'Ваши роли были перемешаны по 3 штуки! Центры перемешивания: *\n'+text2+'*', parse_mode='markdown')
    #    except:
    #        pass
    for g in game['players']:
        if game['players'][g]['role']=='agent':
            game['players'][g]['cankill']=1
            game['players'][g]['blue']=1
        elif game['players'][g]['role']=='killer':
            game['players'][g]['cankill']=1
            game['players'][g]['red']=1
        elif game['players'][g]['role']=='prohojii':
            game['players'][g]['cankill']=0
            game['players'][g]['yellow']=1
        elif game['players'][g]['role']=='primanka':
            game['players'][g]['cankill']=0
            game['players'][g]['yellow']=1
        elif game['players'][g]['role']=='glavar':
            game['players'][g]['cankill']=0
            game['players'][g]['blue']=1
        elif game['players'][g]['role']=='telohranitel':
            game['players'][g]['candef']=1
            game['players'][g]['blue']=1
        elif game['players'][g]['role']=='podrivnik':
            game['players'][g]['cankill']=0
            game['players'][g]['yellow']=1
        elif game['players'][g]['role']=='mirotvorets':
            game['players'][g]['candef']=1
            game['players'][g]['yellow']=1
        elif game['players'][g]['role']=='gangster':
            game['players'][g]['blue']=1
            game['players'][g]['cankill']=1
        elif game['players'][g]['role']=='redprimanka':
            game['players'][g]['red']=1
        elif game['players'][g]['role']=='detective':
            game['players'][g]['cankill']=0
            game['players'][g]['blue']=1
        bot.send_message(game['players'][g]['id'], roletotext(game['players'][g]['role']))
    for ids in game['players']:
        player=game['players'][ids]
        kb=types.InlineKeyboardMarkup()
        x=0
        if player['cankill']==1 or player['role']=='primanka':
            kb.add(types.InlineKeyboardButton(text='Показать оружие', callback_data='showgun'))
            x=1
        if player['role']=='glavar' or player['role']=='prohojii' or player['role']=='primanka':
            kb.add(types.InlineKeyboardButton(text='Сказать всем, что у вас нет оружия.', callback_data='showpocket'))
            x=1
        if player['role']=='detective':
            x=1
            for idss in game['players']:
                if game['players'][idss]['id']!=player['id']:
                    kb.add(types.InlineKeyboardButton(text='Проверить роль '+game['players'][idss]['name'], callback_data='check '+str(game['players'][idss]['id'])))
        if x==1:
            bot.send_message(player['id'], 'Жать кнопку или нет - решать вам.', reply_markup=kb)
       
    bot.send_message(game['id'], 'У вас 120 секунд на обсуждение!')
    t=threading.Timer(120, shoot, args=[game])
    t.start()
      



def shoot(game):
    for g in game['players']:
        Keyboard=types.InlineKeyboardMarkup()
        for ids in game['players']:
            if game['players'][ids]['id']!=game['players'][g]['id']:
                Keyboard.add(types.InlineKeyboardButton(text=game['players'][ids]['name'], callback_data=str(game['players'][ids]['number'])))
        try:
          if game['players'][g]['candef']!=1:
              msg=bot.send_message(game['players'][g]['id'], 'Кого ты хочешь пристрелить? У тебя 60 секунд для выбора.', reply_markup=Keyboard)
          else:
              msg=bot.send_message(game['players'][g]['id'], 'Кого ты хочешь защитить? У тебя 60 секунд для выбора.', reply_markup=Keyboard)
          game['players'][g]['message']={'msg':msg,
                                       'edit':1
                                      }
        except:
            pass
                                       
    bot.send_message(game['id'], 'Теперь выбирайте, на кого хотите направить пистолеты!')
    t=threading.Timer(60, endshoot, args=[game])
    t.start()
        

        
@bot.callback_query_handler(func=lambda call:True)
def inline(call):
    x=0
    for ids in games:
        if call.from_user.id in games[ids]['players']: 
            game=games[ids]
            x=1
            player=games[ids]['players'][call.from_user.id]
    if x==1:
        if 'check' not in call.data:
            if call.data!='showgun' and call.data!='showpocket': 
                for z in game['players']:
                    if game['players'][z]['number']==int(call.data):
                        target=game['players'][z]
                if game['players'][call.from_user.id]['role']!='gangster':
                    game['players'][call.from_user.id]['text']='*'+game['players'][call.from_user.id]['name']+'*'+'🔫стреляет в '+target['name']+'\n'
                    medit('Выбор сделан: '+target['name'],call.from_user.id,call.message.message_id)
                    game['players'][call.from_user.id]['message']['edit']=0
                    game['players'][call.from_user.id]['target']=target
                else:
                  if game['players'][call.from_user.id]['picks']>0:
                    if game['players'][call.from_user.id]['picks']==2:
                        game['players'][call.from_user.id]['text']+='*'+game['players'][call.from_user.id]['name']+'*'+'🔫стреляет в '+target['name']+'\n'
                    else:
                        game['players'][call.from_user.id]['text']+='*'+game['players'][call.from_user.id]['name']+'*'+'🔫стреляет в '+target['name']+'\n'
                    medit('Выбор сделан: '+target['name'],call.from_user.id,call.message.message_id)
                    game['players'][call.from_user.id]['message']['edit']=0
                    if game['players'][call.from_user.id]['target']==None:
                        game['players'][call.from_user.id]['target']=target
                    else:
                        game['players'][call.from_user.id]['target2']=target
                    game['players'][call.from_user.id]['picks']-=1
                    for g in game['players']:
                        Keyboard=types.InlineKeyboardMarkup()
                        for ids in game['players']:
                          if game['players'][g]['target']!=None:
                            if game['players'][ids]['id']!=game['players'][g]['id'] and game['players'][ids]['id']!=game['players'][g]['target']['id']:
                                Keyboard.add(types.InlineKeyboardButton(text=game['players'][ids]['name'], callback_data=str(game['players'][ids]['number'])))
                    msg=bot.send_message(call.from_user.id, 'Теперь выберите вторую цель', reply_markup=Keyboard)
                    game['players'][call.from_user.id]['message']={'msg':msg,
                                           'edit':1
                                          }
                  else:
                    medit('Выбор сделан: '+target['name'],call.from_user.id,call.message.message_id)
                
            else:
                if call.data=='showgun':
                    if player['cankill']==1 or player['role']=='primanka':
                        bot.send_message(game['id'], '🔫|'+player['name']+' достал из кармана пистолет и показал всем!')
                        medit('Выбор сделан.', call.message.chat.id, call.message.message_id)
                if call.data=='showpocket':
                    if player['role']=='glavar' or player['role']=='prohojii' or player['role']=='primanka':
                        bot.send_message(game['id'], '👐|'+player['name']+' вывернул карманы и показал, что он безоружный!')
                        medit('Выбор сделан.', call.message.chat.id, call.message.message_id)
        else:
            if player['role']=='detective':
                if player['checked']==0:
                    i=int(call.data.split(' ')[1])
                    for ids in game['players']:
                        target=game['players'][ids]
                        if target['id']==i:
                            if player['checked']==0:
                                player['checked']=1
                                medit('Выбрано: чек роли.', call.message.chat.id, call.message.message_id)
                                bot.send_message(player['id'], 'Роль игрока '+target['name']+': '+rolename(target['role'])+'!')
                            else:
                                medit('Вы уже проверяли кого-то!', call.message.chat.id, call.message.message_id)
            else:
                medit('Вы не детектив!', call.message.chat.id, call.message.message_id)

def endshoot(game):
    text=''
    for msg in game['players']:
        if game['players'][msg]['message']['edit']==1:
            medit('Время вышло!', game['players'][msg]['message']['msg'].chat.id, game['players'][msg]['message']['msg'].message_id)
    for ids in game['players']:
        if game['players'][ids]['text']!='':
            text+=game['players'][ids]['text']+'\n'
        else:
            text+='*'+game['players'][ids]['name']+'*'+'💨не стреляет\n'
    bot.send_message(game['id'], text, parse_mode='markdown')
    t=threading.Timer(8, reallyshoot, args=[game])
    t.start()
        

def reallyshoot(game):
    for ids in game['players']:
        game['players'][ids]['text']=''
        if game['players'][ids]['candef']==1:
            if game['players'][ids]['target']!=None:
                game['players'][ids]['target']['defence']+=1
                game['players'][ids]['text']+='*'+game['players'][ids]['name']+'*'+' Защищает '+game['players'][ids]['target']['name']+'!'
                
    for ids in game['players']:
        if game['players'][ids]['blue']==1:
            if game['players'][ids]['target']!=None:
                if game['players'][ids]['cankill']==1:
                    if game['players'][ids]['target']['defence']<1:
                        game['players'][ids]['target']['killed']=1
                        game['players'][ids]['target']['killedby'].append(game['players'][ids]['role'])
                        game['players'][ids]['target']['golos']=0
                        game['players'][ids]['killany']=game['players'][ids]['target']          
                    else:
                        game['players'][ids]['target']['defence']-=1
                        game['players'][ids]['killany']=None
                    game['players'][ids]['text']+='*'+game['players'][ids]['name']+'*'+'🔫стреляет в '+game['players'][ids]['target']['name']
            if game['players'][ids]['target2']!=None:
                if game['players'][ids]['cankill']==1:
                    if game['players'][ids]['target2']['defence']<1:
                        game['players'][ids]['target2']['killed']=1
                        game['players'][ids]['target']['killedby'].append(game['players'][ids]['role'])
                        game['players'][ids]['target2']['golos']=0
                        game['players'][ids]['killany2']=game['players'][ids]['target2']          
                    else:
                        game['players'][ids]['target2']['defence']-=1
                        game['players'][ids]['killany2']=None
                    game['players'][ids]['text']+='*'+game['players'][ids]['name']+'*'+'🔫стреляет в '+game['players'][ids]['target2']['name']+'!'
                
    for ids in game['players']:
        if game['players'][ids]['target']!=None:
          if game['players'][ids]['red']==1:
            if game['players'][ids]['cankill']==1:
              if game['players'][ids]['golos']==1:
                if game['players'][ids]['target']['defence']<1:
                    game['players'][ids]['target']['killed']=1
                    game['players'][ids]['target']['killedby'].append(game['players'][ids]['role'])
                    game['players'][ids]['killany']=game['players'][ids]['target']          
                else:
                    game['players'][ids]['target']['defence']-=1
                    game['players'][ids]['killany']=None
                game['players'][ids]['text']+='*'+game['players'][ids]['name']+'*'+'🔫стреляет в '+game['players'][ids]['target']['name']+'!'
              else:
                game['players'][ids]['text']+='*'+game['players'][ids]['name']+'*'+'☠️Убит! (не стреляет)'
                
    text=''
    for ids in game['players']:
        text+=game['players'][ids]['text']+'\n'
    bot.send_message(game['id'],'По-настоящему выстрелившие:\n'+text, parse_mode='markdown')
    text=''
    role=game['players'][ids]['role']
    live=emojize(':neutral_face:', use_aliases=True)
    dead=emojize(':skull:', use_aliases=True)
    blue=emojize(':large_blue_circle:', use_aliases=True)
    red=emojize(':red_circle:', use_aliases=True)
    yellow=emojize(':full_moon:', use_aliases=True)
    pobeda=emojize(':thumbsup:', use_aliases=True)
    porajenie=emojize(':-1:', use_aliases=True)
    podrivnik=0
    for podriv in game['players']:
        if game['players'][podriv]['role']=='podrivnik':
            if game['players'][podriv]['killed']==0:
                podrivnik=1
    for ids in game['players']:
        if game['players'][ids]['blue']==1:
            color=blue
        elif game['players'][ids]['red']==1:
            color=red
        else:
            color=yellow
        if game['players'][ids]['role']=='agent':
            role='Агент'
        elif game['players'][ids]['role']=='killer':
            role='Киллер'
        elif game['players'][ids]['role']=='prohojii':
            role='Прохожий'
        elif game['players'][ids]['role']=='primanka':
            role='Приманка'
        elif game['players'][ids]['role']=='glavar':
            role='Главарь'
        elif game['players'][ids]['role']=='telohranitel':
            role='Телохранитель'
        elif game['players'][ids]['role']=='mirotvorets':
            role='Миротворец'
        elif game['players'][ids]['role']=='gangster':
            role='Гангстер'
        elif game['players'][ids]['role']=='podrivnik':
            role='Подрывник'
        elif game['players'][ids]['role']=='redprimanka':
            role='Красная приманка'
        elif game['players'][ids]['role']=='detective':
            role='Детектив'
        if game['players'][ids]['killed']==1:
            alive=dead+'Мёртв'
        else:
            alive=live+'Жив'
        for idss in game['players']:
            if game['players'][idss]['role']=='glavar':
                glavar=game['players'][idss]
        if game['players'][ids]['blue']==1:
            if glavar['killed']==0:
              if podrivnik!=1:
                win=pobeda+'Выиграл\n'
              else:
                win=porajenie+'Проиграл\n'
            else:
                win=porajenie+'Проиграл\n'
            if game['players'][ids]['killany']!=None:
                if game['players'][ids]['killany']['role']=='prohojii':
                    win=porajenie+'Проиграл (убил прохожего)\n'
                if game['players'][ids]['killany2']!=None:
                    if game['players'][ids]['killany2']['role']=='prohojii':
                        win=porajenie+'Проиграл (убил прохожего)\n'           
        elif game['players'][ids]['red']==1:
          if game['players'][ids]['role']!='redprimanka':
            if glavar['killed']==1:
              if podrivnik!=1:
                win=pobeda+'Выиграл\n'
              else:
                win=porajenie+'Проиграл\n'
            else:
                win=porajenie+'Проиграл\n'
            if game['players'][ids]['killany']!=None:
                if game['players'][ids]['killany']['role']=='prohojii':
                        win=porajenie+'Проиграл (убил прохожего)\n'
                
          else:            
            if glavar['killed']==1 or game['players'][ids]['killed']==1:
              if podrivnik!=1:
                win=pobeda+'Выиграл\n'
              else:
                win=porajenie+'Проиграл\n'
            else:
                win=porajenie+'Проиграл\n'
            if 'gangster' or 'agent' in game['players'][ids]['killedby']:
                if podrivnik!=1:
                    win=pobeda+'Выиграл\n'
                else:
                    win=porajenie+'Проиграл\n'
        elif game['players'][ids]['yellow']==1:
            if game['players'][ids]['role']=='prohojii':
                if game['players'][ids]['killed']==1:
                    win=porajenie+'Проиграл\n'
                else:
                  if podrivnik!=1:
                    win=pobeda+'Выиграл\n'
                  else:
                    win=porajenie+'Проиграл\n'
            if game['players'][ids]['role']=='primanka':
                    if game['players'][ids]['killed']==1:
                      if podrivnik!=1:
                        win=pobeda+'Выиграл\n'
                      else:
                        win=porajenie+'Проиграл\n'
                    else:
                        win=porajenie+'Проиграл\n'
            if game['players'][ids]['role']=='mirotvorets':
                    i=0
                    for prohojii in game['players']:
                        if game['players'][prohojii]['role']=='prohojii' and game['players'][prohojii]['killed']==1:
                            i=1
                    if i==1:
                        win=porajenie+'Проиграл\n'
                    else:
                      if podrivnik!=1:
                        win=pobeda+'Выиграл\n'
                      else:
                        win=porajenie+'Проиграл\n'
            if game['players'][ids]['role']=='podrivnik':
                if game['players'][ids]['killed']==0:
                    win=pobeda+'Выиграл\n'
                else:
                    win=porajenie+'Проиграл\n'
        text+=game['players'][ids]['name']+': '+color+role+','+alive+','+win
        if color==red:
            user.update_one({'id':game['players'][ids]['id']}, {'$inc':{'red':1}})
        elif color==blue:
            user.update_one({'id':game['players'][ids]['id']}, {'$inc':{'blue':1}})
        elif color==yellow:
            user.update_one({'id':game['players'][ids]['id']}, {'$inc':{'yellow':1}})
        if role=='Агент':
            user.update_one({'id':game['players'][ids]['id']}, {'$inc':{'agent':1}})
        elif role=='Киллер':
            user.update_one({'id':game['players'][ids]['id']}, {'$inc':{'killer':1}})
        elif role=='Прохожий':
            user.update_one({'id':game['players'][ids]['id']}, {'$inc':{'prohojii':1}})
        elif role=='Приманка':
            user.update_one({'id':game['players'][ids]['id']}, {'$inc':{'primanka':1}})
        elif role=='Главарь':
            user.update_one({'id':game['players'][ids]['id']}, {'$inc':{'glavar':1}})
        elif role=='Телохранитель':
            user.update_one({'id':game['players'][ids]['id']}, {'$inc':{'telohranitel':1}})
        elif role=='Миротворец':
            user.update_one({'id':game['players'][ids]['id']}, {'$inc':{'mirotvorets':1}})
        elif role=='Гангстер':
            user.update_one({'id':game['players'][ids]['id']}, {'$inc':{'gangster':1}})
        elif role=='Подрывник':
            user.update_one({'id':game['players'][ids]['id']}, {'$inc':{'podrivnik':1}})
        elif role=='Красная приманка':
            user.update_one({'id':game['players'][ids]['id']}, {'$inc':{'redprimanka':1}})
        elif role=='Детектив':
            user.update_one({'id':game['players'][ids]['id']}, {'$inc':{'detective':1}})
        if alive==live+'Жив':
            user.update_one({'id':game['players'][ids]['id']}, {'$inc':{'alive':1}})
        if win==pobeda+'Выиграл\n':
            user.update_one({'id':game['players'][ids]['id']}, {'$inc':{'win':1}})
        elif win==porajenie+'Проиграл\n' or win==porajenie+'Проиграл (убил приманку)\n' or win==porajenie+'Проиграл (убил прохожего)\n':
            user.update_one({'id':game['players'][ids]['id']}, {'$inc':{'loose':1}})
        user.update_one({'id':game['players'][ids]['id']}, {'$inc':{'games':1}})
            
    bot.send_message(game['id'], 'Результаты игры:\n'+text)
    del games[game['id']]
        
     
def rolename(role):
    x='Неизвестная роль, обратитесь к @Loshadkin.'
    if role=='agent':
        x='Агент'
    elif role=='killer':
        x='Киллер'
    elif role=='prohojii':
        x='Прохожий'
    elif role=='primanka':
        x='Приманка'
    elif role=='glavar':
        x='Главарь'
    elif role=='telohranitel':
        x='Телохранитель'
    elif role=='mirotvorets':
        x='Миротворец'
    elif role=='gangster':
        x='Гангстер'
    elif role=='podrivnik':
        x='Подрывник'
    elif role=='redprimanka':
        x='Красная приманка'
    elif role=='detective':
        x='Детектив'
    return x
    
def creategame(id):
    return {id:{
        'players':{},
        'id':id,
        'todel':[],
        'toedit':[],
        'play':0,
        'timebeforestart':180,
        'users':None,
        'userlist':'Игроки:\n\n'
    }
           }
        

def createuser(id, name):
    return{id:{
        'role':None,
        'name':name,
        'id':id,
        'number':None,
        'text':'',
        'shuffle':0,
        'target':None,
        'target2':None,
        'killed':0,
        'cankill':0,
        'defence':0,
        'killany':None,
        'killany2':None,
        'candef':0,
        'blue':0,
        'red':0,
        'yellow':0,
        'win':0,
        'golos':1,
        'message':0,
        'picks':2,
        'killedby':[],
        'checked':0
    }
          }
    
 

bot.polling(none_stop=True)



