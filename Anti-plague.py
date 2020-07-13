from os import listdir, path
from random import choice
import cv2
import pygame
pygame.init()


class Colors:
    BLUE = (50, 50, 255)
    GREEN = (50, 230, 50)
    RED = (240, 50, 50)
    PURPLE = (200, 50, 230)
    WHITE = (243, 246, 248)
    BLACK = (10, 10, 10)
    GRAY50 = (50, 50, 50)
    GRAY100 = (100, 102, 104)
    YELLOW = (255, 255, 20)


class Fonts:
    FONT18 = pygame.font.SysFont('Agency FB', 18, True)
    FONT30 = pygame.font.SysFont('Agency FB', 30)
    FONT40 = pygame.font.SysFont('Agency FB', 40)
    FONT80 = pygame.font.SysFont('Agency FB', 80)
    FONT95 = pygame.font.SysFont('Agency FB', 95, True)


class Game:
    def __init__(self):
        self.tela = pygame.display.set_mode((1366, 768), pygame.FULLSCREEN)
        self.dp_height = pygame.display.Info().current_h
        self.dp_width = pygame.display.Info().current_w
        self.graph_size = 8 * self.dp_height // 49
        self.info_size = self.dp_width // 3

        files = self.__get_all_files("./Data", start_string='')
        self.imgs = {file.split('.')[0]: pygame.image.load(f"Data/{file}") for file in files}

        # consts
        self.mascara_img = self.imgs["Mascara"]
        self.leito_img = self.imgs["Leito"]
        self.pessoas_img = self.imgs["Pessoas"]

        self.contagio = 0.3
        self.taxa_de_graves = 0.15
        self.taxa_de_morte = [0.2]

    def __get_all_files(self, directory, extension='*', start_string='./'):
        if directory.endswith('/') or directory.endswith('\\'):
            directory = directory[:-1]

        for thing in listdir(directory):
            condition = thing.endswith(f'.{extension}')
            if extension == '*':
                condition = thing.count('.') > 0

            if condition:
                yield start_string + thing
            elif '.' not in thing:
                for nxt in self.__get_all_files(path.join(directory, thing), extension, f'{start_string + thing}/'):
                    yield nxt

    def __lvl(self, price_multiplier):
        self.mascara_price = 200 * price_multiplier
        self.leitos_price = 300 * price_multiplier
        self.pessoas_price = 150 * price_multiplier
        self.mascara_qtd = 0
        self.leitos_qtd = 1000
        self.pessoas_qtd = 1000000
        self.saudaveis = [999999]
        self.infectados = [20, 20]
        self.mortos = [0, 0]
        self.imunes = [0, 0]
        self.novos_infectados = list()
        self.novos_mortos = 0

        self.main_img = self.imgs[f"{self.pais}/Main"]
        self.fundo_img = self.imgs[f"{self.pais}/Fundo"]
        self.__transparente()

        self.mascara_price_img = Fonts.FONT40.render(f'R${self.mascara_price}', True, (0, 0, 0))
        self.leitos_price_img = Fonts.FONT40.render(f'R${self.leitos_price}', True, (0, 0, 0))
        self.pessoas_price_img = Fonts.FONT40.render(f'R${self.pessoas_price}', True, (0, 0, 0))

        self.mascara_qtd_img = Fonts.FONT30.render(f'Qtd.:{self.mascara_qtd}', True, Colors.WHITE)
        self.leitos_qtd_img = Fonts.FONT30.render(f'Qtd.:{self.leitos_qtd}', True, Colors.WHITE)
        self.pessoas_qtd_img = Fonts.FONT30.render(f'Qtd.:{self.pessoas_qtd}', True, Colors.WHITE)

        self.pais_img = Fonts.FONT80.render(self.pais, True, (0, 0, 0))

        self.loop()

    def __transparente(self):
        img = cv2.imread(f"Data/{self.pais}/Fundo.png")
        height = len(img)
        width = len(img[0])
        self.transparente = []
        for x in range(width):
            for y in range(height):
                if img[y][x][0] == img[y][x][1] == img[y][x][2] == 0:
                    new_x = (self.dp_width - self.info_size) * x / width
                    new_y = self.dp_height * y / height
                    self.transparente.append((int(new_x), int(new_y)))

    def __pontos(self, qtd, img):
        for _ in range(int(qtd * len(self.transparente) / 100000000)):
            x, y = choice(self.transparente)
            self.tela.blit(pygame.transform.scale(img, (8, 8)), (x + self.info_size, y))

    def __blit_info(self):
        self.tela.blit(pygame.transform.scale(self.main_img, (self.dp_width - self.info_size, self.dp_height)),
                       (self.info_size, 0))
        self.__pontos(self.saudaveis[-1], self.imgs["Green"])
        self.__pontos(self.infectados[-1], self.imgs["Red"])
        #self.__pontos(self.mortos[-1], self.imgs["Black"])
        self.__pontos(self.imunes[-1], self.imgs["Blue"])
        self.tela.blit(pygame.transform.scale(self.fundo_img, (self.dp_width - self.info_size, self.dp_height)),
                       (self.info_size, 0))

        self.tela.blit(self.pais_img, (self.info_size + 100, 50))

        pygame.draw.rect(self.tela, Colors.GRAY100, ((0, 0), (self.info_size, self.dp_height)))
        titulos = ('Nº Saudáveis: ' + str(int(self.saudaveis[-1])), 'Nº Infectados: ' + str(int(self.infectados[-1])),
                   'Nº Mortos: ' + str(int(self.mortos[-1])), 'Nº Imunes: ' + str(int(self.imunes[-1])),
                   'Geral: ', 'Taxa de Morte')
        titulo_img = [Fonts.FONT18.render(ttl, True, Colors.WHITE) for ttl in titulos]

        for i in range(6):
            pt1 = (int(self.info_size*0.1), ((8 * self.dp_height * i) + self.dp_height) // 49)
            pygame.draw.rect(self.tela, Colors.GRAY50, (pt1, (int(self.info_size*0.8), self.dp_height // 7)))
            pygame.draw.rect(self.tela, Colors.BLACK, (pt1, (int(self.info_size*0.8), self.dp_height // 40)))
            self.tela.blit(titulo_img[i], (int(self.info_size*0.11), ((8 * self.dp_height * i) + self.dp_height) // 49))

        saudaveis_img = Fonts.FONT95.render('{:.1f}'.format(self.saudaveis[-1] / 10000) + '%', True, Colors.WHITE)
        self.__blit_grafico(self.saudaveis, 0, Colors.GREEN, saudaveis_img, True)

        infectados_img = Fonts.FONT95.render('{:.1f}'.format(self.infectados[-1] / 10000) + '%', True, Colors.WHITE)
        self.__blit_grafico(self.infectados[:-1], 1 * self.graph_size, Colors.RED, infectados_img, True)

        mortos_img = Fonts.FONT95.render('{:.1f}'.format(self.mortos[-1] / 10000) + '%', True, Colors.WHITE)
        self.__blit_grafico(self.mortos, 2 * self.graph_size, Colors.PURPLE, mortos_img, True)

        imunes_img = Fonts.FONT95.render('{:.1f}'.format(self.imunes[-1] / 10000) + '%', True, Colors.WHITE)
        self.__blit_grafico(self.imunes, 3 * self.graph_size, Colors.BLUE, imunes_img, True)

        taxa_de_morte_img = Fonts.FONT95.render("{:.2f}".format(self.taxa_de_morte[-1]), True, Colors.WHITE)
        self.__blit_grafico(self.taxa_de_morte, 5 * self.graph_size, Colors.BLACK, taxa_de_morte_img)

        self.pessoas_qtd_img = Fonts.FONT30.render(f'Qtd.:{int(self.pessoas_qtd)}', True, Colors.WHITE)

        self.__grafico_geral(self.saudaveis, Colors.GREEN)
        self.__grafico_geral(self.infectados, Colors.RED)
        self.__grafico_geral(self.mortos, Colors.PURPLE)
        self.__grafico_geral(self.imunes, Colors.BLUE)

    def __blit_botoes(self):
        options = [[self.mascara_img, self.mascara_price_img, self.mascara_qtd_img, 550],
                   [self.leito_img, self.leitos_price_img, self.leitos_qtd_img, self.dp_width // 3 + 367],
                   [self.pessoas_img, self.pessoas_price_img, self.pessoas_qtd_img, int(self.dp_width / 1.5 + 183)]]
        for i in range(3):
            icon_bt, price, qtd, pos_x = options[i]
    
            pygame.draw.rect(self.tela, Colors.GREEN, ((pos_x, self.dp_height - 130), (80, 80)))
            self.tela.blit(icon_bt, (pos_x + 10, self.dp_height - 120))
            self.tela.blit(price, (pos_x + 90, self.dp_height - 130))
            pygame.draw.rect(self.tela, Colors.BLACK, ((pos_x + 90, self.dp_height - 80), (150, 30)))
            self.tela.blit(qtd, (pos_x + 93, self.dp_height - 83))

        # Passar o dia
        '''
        icon_bt = self.imgs["Clock"]
        size = 64
        margin = 10

        pygame.draw.rect(self.tela, Colors.YELLOW, ((self.dp_width - size - margin, margin), (size, size)))
        self.tela.blit(icon_bt, (self.dp_width - size - margin, margin))
        pygame.draw.rect(self.tela, Colors.BLACK, ((self.dp_width - size - margin, margin + size), (size, size)))
        '''

    def __grafico_geral(self, values, cor):
        coords = list()
        height = (4 * self.dp_height / 35) / 1000000
        width = self.info_size * 0.8 / (len(values) - 1)

        for index, b in enumerate(values):
            coords.append((int(self.info_size * 0.1 + width * index), int(5 * self.graph_size - height * int(b))))

        pygame.draw.lines(self.tela, cor, False, coords, 3)

    def __blit_grafico(self, values, altura, cor, numero, inteiro=False):
        coords = [(int(self.info_size*0.9), altura + self.graph_size), (int(self.info_size*0.1), altura + self.graph_size)]
        height = (4 * self.dp_height / 35) / max(values) if max(values) else (4 * self.dp_height / 35)
        width = self.info_size*0.8 / (len(values) - 1)

        for index, b in enumerate(values):
            if inteiro:
                b = int(b)
            coords.append((int(self.info_size*0.1 + width * index), int(altura + self.graph_size - height * b)))

        pygame.draw.polygon(self.tela, cor, coords)
        self.tela.blit(numero, (int(self.info_size*0.3), int(altura + self.dp_height / 30)))

    def __day(self):
        graves = self.infectados[-1] * self.taxa_de_graves
        if graves > self.leitos_qtd:
            nova_taxa = ((self.leitos_qtd * self.com_leito) + (graves - self.leitos_qtd) * self.sem_leito) / graves
        else:
            nova_taxa = self.com_leito
        self.taxa_de_morte.append(nova_taxa)
        passiveis = self.saudaveis[-1] - self.imunes[-1]
        self.novos_infectados.append(
            self.contagio * (passiveis * self.infectados[-1]) / (passiveis + self.infectados[-1]))
        novos_mortos = 0
        if len(self.infectados) >= 10:
            pop = self.novos_infectados.pop(0)
            novos_mortos = pop * self.taxa_de_graves * self.taxa_de_morte[-1]
            self.mortos.append(self.mortos[-1] + novos_mortos)
            self.infectados[-1] -= pop - novos_mortos
            self.imunes.append(self.imunes[-1] + (pop - novos_mortos) * 0.01)
        self.infectados.append(self.infectados[-1] + (self.novos_infectados[-1] - novos_mortos))
        self.saudaveis.append(1000000 - self.infectados[-1] - self.mortos[-1])
        self.pessoas_qtd -= novos_mortos

    def __events_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.dp_height - 130 < event.pos[1] < self.dp_height - 50:
                    if 550 < event.pos[0] < 630:  # Mascaras
                        self.mascara_qtd += 2000
                        self.mascara_qtd_img = Fonts.FONT30.render(f'Qtd.:{self.mascara_qtd}', True, Colors.WHITE)
                        self.contagio *= 0.995
                    if self.dp_width // 3 + 367 < event.pos[0] < self.dp_width // 3 + 447:  # Leitos
                        self.leitos_qtd += 500
                        self.leitos_qtd_img = Fonts.FONT30.render(f'Qtd.:{self.leitos_qtd}', True, Colors.WHITE)
                    if self.dp_width / 1.5 + 183 < event.pos[0] < self.dp_width / 1.5 + 263:  # Pessoas
                        self.pessoas_qtd *= 0.95
                        self.pessoas_qtd_img = Fonts.FONT30.render(f'Qtd.:{int(self.pessoas_qtd)}', True, Colors.WHITE)

    def __all_blits(self):
        self.tela.fill((243, 246, 248))
        self.__blit_info()
        self.__blit_botoes()

    def loop(self):
        frames = 0
        self.running = True
        while self.running:
            if frames % 100 == 0:
                self.__day()
                self.__all_blits()
            self.__events_handler()

            pygame.display.update()
            frames += 1

    def lvl1(self):
        self.pais = 'China'
        self.sem_leito = 0.5
        self.com_leito = 0.2
        self.__lvl(1)


Game().lvl1()
