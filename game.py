import pygame
import random
import sys
import json
import math

# 居中函数
def mid(size,surf):
    xmid = (size[0]/2)-(surf.get_rect().width/2)
    return xmid

# 加载配置文件
def loads(jsonpath):
    j = open(jsonpath)
    config = json.loads(j.read())
    j.closed
    return config

# 保存配置文件
def save(config,file):
    saving = json.dumps(config)
    f = open(file,'w')
    f.write(saving)
    f.closed

# 载入配置
config = loads("config.json")
fps = config["fps"]
size_name = {"qHD":(960,540),"HD":(1280,720),"FHD":(1920,1080)}
size = size_name[config["screen_size"]]
vol = config["vol"]*0.01
speed = config["speed"]
font_size = {'qHD':0.75,'HD':1,'FHD':1.5}

# 初始化游戏
pygame.init()
pygame.key.stop_text_input()
clock = pygame.time.Clock()
pixel_font = pygame.font.Font('./font/DePixelBreitFett.ttf',int(56*(font_size[config["screen_size"]])))
pixel_font_mid = pygame.font.Font('./font/DePixelKlein.ttf',int(50*(font_size[config["screen_size"]])))
pixel_font_small = pygame.font.Font('./font/DePixelKlein.ttf',int(20*(font_size[config["screen_size"]])))
cn_font = pygame.font.Font('./font/SourceHanSerifSC-Bold.otf',int(40*(font_size[config["screen_size"]])))
cn_font_heavy = pygame.font.Font('./font/SourceHanSerifSC-Bold.otf',int(56*(font_size[config["screen_size"]])))
cn_font_small = pygame.font.Font('./font/SourceHanSerifSC-Bold.otf',int(32*(font_size[config["screen_size"]])))
#pygame.display.set_icon(pygame.image.load('./icon/favicon.ico'))

# 创建窗口
bg_pic = './source/background.jpg'
window = pygame.display.set_mode(size)
pygame.display.set_caption('Space Fighting')
bg = pygame.image.load("./source/background.jpg").convert()
bg = pygame.transform.scale(bg,size)


# 定义游戏中出现的对象

# 飞船类型
class Ship(pygame.sprite.Sprite):
    def __init__(self,img,position,hp):
        super().__init__()
        self.position = position
        self.image = pygame.image.load(img).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.left,self.rect.top = self.position
        self.hp = hp
    
    def moveto(self,position):
        self.rect.left,self.rect.top = position

    def move(self,speed):
        self.rect = self.rect.move(speed)
        self.position = self.rect.left,self.rect.top

    def mid(self):
        self.rect.left = mid(size,self.image)
        self.position = self.rect.left,self.rect.top
    
    def rotate(self,theta):
        self.image = pygame.transform.rotate(self.image,theta)
        self.rect = self.image.get_rect()
        self.rect.left,self.rect.top = self.position

    def scale(self,size):
        self.image = pygame.transform.scale(self.image,size)
        self.rect = self.image.get_rect()
        self.rect.left,self.rect.top = self.position

    def get_hurt(self,dmg):
        self.hp -= dmg

    def outside(self):
        l_byd = self.rect.left < 0
        r_byd = self.rect.left + self.rect.width > size[0]+ 0
        t_byd = self.rect.top + self.rect.height < -1
        b_byd = self.rect.top > size[1] + 1
        return (l_byd or r_byd) or (t_byd or b_byd)
    
    def get_outside(self):
        self.rect.left,self.rect.top = (-200,-2000)

    def change_img(self,new_img):
        self.image = pygame.image.load(new_img).convert_alpha()
        self.rect.left,self.rect.top = self.position
    

# 陨石类
class Mete(pygame.sprite.Sprite):
    def __init__(self,img,position,inf):
        super().__init__()
        self.image = pygame.image.load(img).convert_alpha()
        self.rect = self.image.get_rect()
        self.position = position
        self.lt_float,self.top_float = self.rect.left,self.rect.top
        self.speed = (0,0)
        self.inf = inf
        self.init_p = (img,position,inf)
    
    def set_speed(self,speed):
        self.speed = speed
    
    def update(self):
        self.lt_float += self.speed[0] 
        self.top_float += self.speed[1]
        self.rect.left,self.rect.top = self.lt_float,self.top_float
        #print('top',self.rect.top,'speed',self.speed[1],'he',self.rect.top+self.speed[1],self.inf)
        self.position = (self.position[0]+self.speed[0],self.position[1]+self.speed[1])
        

    def move(self,position):
        self.rect.left,self.rect.top = position
        self.lt_float,self.top_float = self.rect.left,self.rect.top
        self.position = position

    def scale(self,size):
        self.image = pygame.transform.scale(self.image,size)
        self.rect = self.image.get_rect()
        self.rect.left,self.rect.top = self.position

    def set_inf(self,inf):
        self.inf = inf

    def rotate(self,theta):
        self.image = pygame.transform.rotate(self.image,theta)
        self.rect = self.image.get_rect()
        self.lt_float,self.top_float = self.rect.left,self.rect.top
        self.speed = (0,0)

    def draw(self):
        window.blit(self.image,self.position)

    def outside(self):
        l_byd = self.rect.left + self.rect.width < 0
        r_byd = self.rect.left > size[0]+ 0
        t_byd = self.rect.top + self.rect.height < -1
        b_byd = self.rect.top > size[1] + 1
        return (l_byd or r_byd) or (t_byd or b_byd)
    
    def init(self):
        self.__init__(self.init_p[0],self.init_p[1],self.init_p[2])


class Sheld(Mete):
    def __init__(self, img, position, inf):
        super().__init__(img, position, inf)
        self.img = img

    def convert(self):
        self.image = pygame.image.load(self.img).convert()
        self.image.set_colorkey((255,255,255))
        self.image.set_alpha(128)

class bullet_pool():
    def __init__(self,n,img) -> None:
        self.pool = []
        self.img = img
        for i in range(n):
            self.pool.append(Mete(img,(0,0),0))
    
    def get(self):
        if len(self.pool) == 0:
            return Mete(self.img,(0,0),0)
        else:
            return self.pool.pop()
    
    def return_bullet(self,bullet):
        self.pool.append(bullet)

