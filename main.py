import pygame
from os import listdir, path
from time import sleep


class Game:
    def __init__(self):
        pygame.init()

        icon_img = pygame.image.load("assets/icon.jpg")
        pygame.display.set_caption("Anti-Plague Simulator")
        pygame.display.set_icon(icon_img)

        self.screen = pygame.display.set_mode((1080, 720))
        self.imgs = dict()
        for file in self.get_all_files("./assets", start_string=''):
            self.imgs[file.split('.')[0].replace('/', '.')] = pygame.image.load(file)

        self.running = True
        self.keys_pressed = []
        self.font = pygame.font.Font('freesansbold.ttf', 32)

    def get_all_files(self, directory, extension='*', start_string='./'):
        if directory.endswith('/') or directory.endswith('\\'):
            directory = directory[:-1]

        for thing in listdir(directory):
            condition = thing.endswith(f'.{extension}')
            if extension == '*':
                condition = thing.count('.') > 0

            if condition:
                yield start_string + thing
            elif '.' not in thing:
                for nxt in self.get_all_files(path.join(directory, thing), extension, f'{start_string + thing}/'):
                    yield nxt

    # Montagem dos Niveis
    def __days(self):
        x = 750
        ini_y = 30
        dif_y = 50
        black = (0, 0, 0)
        blue = (0, 0, 255)
        txts = [
            (pygame.transform.scale(self.imgs['Colors.white'], (350, dif_y*3)), (x-20, ini_y - 30)),

            (self.font.render(f"{self.dias:.0f} dias restantes", True, black), (x, ini_y)),
            (self.font.render(f"(espaço)", True, blue), (x + 50, ini_y + dif_y)),
        ]
        for txt in txts:
            self.screen.blit(*txt)
    
    def __info(self):
        size = 30
        x_icon = 10
        x_text = x_icon + size*4
        ini_y = 450
        dif_y = 50
        black = (0, 0, 0)
        blue = (0, 0, 255)
        txts = [
            (pygame.transform.scale(self.imgs['Colors.white'], (600, 720 - dif_y)), (0, ini_y - dif_y)),
            # Dinheiro
            (pygame.transform.scale(self.imgs['Icones.money'], (size, size)), (x_icon, ini_y)),
            (self.font.render(f"{self.money:.0f} R$", True, black), (x_text, ini_y)),
            # Leitos
            (pygame.transform.scale(self.imgs['Icones.leito'], (size, size)), (x_icon, ini_y + dif_y)),
            (self.font.render(f"(a)", True, blue), (x_text - size * 2, ini_y + dif_y)),
            (self.font.render(f"{self.leitos:.0f} leitos", True, black), (x_text, ini_y + dif_y)),
            # Mascaras
            (pygame.transform.scale(self.imgs['Icones.mascara'], (size, size)), (x_icon, ini_y + dif_y * 2)),
            (self.font.render(f"(s)", True, blue), (x_text - size * 2, ini_y + dif_y * 2)),
            (self.font.render(f"{self.mascaras:.0f} mascaras", True, black), (x_text, ini_y + dif_y * 2)),
            # Graves
            (pygame.transform.scale(self.imgs['Icones.graves'], (size, size)), (x_icon, ini_y + dif_y * 3)),
            (self.font.render(f"{self.graves:.0f} casos graves", True, black), (x_text, ini_y + dif_y * 3)),
            # Pessoas Circulando
            (pygame.transform.scale(self.imgs['Icones.pessoas'], (size, size)), (x_icon, ini_y + dif_y * 4)),
            (self.font.render(f"(d)", True, blue), (x_text - size * 2, ini_y + dif_y * 4)),
            (self.font.render(f"{self.circulando:.0f} pessoas circulando", True, black), (x_text, ini_y + dif_y * 4)),
        ]
        for txt in txts:
            self.screen.blit(*txt)

    def __grafico(self):
        mortespct = self.mortes/10000
        infectpct = self.infectados/10000
        saudaspct = self.saudaveis/10000
        # Grafico

        tam = 280
        size = int((mortespct + infectpct + saudaspct) * (tam / 100))
        displace = int((tam - size) / 2)
        self.screen.blit(pygame.transform.scale(self.imgs['Grafico.Amarelo'], (size, size)), (displace, displace))

        size = int((mortespct + infectpct) * (tam / 100))
        displace = int((tam - size) / 2)
        self.screen.blit(pygame.transform.scale(self.imgs['Grafico.Vermelho'], (size, size)), (displace, displace))

        size = int(mortespct * (tam / 100))
        displace = int((tam - size) / 2)
        self.screen.blit(pygame.transform.scale(self.imgs['Grafico.Preto'], (size, size)), (displace, displace))

        # Legenda

        x = 300
        y_ini = 100
        dif = 50
        txts = [
            (pygame.transform.scale(self.imgs['Colors.white'], (300, 200)), (x-20, y_ini-40)),
            (self.font.render(f"{mortespct:.0f}% Mortos", True, (0, 0, 0)), (x, y_ini)),
            (self.font.render(f"{infectpct:.0f}% Infectados", True, (255, 0, 0)), (x, y_ini+dif)),
            (self.font.render(f"{saudaspct:.0f}% Infectados", True, (0, 255, 0)), (x, y_ini+dif*2)),
            ]
        for txt in txts:
            self.screen.blit(*txt)

    def __lvl(self, background, preco, lvl_id):
        # Variaveis
        self.dias = 365
        self.novos_infectados = []
        self.infectados = 500
        self.graves = 0.05 * self.infectados
        self.saudaveis = 999500
        self.mortes = 0
        self.novas_mortes = 0
        self.imunes = 0

        self.money = 5000
        self.leitos = 1000
        self.circulando = 1000000
        self.mascaras = 0

        self.preco_leitos = 200
        self.preco_mascara = 300
        self.preco_campanha = 100

        run = True
        frames = 0
        while run:
            # Blits
            self.screen.blit(pygame.transform.scale(background, (1080, 720)), (0, 0))
            self.__grafico()
            self.__info()
            self.__days()

            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self.keys_pressed.append(event.key)
                elif event.type == pygame.KEYUP:
                    self.keys_pressed.remove(event.key)
            if frames % 3:
                if pygame.K_a in self.keys_pressed and self.money >= self.preco_leitos*preco:
                    self.money -= self.preco_leitos*preco
                    self.leitos += 1000
                if pygame.K_s in self.keys_pressed and self.money >= self.preco_mascara*preco:
                    self.money -= self.preco_mascara*preco
                    self.mascaras += 1000
                    self.contagio -= 0.002
                if pygame.K_d in self.keys_pressed and self.money >= self.preco_campanha*preco:
                    self.money -= self.preco_campanha * preco
                    self.circulando -= 1000
                    self.contagio -= 0.001
                if pygame.K_SPACE in self.keys_pressed:
                    self.__day()

            # Finalização
            pygame.display.update()
            frames += 1
            if self.dias == 0:
                self.__win(lvl_id)
                run = False
            sleep(0.03)

    # Niveis
    def __lvl1(self):
        self.sem_leito = 0.5
        self.com_leito = 0.2
        self.contagio = 0.5
        self.__lvl(self.imgs['Background.China'], 1, 1)

    def __lvl2(self):
        self.sem_leito = 0.8
        self.com_leito = 0.4
        self.contagio = 0.6
        self.__lvl(self.imgs['Background.Italia'], 1, 2)

    def __lvl3(self):
        self.sem_leito = 0.5
        self.com_leito = 0.2
        self.contagio = 0.5
        self.__lvl(self.imgs['Background.EUA'], 2, 3)

    def __boss(self):
        self.sem_leito = 0.8
        self.com_leito = 0.5
        self.contagio = 0.8
        self.__lvl(self.imgs['Background.Brasil'], 2, 4)

    # Outras Telas
    def __win(self, lvl):
        if self.mortes > 300000:
            result = 'lose'
        else:
            result = str(lvl)

        self.screen.blit(pygame.transform.scale(self.imgs[f'Fim de Fase.{result}'], (1080, 720)), (0, 0))
        pygame.display.update()
        sleep(2)

        action = False
        while not action:
            self.screen.blit(pygame.transform.scale(self.imgs[f'Fim de Fase.{result}'], (1080, 720)), (0, 0))
            pygame.display.update()
            for event in pygame.event.get():
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    action = True
                if event.type == pygame.QUIT:
                    action = True
                    self.running = False

    def __inicio(self):
        def blit(dimension):
            self.screen.fill((255, 255, 255))
            self.screen.blit(pygame.transform.scale(self.imgs[f'Start Button.{dimension}'], (1500, 1000)), (0, 0))
            pygame.display.update()
        blit(3)
        click = False
        while not click:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    click = True
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    blit(2)
                elif event.type == pygame.MOUSEBUTTONUP:
                    click = True

    # Calculos
    def __day(self):
        if self.graves > self.leitos:
            self.taxa_de_morte = ((self.leitos*self.com_leito) + (self.graves-self.leitos)*self.sem_leito) / self.graves
        else:
            self.taxa_de_morte = self.com_leito
        self.novos_infectados.append(self.contagio*(self.saudaveis*self.infectados)/(self.saudaveis+self.infectados))
        if len(self.novos_infectados) >= 10:
            pop = self.novos_infectados.pop(0)
            self.novas_mortes = pop*0.1*self.taxa_de_morte
            self.mortes += self.novas_mortes
            self.infectados -= pop - self.novas_mortes
            self.imunes += (pop - self.novas_mortes) / 2
        self.infectados += self.novos_infectados[-1] - self.novas_mortes
        self.graves = self.infectados * 0.05
        self.saudaveis = 1000000 - self.infectados - self.mortes - self.imunes
        self.circulando -= self.novas_mortes
        self.money += round(self.circulando*0.0015 - 800)
        self.dias -= 1
        if self.money < 0:
            self.__win('noMoney')

    def run(self):
        sleep(1)
        pygame.event.get()

        if self.running:
            self.__inicio()
        if self.running:
            self.__lvl1()
        if self.running:
            self.__lvl2()
        if self.running:
            self.__lvl3()
        if self.running:
            self.__boss()


gm = Game()
gm.run()