if __name__ == '__main__':
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        
        # 载入背景音乐
        pygame.display.update()
        pygame.mixer.music.load('./music/David Bowie - Starman.mp3')
        pygame.mixer.music.set_volume(vol)
        pygame.mixer.music.play()

        # 设置开始菜单初始状态
        option_choose = 'start'
        click = False

        # 定义状态间的转移函数
        def up(option):
            return {'start':'quit','quit':'config','config':'start'}[option]
        
        def down(option):
            return {'quit':'start','config':'quit','start':'config'}[option]
        
        while True:
            # 设置菜单的帧率
            clock.tick(30)

            # 绘制背景
            window.blit(bg,(0,0))

            # 绘制标题
            title_1 = pixel_font.render("SPACE",False,(255,255,255))
            window.blit(title_1,(mid(size,title_1),size[1]*0.22))
            title_2 = pixel_font.render("FIGHTING",False,(255,255,255))
            window.blit(title_2,(mid(size,title_2),size[1]*0.22+title_1.get_rect().height))

            # 绘制选项
            start = cn_font.render('开始游戏',True,(255,255,255))
            opt_config = cn_font.render('游戏设置',True,(255,255,255))
            quit_game = cn_font.render('退出游戏',True,(255,255,255))
            start_y = size[1]*0.5
            for option in [start,opt_config,quit_game]:
                window.blit(option,(mid(size,option),start_y))
                start_y += size[1]*0.1
            start_y = size[1]*0.5

            # 绘制被选中的选项
            if option_choose == 'start':
                pygame.draw.rect(window,(255,255,255),[mid(size,start)-size[0]*0.025,start_y,start.get_rect().width+size[0]*0.05,start.get_rect().height])
                anti_start = cn_font.render('开始游戏',True,(0,0,0))
                window.blit(anti_start,(mid(size,start),start_y))
                pygame.display.update()

            elif option_choose == 'config':
                pygame.draw.rect(window,(255,255,255),[mid(size,start)-size[0]*0.025,start_y+size[1]*0.1,start.get_rect().width+size[0]*0.05,start.get_rect().height])
                anti_config = cn_font.render('游戏设置',True,(0,0,0))
                window.blit(anti_config,(mid(size,start),start_y+size[1]*0.1)) 
                pygame.display.update()       
            
            elif option_choose == 'quit':
                pygame.draw.rect(window,(255,255,255),[mid(size,start)-size[0]*0.025,start_y+size[1]*0.2,start.get_rect().width+size[0]*0.05,start.get_rect().height])
                anti_quit = cn_font.render('退出游戏',True,(0,0,0))
                window.blit(anti_quit,(mid(size,start),start_y+size[1]*0.2)) 
                pygame.display.update() 
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    # 向下切换
                    if event.key == pygame.K_UP:
                        option_choose = up(option_choose)
                    # 向上切换
                    elif event.key == pygame.K_DOWN:
                        option_choose = down(option_choose)
                    # 选定
                    if event.key == pygame.K_SPACE:
                        if option_choose == 'quit':
                            sys.exit()
                        click = True
            # 退出开始菜单页面
            if click:
                break
        
        if click and option_choose == 'config':
            # 初始化设置界面中的数据
            cfg_not_changed = (vol,size,fps,speed)
            cfg_changed = False
            cfg_option = 'vol'
            cfg_down = {'vol':'size','size':'fps','fps':'speed','speed':'vol'}
            cfg_up = {'vol':'speed','speed':'fps','fps':'size','size':'vol'}
            size_lt = {size_name['HD']:size_name['qHD'],size_name['qHD']:size_name['FHD'],size_name['FHD']:size_name['HD']}
            size_rt = {size_name['HD']:size_name['FHD'],size_name['FHD']:size_name['qHD'],size_name['qHD']:size_name['HD']}
            size_changed = size
            saved = False
            esc = False

            while True:
                # 判断是否重新绘制
                switch = False

                # 设置帧率
                clock.tick(30)

                # 绘制背景
                window.blit(bg,(0,0))
                
                # 绘制标题
                title_config = cn_font_heavy.render('游戏设置',True,(255,255,255))
                window.blit(title_config,(mid(size,title_config),size[1]*0.05))

                # 绘制底部提升
                cfg_help = cn_font_small.render('按ESC直接返回菜单，按H保持更改的设置',True,(255,255,255))
                window.blit(cfg_help,(mid(size,cfg_help),size[1]*0.75))

                # 绘制选项
                volume = cn_font.render('游戏音量 ：◀         '+ '{:^3.0f}'.format(vol*100) + '          ▶',True,(255,255,255))
                scr_size = cn_font.render('屏幕尺寸 ：◀  ' + '{:>4.0f}'.format(size_changed[0]) + '×' + '{:<4.0f}'.format(size[1]) + ' ▶',True,(255,255,255))
                cfg_fps = cn_font.render('游戏帧率 ：◀         ' + '{:^3.0f}'.format(fps) + '          ▶',True,(255,255,255))
                cfg_speed = cn_font.render('移动速度 ：◀         ' + '{:^3.0f}'.format(speed) + '          ▶',True,(255,255,255))
                cfg_start_y = size[1]*0.3
                for cfg in [volume,scr_size,cfg_fps,cfg_speed]:
                    window.blit(cfg,(mid(size,cfg),cfg_start_y))
                    cfg_start_y += size[1]*0.1
                pygame.display.update

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        # 向下切换
                        if event.key == pygame.K_DOWN:
                            cfg_option = cfg_down[cfg_option]
                        # 向上切换
                        elif event.key == pygame.K_UP:
                            cfg_option = cfg_up[cfg_option]

                
                while cfg_option == 'vol' and not switch:
                    pygame.mixer.music.set_volume(vol)
                    clock.tick(60)
                    pygame.key.set_repeat(200,20)
                    if vol<0:
                        anti_vol = anti_vol = cn_font.render('游戏音量 ：◀         '+ '  0 ' + '          ▶',True,(0,0,0))
                    else:
                        anti_vol = cn_font.render('游戏音量 ：◀         '+ '{:^3.0f}'.format(vol*100) + '          ▶',True,(0,0,0))
                    pygame.draw.rect(window,(255,255,255),[mid(size,volume)-size[0]*0.025,size[1]*0.3,volume.get_rect().width+size[1]*0.06,volume.get_rect().height])
                    window.blit(anti_vol,(mid(size,volume),size[1]*0.3))
                    pygame.display.update()
                    
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            sys.exit()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_RIGHT:
                                if vol < 1:
                                    vol += 0.01
                                    cfg_changed = True
                            if event.key == pygame.K_LEFT:
                                if vol > 0.0:
                                    vol -= 0.01 
                                    cfg_changed = True
                            if event.key == pygame.K_UP:
                                cfg_option = cfg_up['vol']
                                pygame.key.set_repeat()
                                switch = True
                            if event.key == pygame.K_DOWN:
                                cfg_option = cfg_down['vol']
                                pygame.key.set_repeat()
                                switch = True
                            if event.key == pygame.K_h:
                                saved = True
                                switch = True
                            if event.key == pygame.K_ESCAPE:
                                switch = True
                                esc = True
                            
                while cfg_option == 'size' and not switch:
                    clock.tick(30)
                    anti_size = cn_font.render('屏幕尺寸 ：◀  ' + '{:>4.0f}'.format(size_changed[0]) + '×' + '{:<4.0f}'.format(size_changed[1]) + ' ▶',True,(0,0,0))
                    pygame.draw.rect(window,(255,255,255),[mid(size,scr_size)-size[0]*0.025,size[1]*0.4,volume.get_rect().width+size[1]*0.06,volume.get_rect().height])
                    window.blit(anti_size,(mid(size,scr_size),size[1]*0.4))
                    pygame.display.update()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            sys.exit()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_LEFT:
                                size_changed = size_lt[size_changed]
                                cfg_changed = True
                            elif event.key == pygame.K_RIGHT:
                                size_changed = size_rt[size_changed]
                                cfg_changed = True
                            elif event.key == pygame.K_DOWN:
                                cfg_option = cfg_down['size']
                                switch = True
                            elif event.key == pygame.K_UP:
                                cfg_option = cfg_up['size']
                                switch = True
                            if event.key == pygame.K_h:
                                saved = True
                                switch = True
                            if event.key == pygame.K_ESCAPE:
                                switch = True
                                esc = True

                while cfg_option == 'fps' and not switch:
                    clock.tick(30)
                    anti_fps = cn_font.render('游戏帧率 ：◀         ' + '{:^3.0f}'.format(fps) + '          ▶',True,(0,0,0))
                    pygame.draw.rect(window,(255,255,255),[mid(size,scr_size)-size[0]*0.025,size[1]*0.5,volume.get_rect().width+size[1]*0.06,cfg_fps.get_rect().height])
                    window.blit(anti_fps,(mid(size,anti_fps),size[1]*0.5))
                    pygame.display.update()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            sys.exit()
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_LEFT:
                                fps = {90:60,60:120,120:90}[fps]
                                cfg_changed = True
                            elif event.key == pygame.K_RIGHT:
                                fps = {90:120,120:60,60:90}[fps]
                                cfg_changed = True
                            elif event.key == pygame.K_DOWN:
                                cfg_option = cfg_down['fps']
                                switch = True
                            elif event.key == pygame.K_UP:
                                cfg_option = cfg_up['fps']
                                switch = True
                            if event.key == pygame.K_h:
                                saved = True
                                switch = True
                            if event.key == pygame.K_ESCAPE:
                                switch = True
                                esc = True

                while cfg_option == 'speed' and not switch:
                    clock.tick(60)
                    anti_spd = cn_font.render('移动速度 ：◀         ' + '{:^3.0f}'.format(speed) + '          ▶',True,(0,0,0))
                    pygame.draw.rect(window,(255,255,255),[mid(size,cfg_speed)-size[0]*0.025,size[1]*0.6,volume.get_rect().width+size[1]*0.06,cfg_fps.get_rect().height])
                    window.blit(anti_spd,(mid(size,anti_spd),size[1]*0.6))
                    pygame.display.update()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            sys.exit()
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_RIGHT:
                                if speed < 69:
                                    speed += 5
                                    cfg_changed = True
                            if event.key == pygame.K_LEFT:
                                if speed > 50:
                                    speed -= 5
                                    cfg_changed = True
                            if event.key == pygame.K_DOWN:
                                cfg_option = cfg_down['speed']
                                switch = True
                            if event.key == pygame.K_UP:
                                cfg_option = cfg_up['speed']
                                switch = True
                            if event.key == pygame.K_h:
                                saved = True
                                switch = True
                            if event.key == pygame.K_ESCAPE:
                                switch = True
                                esc = True
                
                if saved:
                    # 保存已更改的配置
                    save({'vol':int('{:^3.0f}'.format(vol*100)),'screen_size':{(960,540):'qHD',(1280,720):'HD',(1920,1080):'FHD'}[size_changed],'fps':fps,'speed':speed},'config.json')
                    
                    # 重新载入配置
                    config = loads("config.json")
                    fps = config["fps"]
                    size = size_name[config["screen_size"]]
                    vol = config["vol"]*0.01 
                    speed = config["speed"]

                    window = pygame.display.set_mode(size)
                    bg = pygame.image.load("./source/background.jpg").convert()
                    bg = pygame.transform.scale(bg,size)

                    pixel_font = pygame.font.Font('./font/DePixelBreitFett.ttf',int(56*(font_size[config["screen_size"]])))
                    pixel_font_mid = pygame.font.Font('./font/DePixelKlein.ttf',int(50*(font_size[config["screen_size"]])))
                    pixel_font_small = pygame.font.Font('./font/DePixelKlein.ttf',int(20*(font_size[config["screen_size"]])))
                    cn_font = pygame.font.Font('./font/SourceHanSerifSC-Bold.otf',int(40*(font_size[config["screen_size"]])))
                    cn_font_heavy = pygame.font.Font('./font/SourceHanSerifSC-Bold.otf',int(56*(font_size[config["screen_size"]])))
                    cn_font_small = pygame.font.Font('./font/SourceHanSerifSC-Bold.otf',int(32*(font_size[config["screen_size"]])))

                    break

                elif esc:
                    vol = cfg_not_changed[0]
                    fps = cfg_not_changed[2]
                    speed = cfg_not_changed[3]
                    break
        
        # 开始游戏
        elif click and option_choose == 'start':
            while True:
                # 载入记录
                record = loads('data.json')['record']
                record_float = loads('data.json')['record_float']
                # 实例化主角机
                boost = Ship('./source/boost.png',(100,-100*(size[1]/720)),0)
                boost.scale((38*(size[1]/720),11*(size[1]/720)))
                # print(boost.rect)
                player = Ship('./source/player.png',(100,-100*(size[1]/720)),100)
                player.scale((33*(size[1]/540),61*(size[1]/540)))
                player.mid()
                spd = speed*10*(size[1]/720)/fps
                boost.move((0,player.rect.height))
                boost.mid()
                playerfire = False
                player_bullet_group = pygame.sprite.Group()
                # 设定动画速度
                y_v_anime = size[1]/(2*fps)
                # 设置声音
                pygame.time.delay(100)
                pygame.mixer.music.fadeout(1000)
                # 初始化声音
                score = 0
                score_count = 0
                # 初始化敌机状态
                enemy_bullet_1 = pygame.sprite.Group()
                enemy_bullet_2 = pygame.sprite.Group()
                enemy_bullet_3 = pygame.sprite.Group()
                mod = 0
                upgrade = False
                enemyfire = False
                # 初始化陨石组
                mete = pygame.sprite.Group()
                # 动画判断
                anime = False
                # 生成子弹池
                player_bullet_pool = bullet_pool(10,'./source/playerbullet.png')
                enemy_bullet_pool = bullet_pool(50,'./source/EnemyBullet.png')
               # bullet_check_lst_1 = multiprocessing.Queue()
                #bullet_check_lst_2 = multiprocessing.Queue()
               # bullet_check_lst_3 = multiprocessing.Queue()

                # 判断血量
                def live(sprite):
                    if sprite.hp < 0.1:
                        return False
                    else:
                        return True
                
                hitting = False
                # 载入动画
                while True:
                    clock.tick(fps)

                    # 绘制背景
                    window.blit(bg,(0,0))

                    # 绘制主角机
                    window.blit(player.image,player.rect)
                    window.blit(boost.image,boost.rect)
                    player.move((0,y_v_anime))
                    boost.move((0,y_v_anime))

                    pygame.display.update()

                    # 结束动画
                    if player.rect.top + player.rect.height + boost.rect.height >= size[1]:
                        break
                    
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            sys.exit()

                # 加载音乐
                pygame.mixer.music.load('./music/Lyn - Life Will Change.mp3')
                pygame.mixer.music.set_volume(vol)
                pygame.mixer.music.play()
                # 初始按键
                w_down = 0
                a_down = 0
                s_down = 0
                d_down = 0

                mete_inf = set()
                # 计算速度
                def e_speed_count(p1,p2,spd):
                    vec = pygame.math.Vector2((p1[0]-p2[0],p1[1]-p2[1]))
                    vec = -spd*vec.normalize()
                    return (vec.x,vec.y)
                
                # 实例化道具
                sheld = Mete('./source/Armor_Bonus.png',(0,0),0)
                medkit = Mete('./source/HP_Bonus.png',(0,0),1)
                player_sheld_on = False
                sheld_obj = Sheld('./source/sheld.png',(0,0),None)
                sheld_obj.convert()
                sheld_obj.scale((player.rect.h*1.2,player.rect.h*1.2))

                # 自定义事件    
                PROP = pygame.USEREVENT + 1
                SHELDOFF = pygame.USEREVENT + 2
                CHANGE_DIRECTION = pygame.USEREVENT +3
                ANTICHANGE = pygame.USEREVENT + 4
                ENEMYFIRE = pygame.USEREVENT + 5
                PLAYERFIRE = pygame.USEREVENT + 6
                PLAYERNORMAL = pygame.USEREVENT + 7
                ENEMYNORMAL = pygame.USEREVENT + 8

                # time_start = time.daylight
                
                # 设置触发道具的计时器
                pygame.time.set_timer(PROP,15000,1)
                prop_refresh = False
                bullet_count = 0
                # 主角極開火的計時器
                pygame.time.set_timer(PLAYERFIRE,1000,1)
                
                change_direction = True
                dead = False
                frame_num = 0
            # while True:
                while live(player):
                    clock.tick(fps)

                    # 绘制背景
                    window.blit(bg,(0,0))

                    # 绘制主角机
                    if player_sheld_on:
                        sheld_obj.move((player.rect.left+player.rect.w/2-sheld_obj.rect.w/2,player.rect.top+player.rect.h/2-sheld_obj.rect.h/2))
                        window.blit(sheld_obj.image,sheld_obj.rect)
                    window.blit(player.image,player.rect)
                    window.blit(boost.image,boost.rect)

                    # 绘制右上角信息
                    #score_text = pixel_font_small.render('score: '+str(score),False,(255,255,255))
                # hp_text = pixel_font_small.render('HP: '+str(int(player.hp)),False,(255,255,255))
                # window.blit(score_text,(0,0))
                #  window.blit(hp_text,(0,score_text.get_rect().height))

                    score_count += 10/fps
                    score = math.floor(score_count)

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            sys.exit()
                        # 检测wasd四个按键的状态
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_w:
                                w_down = 1
                            if event.key == pygame.K_a:
                                a_down = 1
                            if event.key == pygame.K_s:
                                s_down = 1
                            if event.key == pygame.K_d:
                                d_down = 1
                        elif event.type == pygame.KEYUP:
                            if event.key == pygame.K_w:
                                w_down = 0
                            if event.key == pygame.K_a:
                                a_down = 0
                            if event.key == pygame.K_s:
                                s_down = 0
                            if event.key == pygame.K_d:
                                d_down = 0
                        # 监测是否刷新道具
                        elif event.type == PROP:
                            #print(1,end = ' ')
                            prop_time_reset = True
                            prop_refresh = True
                            prop = {0:sheld,1:medkit}[random.randint(0,1)]
                            prop.scale((300*size[1]*0.75/(720*3),0.75*300*size[1]/(720*3)))
                            prop_side = random.randint(0,1)
                            prop_start_y = random.randint(int(round(size[1]*0.2)),int(round(size[1]))-prop.rect.height)
                            prop_end_y = random.randint(int(round(size[1]*0.2)),int(round(size[1]))-prop.rect.height)
                            prop_spd = (120/fps)*random.randint(24,30)*3.75*0.5*0.1*0.8
                            #print(sheld.rect)
                            # 从左侧刷新
                            if prop_side == 0:
                                prop.move((-prop.rect.width,prop_start_y))
                                prop_spd_v = e_speed_count((-prop.rect.width,prop_start_y),(size[0]+prop.rect.width,prop_end_y),prop_spd)
                                prop.set_speed(prop_spd_v)
                            else:
                                prop.move((size[0],prop_start_y))
                                prop_spd_v = e_speed_count((size[0],prop_start_y),(-prop.rect.width,prop_end_y),prop_spd)
                                prop.set_speed(prop_spd_v)
                        # 检测护盾效果是否消失
                        elif event.type == SHELDOFF:
                            #print('OFF')
                            player_sheld_on = False
                        # 检查方向
                        elif event.type == CHANGE_DIRECTION:
                            change_direction = True
                        # 检测刷新敌机
                        elif event.type == ANTICHANGE:
                            #print('UPGRADE')
                            mod = 0
                        # 检测是否开火（敌机）
                        elif event.type == ENEMYFIRE:
                            enemyfire = True
                        # 检测是否开火（主角机）
                        elif event.type == PLAYERFIRE:
                            playerfire = True
                        # 检测主角机图像状态
                        elif event.type == PLAYERNORMAL:
                            player.change_img('./source/player.png')
                            player.scale((33*(size[1]/540),61*(size[1]/540)))
                        # 检测敌机图像状态
                        elif event.type == ENEMYNORMAL:
                            if mod == 2:
                                enemy.change_img('./source/anti_'+{0:'1',1:'1',2:'2'}[mod]+'.png')
                                enemy.scale(enemysize)
                            else:
                                hitting = False
                    
                    wasd = (w_down,a_down,s_down,d_down)

                    # 不同按键对应速度
                    if wasd == (0,0,0,0) or wasd == (0,1,0,1) or wasd == (1,0,1,0) or wasd == (1,1,1,1):
                        player_speed = (0,0)
                    elif wasd == (1,0,0,0) or wasd == (1,1,0,1):
                        player_speed = (0,-spd)
                    elif wasd == (0,0,1,0) or wasd == (0,1,1,1):
                        player_speed = (0,spd)
                    elif wasd == (0,1,0,0) or wasd == (1,1,1,0):                
                        player_speed = (-spd,0)
                    elif wasd == (0,0,0,1) or wasd == (1,0,1,1):
                        player_speed = (spd,0)
                    elif wasd == (1,1,0,0):
                        player_speed = (-1.414*0.5*spd,-0.5*1.414*spd)
                    elif wasd == (1,0,0,1):
                        player_speed = (1.414*0.5*spd,-0.5*1.414*spd)
                    elif wasd == (0,1,1,0):
                        player_speed = (-1.414*0.5*spd,1.414*0.5*spd)
                    elif wasd == (0,0,1,1):
                        player_speed = (1.414*0.5*spd,0.5*1.414*spd)
                    
                    # 设置飞行器运动
                    if player.rect.left <= 0:
                        x_v_side = 0 if player_speed[0] < 0 else player_speed[0]
                        player_speed = (x_v_side,player_speed[1])
                    elif  player.rect.left + player.rect.width >= size[0]:
                        x_v_side = 0 if not player_speed[0] < 0 else player_speed[0]
                        player_speed = (x_v_side,player_speed[1])
                    if player.rect.top + player.rect.height + boost.rect.height >= size[1]:
                        y_v_side = 0 if player_speed[1] > 0 else player_speed[1]
                        player_speed = (player_speed[0],y_v_side)
                    elif player.rect.top < size[1]*0.2:
                        y_v_side = 0 if player_speed[1] < 0 else player_speed[1]
                        player_speed = (player_speed[0],y_v_side)
                    player.move(player_speed)
                    boost.move(player_speed)

                    # 生成陨石
                    if len(mete) < 4:
                        mete_img = {1:'./source/Meteor_01.png',2:'./source/Meteor_02.png',3:'./source/Meteor_03.png',4:'./source/Meteor_04.png'}
                        for i in range(len(mete),4):
                            
                            mete_num = random.randint(1,4)
                            
                            mete_obj = Mete(mete_img[mete_num],(-200,-200),0)

                            mete_obj.scale((mete_obj.rect.width*size[1]/(3*720),mete_obj.rect.height*size[1]/(720*3)))

                            # 左上
                            if 0 not in mete_inf:
                                mete_begin_y = random.randint(int(round(size[1]*0.1)),int(round(size[1]*0.5)))
                                mete_end_y = random.randint(int(round(size[1]*0.5)),int(round(size[1]*1.2)))
                                mete_begin_position = (-mete_obj.rect.width,mete_begin_y)
                                mete_end_position = (size[0]+mete_obj.rect.width,mete_end_y)
                                mete_inf.add(0)
                                mete_obj.set_inf(0)
                            
                            # 左下
                            elif 1 not in mete_inf:
                                mete_end_y = random.randint(int(round(size[1]*0.1)),int(round(size[1]*0.5)))
                                mete_begin_y = random.randint(int(round(size[1]*0.5)),int(round(size[1]*1.2)))
                                mete_begin_position = (-mete_obj.rect.width,mete_begin_y)
                                mete_end_position = (size[0]+mete_obj.rect.width,mete_end_y)
                                mete_inf.add(1)
                                mete_obj.set_inf(1)
                            
                            # 右上
                            elif 2 not in mete_inf:
                                mete_begin_y = random.randint(int(round(size[1]*0.1)),int(round(size[1]*0.5)))
                                mete_end_y = random.randint(int(round(size[1]*0.5)),int(round(size[1]*1.2)))
                                mete_begin_position = (size[0],mete_begin_y)
                                mete_end_position = (-mete_obj.rect.width,mete_end_y)
                                mete_inf.add(2)
                                mete_obj.set_inf(2)
                            
                            # 右下
                            elif 3 not in mete_inf:
                                mete_end_y = random.randint(int(round(size[1]*0.1)),int(round(size[1]*0.5)))
                                mete_begin_y = random.randint(int(round(size[1]*0.5)),int(round(size[1]*1.2)))
                                mete_begin_position = (size[0],mete_begin_y)
                                mete_end_position = (-mete_obj.rect.width,mete_end_y)
                                mete_inf.add(3)
                                mete_obj.set_inf(3)

                            mete_obj.move(mete_begin_position)
                            mete_obj.set_speed(e_speed_count(mete_begin_position,mete_end_position,(120/fps)*3.75*random.randint(10,20)*0.03))
                            #print(mete_begin_position,mete_end_position)
                            #print(mete_obj.speed)

                            mete.add(mete_obj)
                        
                    mete.update()
                    mete.draw(window)

                    for sprite in mete.sprites():
                        if sprite.outside():
                            #print(sprite.rect.left,sprite.inf)
                            mete.remove(sprite)
                            mete_inf.remove(sprite.inf)

                        elif pygame.sprite.collide_mask(sprite,player):
                            player.get_hurt(100)
                    
                    if prop_refresh:
                        #print(prop_time_reset)
                        #print(prop.outside())
                        if prop.outside() and prop_time_reset:
                            #print(2)
                            pygame.time.set_timer(PROP,15000,1)
                            prop_time_reset = False
                            prop_refresh = False
                        #print(prop.rect)
                        elif pygame.sprite.collide_mask(prop,player):
                            pygame.time.set_timer(PROP,15000,1)
                            prop_refresh = False
                            prop.move((-200,-200))
                            if prop.inf == 0:
                                #护盾
                                player_sheld_on = True
                                pygame.time.set_timer(SHELDOFF,4000,1)
                            elif prop.inf == 1:
                                #医疗包
                                if player.hp + 10 < 100:
                                    player.hp += 20
                                elif player.hp + 10 >= 100:
                                    player.hp = 100

                        prop.update()
                        prop.draw()

                    # 判断是否生成敌机
                    if mod == 0:
                        # 判断生成敌机种类
                        #print(1)
                        mod = random.randint(1,2)
                        upgrade = True
                        anime = True
                        dead = False
                        
                    if mod == 1 and upgrade:
                        enemy = Ship('./source/anti_1.png',(0,-180),7)
                        enemy.scale((enemy.rect.width*0.8*(size[1]/720),enemy.rect.height*0.68*(size[1]/720)))
                        enemy.mid()
                        upgrade = False
                        pygame.time.set_timer(ENEMYFIRE,1000,1)

                    if mod == 2 and upgrade:   
                        enemy = Ship('./source/anti_2.png',(0,-180),5)
                        enemy.scale((enemy.rect.width*0.8*(size[1]/720),enemy.rect.height*0.8*(size[1]/720)))
                        enemy.mid()
                        enemy_direction = {0:False,1:True}[random.randint(0,1)]
                        upgrade = False
                        pygame.time.set_timer(ENEMYFIRE,500,1)

                    # 进入动画
                    if anime:
                        enemy.move((0,10*size[1]/540))

                        if enemy.rect.top > 0:
                            anime = False
                            enemy.move((0,0))
                    
                    #射击
                    else:
                        if live(enemy):
                            if mod == 1:
                                if enemyfire and (not dead):
                                    enemyfire = False
                                    bullet_m_1 = enemy_bullet_pool.get()
                                    bullet_m_2 = enemy_bullet_pool.get()
                                    bullet_m_3 = enemy_bullet_pool.get()
                                    bullet_m_1.scale((5*size[1]/540,24*size[1]/540))
                                    bullet_m_2.scale((5*size[1]/540,24*size[1]/540))
                                    bullet_m_3.scale((5*size[1]/540,24*size[1]/540))
                                    bullet_m_1.set_speed((0,(120/fps)*3*size[1]/720))
                                    bullet_m_2.set_speed((0,(120/fps)*3*size[1]/720))
                                    bullet_m_3.set_speed((0,(120/fps)*3*size[1]/720))
                                    bullet_m_1.move((enemy.rect.left+enemy.rect.w/2-10*size[0]/540,enemy.rect.bottom))
                                    bullet_m_2.move((enemy.rect.left+enemy.rect.w/2+10*size[0]/540,enemy.rect.bottom))
                                    bullet_m_3.move((enemy.rect.left+enemy.rect.w/2-0*size[0]/540,enemy.rect.bottom))
                                    enemy_bullet_2.add(bullet_m_2)
                                    enemy_bullet_1.add(bullet_m_1)
                                    enemy_bullet_3.add(bullet_m_3)
                                    bullet_l_1 = enemy_bullet_pool.get()
                                    bullet_l_2 = enemy_bullet_pool.get()
                                    bullet_l_1.scale((5*size[1]/540,24*size[1]/540))
                                    bullet_l_2.scale((5*size[1]/540,24*size[1]/540))
                                    bullet_l_1.rotate( -60)
                                    bullet_l_2.rotate(-30)
                                    bullet_l_1.set_speed((-(120/fps)*1.5*1.732*size[1]/720,(120/fps)*3*0.5*size[1]/720))
                                    bullet_l_2.set_speed((-(120/fps)*1.5*size[1]/720,(120/fps)*1.5*1.732*size[1]/720))
                                    bullet_l_1.move((enemy.rect.left+enemy.rect.w*0.2-bullet_l_1.rect.w,enemy.rect.bottom-(1/6)*enemy.rect.h))
                                    bullet_l_2.move((enemy.rect.left+enemy.rect.w*0.2-bullet_l_2 .rect.w,enemy.rect.bottom-(1/6)*enemy.rect.h))
                                    enemy_bullet_1.add(bullet_l_1)
                                    enemy_bullet_2.add(bullet_l_2)
                                    bullet_r_1 = enemy_bullet_pool.get()
                                    bullet_r_2 = enemy_bullet_pool.get()
                                    bullet_r_1.scale((5*size[1]/540,24*size[1]/540))
                                    bullet_r_2.scale((5*size[1]/540,24*size[1]/540))
                                    bullet_r_1.rotate(60)
                                    bullet_r_2.rotate(30)
                                    bullet_r_1.set_speed((1.5*(120/fps)*1.732*size[1]/720,(120/fps)*3*0.5*size[1]/720))
                                    bullet_r_2.set_speed((1.5*(120/fps)*size[1]/720,(120/fps)*1.5*1.732*size[1]/720))
                                    bullet_r_1.move((enemy.rect.left+enemy.rect.w*0.8,enemy.rect.bottom-(1/6)*enemy.rect.h))
                                    bullet_r_2.move((enemy.rect.left+enemy.rect.w*0.8,enemy.rect.bottom-(1/6)*enemy.rect.h))
                                    enemy_bullet_3.add(bullet_r_1)
                                    enemy_bullet_1.add(bullet_r_2)
                                    if bullet_count < 6:
                                        pygame.time.set_timer(ENEMYFIRE,200,1)
                                        bullet_count += 1
                                    else:
                                        bullet_count = 0
                                        pygame.time.set_timer(ENEMYFIRE,1000,1)
                                    
                            if mod == 2:
                                if enemy.outside() and change_direction:
                                    enemy_direction = not enemy_direction
                                    pygame.time.set_timer(CHANGE_DIRECTION,50,1)
                                    change_direction = False 
                                enemy.move((1.5*(120/fps)*(size[1]/540),0)) if enemy_direction else enemy.move((-1.5*(120/fps)*(size[1]/540),0))
                                if enemyfire:
                                    enemyfire = False
                                    bullet_l = enemy_bullet_pool.get()
                                    bullet_2 = enemy_bullet_pool.get()
                                    bullet_l.scale((5*size[1]/540,24*size[1]/540))
                                    bullet_2.scale((5*size[1]/540,24*size[1]/540))
                                    bullet_l.set_speed((0,(120/fps)*3*size[1]/720))
                                    bullet_2.set_speed((0,(120/fps)*3*size[1]/720))
                                    bullet_l.move(((enemy.rect.left + enemy.rect.w/2 - 6*size[0]/540),enemy.rect.bottom))
                                    bullet_2.move(((enemy.rect.left + enemy.rect.w/2 + 6*size[0]/540),enemy.rect.bottom))
                                    enemy_bullet_2.add(bullet_l)
                                    enemy_bullet_3.add(bullet_2)
                                    pygame.time.set_timer(ENEMYFIRE,500,1)

                        else:
                        # print(enemy.rect.left,mod)
                            enemy.get_outside()
                        # print(enemy.rect,mod)
                            if mod == 1:
                                dead = True
                            enemy.get_hurt(-1)
                            dead = True
                            #enemy.kill()
                            pygame.time.set_timer(ANTICHANGE,1000,1)
                            score_count += 200
                    #print(enemy.rect,'end',mod)
                    window.blit(enemy.image,enemy.rect)
                    #print(len(enemy_bullet.sprites()))
                    enemy_bullet_1.update()
                    enemy_bullet_1.draw(window)
                    enemy_bullet_2.update()
                    enemy_bullet_2.draw(window)
                    enemy_bullet_3.update()
                    enemy_bullet_3.draw(window)    

                    bullet_iter = [enemy_bullet_1.sprites(),enemy_bullet_2.sprites(),enemy_bullet_3.sprites()][frame_num]
                    #for bullet_iter in enemy_bullet:
                    if not player_sheld_on:
                        for bullet in bullet_iter:
                            if bullet.outside():
                                bullet.kill()
                                bullet.init()
                                enemy_bullet_pool.return_bullet(bullet)                                
                            elif pygame.sprite.collide_mask(bullet,player):
                                bullet.kill()
                                bullet.init()
                                enemy_bullet_pool.return_bullet(bullet)
                                player.get_hurt(20)
                                theposition = player.position
                                # print(player.rect,theposition)
                                player.change_img('./source/player_damage.png')
                                player.moveto(theposition)
                                #print(player.rect)
                                player.scale((33*(size[1]/540),61*(size[1]/540)))
                                pygame.time.set_timer(PLAYERNORMAL,100,1)
                            else:
                                for sprite in mete.sprites():
                                    if pygame.sprite.collide_mask(bullet,sprite):
                                        bullet.kill()    
                                        bullet.init()
                                        enemy_bullet_pool.return_bullet(bullet)
                    else:
                        for bullet in bullet_iter:
                            if bullet.outside():
                                bullet.kill()
                                bullet.init()
                                enemy_bullet_pool.return_bullet(bullet)                                
                            elif pygame.sprite.collide_mask(bullet,sheld_obj):
                                bullet.kill()
                                bullet.init()
                                enemy_bullet_pool.return_bullet(bullet)
                                #theposition = player.position
                                # print(player.rect,theposition)
                                #  player.change_img('./source/player_damage.png')
                                # player.moveto(theposition)
                                    #print(player.rect)
                                    #player.scale((33*(size[1]/540),61*(size[1]/540)))
                                    #pygame.time.set_timer(PLAYERNORMAL,100,1)
                            else:
                                for sprite in mete.sprites():
                                    if pygame.sprite.collide_mask(bullet,sprite):
                                        bullet.kill()    
                                        bullet.init()                                            
                                        enemy_bullet_pool.return_bullet(bullet)
                    
                    # 主角射击
                    if playerfire:
                        player_bullet = player_bullet_pool.get()
                        player_bullet.set_speed((0,-(120/fps)*5*size[1]/720))
                        player_bullet.scale((5*size[1]/540,24*size[1]/540))
                        playerfire = False
                        player_bullet.move((player.rect.left+player.rect.w/2,player.rect.top-player_bullet.rect.h))
                        player_bullet_group.add(player_bullet)
                        pygame.time.set_timer(PLAYERFIRE,400,1)

                    for bullet in player_bullet_group.sprites():
                        if bullet.outside():
                            bullet.kill()
                            bullet.init()
                            player_bullet_pool.return_bullet(bullet)
                        elif pygame.sprite.collide_mask(enemy,bullet) and live(enemy):
                            bullet.kill()
                            bullet.init()
                            player_bullet_pool.return_bullet(bullet)
                            enemy.get_hurt(1)
                            if mod == 2:
                        # print(enemy.rect,mod)
                                the_enemy_position = enemy.position
                            #  print(enemy.rect,mod)
                                enemy.change_img('./source/anti_'+{0:'1',1:'1',2:'2'}[mod]+'_damage.png')
                                enemy.moveto(the_enemy_position)
                                #print(player.rect)
                                enemysize = {1:(75*(size[1]/720),128*(size[1]/720)),2:(51*(size[1]/720),86*(size[1]/720))}[mod]
                                enemy.scale(enemysize)
                                pygame.time.set_timer(ENEMYNORMAL,100,1)
                            elif mod == 1:
                                the_enemy_position = enemy.position
                            #  print(enemy.rect,mod)
                                anti1=Ship('./source/anti_'+{0:'1',1:'1',2:'2'}[mod]+'_damage.png',(0,0),0)
                                anti1.moveto(the_enemy_position)
                                #print(player.rect)
                                enemysize = {1:(75*(size[1]/720),128*(size[1]/720)),2:(51*(size[1]/720),86*(size[1]/720))}[mod]
                                anti1.scale(enemysize)
                                pygame.time.set_timer(ENEMYNORMAL,100,1)
                                hitting = True
                        else:
                            for sprite in mete.sprites():
                                if pygame.sprite.collide_mask(bullet,sprite):
                                        bullet.kill()   
                                        bullet.init()
                                        player_bullet_pool.return_bullet(bullet)

                    player_bullet_group.update()
                    player_bullet_group.draw(window)
                    if hitting:
                        window.blit(anti1.image,enemy.rect)
                    # 绘制右上角信息
                    score_text = pixel_font_small.render('score: '+str(score),False,(255,255,255))
                    hp_text = pixel_font_small.render('HP: '+str(int(player.hp)),False,(255,255,255))
                    window.blit(score_text,(0,0))
                    window.blit(hp_text,(0,score_text.get_rect().height))

                    frame_num = {0:1,1:2,2:0}[frame_num]
                    
                    #print(clock.get_fps(),mod)

                    pygame.display.update()
                # test = pygame.image.load('./source/anti_1.png').convert_alpha()

                #hp_text = pixel_font_small.render('HP: '+str(int(player.hp)),False,(255,255,255))
                #window.blit(hp_text,(0,score_text.get_rect().height))
                pygame.mixer.music.stop()
                # 判断分数
                if score_count > record_float:
                    save({'record':score,'record_float':score_count},'DATA.JSON')
                    text = ('N E W','R E C O R D !')
                else:
                    text = ('G A M E','O V E R !')
                #test = pygame.image.load('./source/anti_1.png').convert_alpha()
                shake = 1
                # 结束动画
                while shake < 11:
                    clock.tick(5)
                    theposition = player.position
                # print(int(shake%1))
                    player.change_img({0:'./source/player_damage.png',1:'./source/player.png'}[int(shake%2)])
                    player.moveto(theposition)
                    player.scale((33*(size[1]/540),61*(size[1]/540)))
                    window.blit(player.image,player.rect)
                    pygame.display.update()
                    shake+=1
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            sys.exit()

                pygame.image.save(window,'./data/bga.tga')
                opt_num = 0
                choose_again = False
                choose_back = False
                breaking = False

                while True:
                    clock.tick(30)
                    window.blit(pygame.image.load('./data/bga.tga').convert(),(0,0))
                    #pygame.display.update()
                    # 绘制标题
                    title_up = pixel_font_mid.render(text[0],False,(255,255,255))
                    title_down = pixel_font_mid.render(text[1],False,(255,255,255))
                    window.blit(title_up,(mid(size,title_up),size[1]*0.2))
                    window.blit(title_down,(mid(size,title_down),size[1]*0.2+title_up.get_rect().h))
                    # 绘制选项
                    again = cn_font_small.render('重新开始',True,(255,255,255))
                    anti_again = cn_font_small.render('重新开始',True,(0,0,0))
                    back = cn_font_small.render('回到菜单',True,(255,255,255))
                    anti_back = cn_font_small.render('回到菜单',True,(0,0,0))
                    end = cn_font_small.render('退出游戏',True,(255,255,255))
                    anti_end = cn_font_small.render('退出游戏',True,(0,0,0))

                    window.blit(again,(mid(size,again),size[1]*0.5))
                    window.blit(back,(mid(size,back),size[1]*0.65))
                    window.blit(end,(mid(size,end),size[1]*0.8))
                    # 选择again
                    if opt_num == 0:
                        #print(again.get_rect())
                        pygame.draw.rect(window,(255,255,255),[mid(size,again),size[1]*0.5,again.get_rect().w,again.get_rect().h])
                        window.blit(anti_again,(mid(size,again),size[1]*0.5))
                    
                    elif opt_num == 1:
                        pygame.draw.rect(window,(255,255,255),(mid(size,back),size[1]*0.65,back.get_rect().w,back.get_rect().h))
                        window.blit(anti_back,(mid(size,back),size[1]*0.65))
                    
                    elif opt_num == 2:
                        pygame.draw.rect(window,(255,255,255),(mid(size,end),size[1]*0.8,end.get_rect().w,end.get_rect().h))
                        window.blit(anti_end,(mid(size,end),size[1]*0.8))

                    pygame.display.update()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            sys.exit()
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_DOWN:
                                opt_num = (opt_num+1)%3
                            elif event.key == pygame.K_UP:
                                opt_num = (opt_num-1)%3
                            elif event.key == pygame.K_SPACE:
                                if opt_num == 0:
                                    choose_again = True
                                    breaking = True
                                    break
                                elif opt_num == 1:
                                    choose_back = True
                                    breaking = True
                                    break
                                elif opt_num == 2:
                                    sys.exit()
                    if breaking:
                        break
                
                if choose_again:
                    pass
                elif choose_back:
                    break