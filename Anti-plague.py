from os import listdir, path
from random import choice
from time import sleep
from threading import Thread
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
    GRAY200 = (200, 200, 200)
    YELLOW = (255, 255, 20)
    ORANGE = (255, 180, 20)


class Fonts:
    FONT18 = pygame.font.SysFont('Agency FB', 18, True)
    FONT30 = pygame.font.SysFont('Agency FB', 30)
    FONT40 = pygame.font.SysFont('Agency FB', 40)
    FONT70 = pygame.font.SysFont('Agency FB', 70)
    FONT80 = pygame.font.SysFont('Agency FB', 80)
    FONT95 = pygame.font.SysFont('Agency FB', 95, True)


class Game:
    def __init__(self):
        # Numeros
        self.dp_height = 768
        self.dp_width = 1366
        self.graph_size = 8 * self.dp_height // 49
        self.info_size = self.dp_width // 3

        # Dicionários de Imagens
        files = self.__get_all_files("./Data", start_string='')
        self.imgs = {file.split('.')[0]: pygame.image.load(f"Data/{file}") for file in files}

        # Constantes Globais
        self.mascara_img = self.imgs["Mascara"]
        self.leito_img = self.imgs["Leito"]
        self.pessoas_img = self.imgs["Pessoas"]

        self.contagio = 0.3
        self.taxa_de_graves = 0.15
        self.taxa_de_morte = [0.2, 0.2]

        self.pais = None
        self.sem_leito = 0.5
        self.com_leito = 0.2

        self.running = False
        self.quit = False
        self.loading = False
        self.mouse_press = False

        # Criação da Tela
        self.tela: pygame.Surface = pygame.display.set_mode((self.dp_width, self.dp_height))
        pygame.display.set_caption("Anti-Plague Simulator", "Ícone")
        pygame.display.set_icon(self.imgs['Virus'])

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

    # Blits
    def __blit_info(self, move_points):
        if move_points:
            self.tela.blit(pygame.transform.scale(self.main_img, (self.dp_width - self.info_size, self.dp_height)),
                           (self.info_size, 0))
            self.__pontos(self.saudaveis[-1] - self.imunes[-1], self.imgs["Pontos/Green"])
            self.__pontos(self.infectados[-1], self.imgs["Pontos/Red"])
            self.__pontos(self.imunes[-1], self.imgs["Pontos/Blue"])

        self.tela.blit(pygame.transform.scale(self.fundo_img, (self.dp_width - self.info_size, self.dp_height)),
                       (self.info_size, 0))
        self.tela.blit(self.pais_img, (self.info_size + 100, 50))

        pygame.draw.rect(self.tela, Colors.GRAY100, ((0, 0), (self.info_size, self.dp_height)))
        titulos = ('Nº Saudáveis: ' + str(int(self.saudaveis[-1])), 'Nº Infectados: ' + str(int(self.infectados[-1])),
                   'Nº Mortos: ' + str(int(self.mortos[-1])), 'Nº Imunes: ' + str(int(self.imunes[-1])),
                   'Geral: ', 'Taxa de Morte')
        titulo_img = [Fonts.FONT18.render(ttl, True, Colors.WHITE) for ttl in titulos]

        for i in range(6):
            pt1 = (int(self.info_size * 0.1), ((8 * self.dp_height * i) + self.dp_height) // 49)
            pygame.draw.rect(self.tela, Colors.GRAY50, (pt1, (int(self.info_size * 0.8), self.dp_height // 7)))
            pygame.draw.rect(self.tela, Colors.BLACK, (pt1, (int(self.info_size * 0.8), self.dp_height // 40)))
            self.tela.blit(titulo_img[i],
                           (int(self.info_size * 0.11), ((8 * self.dp_height * i) + self.dp_height) // 49))

        saudaveis_img = Fonts.FONT95.render('{:.1f}'.format(self.saudaveis[-1] / 10000) + '%', True, Colors.WHITE)
        self.__blit_grafico(self.saudaveis, 0, Colors.GREEN, saudaveis_img, True)

        infectados_img = Fonts.FONT95.render('{:.1f}'.format(self.infectados[-1] / 10000) + '%', True, Colors.WHITE)
        self.__blit_grafico(self.infectados, 1 * self.graph_size, Colors.RED, infectados_img, True)

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
        img = pygame.transform.scale(self.imgs[f'Speed/{(self.speed+1)%3}'], (50, 50))
        self.tela.blit(img, (self.dp_width - 50, 0))
        self.tela.blit(Fonts.FONT40.render(f"Dia {365-self.dias}", True, (0, 0, 0)), (self.dp_width - 150, 0))

        options = [[self.mascara_img, self.mascara_price_img, self.mascara_qtd_img, 550],
                   [self.leito_img, self.leitos_price_img, self.leitos_qtd_img, self.dp_width // 3 + 367],
                   [self.pessoas_img, self.pessoas_price_img, self.pessoas_qtd_img, self.dp_width // 1.5 + 183]]
        for i in range(3):
            icon_bt, price, qtd, pos_x = options[i]

            pygame.draw.rect(self.tela, Colors.GREEN, ((int(pos_x), self.dp_height - 130), (80, 80)))
            self.tela.blit(icon_bt, (int(pos_x) + 10, self.dp_height - 120))
            self.tela.blit(price, (int(pos_x) + 90, self.dp_height - 130))
            pygame.draw.rect(self.tela, Colors.BLACK, ((int(pos_x) + 90, self.dp_height - 80), (150, 30)))
            self.tela.blit(qtd, (int(pos_x) + 93, self.dp_height - 83))

    def __transparente(self):
        img = cv2.imread(f"Data/{self.pais}/Fundo.png")
        height = len(img)
        width = len(img[0])
        self.transparente = []
        for x in range(width):
            for y in range(height):
                if img[y][x][0] == img[y][x][1] == img[y][x][2] == 0:
                    new_x = (self.dp_width - self.info_size) * x // width
                    new_y = self.dp_height * y // height
                    self.transparente.append((new_x, new_y))

    def __pontos(self, qtd, img):
        for _ in range(int(qtd * len(self.transparente) / 100000000)):
            x, y = choice(self.transparente)
            self.tela.blit(pygame.transform.scale(img, (8, 8)), (x + self.info_size, y))

    # Gráficos
    def __grafico_geral(self, values, cor):
        coords = list()
        height = (4 * self.dp_height / 35) / 1000000
        width = self.info_size * 0.8 / (len(values) - 1)

        for index, b in enumerate(values):
            coords.append((int(self.info_size * 0.1 + width * index), int(5 * self.graph_size - height * int(b))))

        pygame.draw.lines(self.tela, cor, False, coords, 3)

    def __blit_grafico(self, values, altura, cor, numero, inteiro=False):
        altura += self.graph_size
        coords = [(int(self.info_size*0.9), altura), (int(self.info_size*0.1), altura)]
        height = (4 * self.dp_height / 35) / max(values) if max(values) else (4 * self.dp_height / 35)
        width = self.info_size*0.8 / (len(values) - 1)

        for index, b in enumerate(values):
            if inteiro:
                b = int(b)
            coords.append((int(self.info_size*0.1 + width * index), int(altura - height * b)))

        pygame.draw.polygon(self.tela, cor, coords)
        self.tela.blit(numero, (int(self.info_size*0.3), altura - self.graph_size + self.dp_height // 30))

    # Principais
    def __carregamento(self):
        def transform(image, topleft, angle):
            rotated_image = pygame.transform.rotate(image, angle)
            new_rect = rotated_image.get_rect(center=image.get_rect(topleft=topleft).center)

            return rotated_image, new_rect.topleft

        text = "Carregando "
        rotation = 0
        virus_img = self.imgs["Virus"]
        frames = 0
        while self.loading:
            if frames % 10 == 0:
                if text.count('.') < 3:
                    text += '.'
                else:
                    text = text[:-3]
            rotation -= 3

            text_img = Fonts.FONT80.render(text, True, (0, 0, 0))
            x = self.dp_width // 2 - 50
            y = self.dp_height // 2
            self.tela.fill((255, 255, 255))
            self.tela.blit(*transform(virus_img, (x - 100, y - 100), rotation))
            self.tela.blit(text_img, (x, y - 100))

            pygame.display.update()
            frames += 1
            sleep(0.03)

    def __lvl(self, price_multiplier):
        self.mascara_price = 200 * price_multiplier
        self.leitos_price = 300 * price_multiplier
        self.pessoas_price = 150 * price_multiplier
        self.mascara_qtd = 0
        self.leitos_qtd = 1000
        self.pessoas_qtd = 1000000
        self.saudaveis = [999999, 999999]
        self.infectados = [20, 20]
        self.mortos = [0, 0]
        self.imunes = [0, 0]
        self.novos_infectados = list()
        self.novos_mortos = 0
        self.dias = 365
        self.speed = 1
        self.money = 5000

        self.main_img = self.imgs[f"{self.pais}/Main"]
        self.fundo_img = self.imgs[f"{self.pais}/Fundo"]
        self.loading = True
        Thread(target=self.__carregamento).start()
        self.__transparente()

        self.mascara_price_img = Fonts.FONT40.render(f'R${self.mascara_price}', True, (0, 0, 0))
        self.leitos_price_img = Fonts.FONT40.render(f'R${self.leitos_price}', True, (0, 0, 0))
        self.pessoas_price_img = Fonts.FONT40.render(f'R${self.pessoas_price}', True, (0, 0, 0))

        self.mascara_qtd_img = Fonts.FONT30.render(f'Qtd.:{self.mascara_qtd}', True, Colors.WHITE)
        self.leitos_qtd_img = Fonts.FONT30.render(f'Qtd.:{self.leitos_qtd}', True, Colors.WHITE)
        self.pessoas_qtd_img = Fonts.FONT30.render(f'Qtd.:{self.pessoas_qtd}', True, Colors.WHITE)

        self.pais_img = Fonts.FONT80.render(self.pais, True, (0, 0, 0))

        self.__loop()

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

        self.dias -= 1
        self.__all_blits()

    def __events_handler(self, frames):
        get = pygame.event.get()
        for event in get:
            if event.type == pygame.QUIT:
                self.running = False
                self.quit = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.pos[0] > self.dp_width - 50 and event.pos[1] < 50:
                    self.speed = (self.speed + 1) % 3
                    self.__all_blits(False)
                else:
                    self.mouse_press = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_press = False
        if type(self.mouse_press) == tuple and frames % 5 == 0:
            if self.dp_height - 130 < self.mouse_press[1] < self.dp_height - 50:
                if 550 < self.mouse_press[0] < 630:  # Mascaras
                    self.mascara_qtd += 2000
                    self.mascara_qtd_img = Fonts.FONT30.render(f'Qtd.:{self.mascara_qtd}', True, Colors.WHITE)
                    self.contagio *= 0.995
                    self.money -= self.mascara_price
                elif self.dp_width // 3 + 367 < self.mouse_press[0] < self.dp_width // 3 + 447:  # Leitos
                    self.leitos_qtd += 500
                    self.leitos_qtd_img = Fonts.FONT30.render(f'Qtd.:{self.leitos_qtd}', True, Colors.WHITE)
                    self.money -= self.leitos_price
                elif self.dp_width / 1.5 + 183 < self.mouse_press[0] < self.dp_width / 1.5 + 263:  # Pessoas
                    self.pessoas_qtd *= 0.95
                    self.pessoas_qtd_img = Fonts.FONT30.render(f'Qtd.:{int(self.pessoas_qtd)}', True, Colors.WHITE)
                    self.money -= self.pessoas_price
            self.__all_blits(False)
        return get

    def __all_blits(self, move_points=True):
        self.__blit_info(move_points)
        self.__blit_botoes()

    def __loop(self):
        frames = 0
        self.loading = False
        self.running = True
        while self.running:
            if self.dias == 0:
                self.running = False
            if self.speed:
                if frames % (10 / self.speed) == 0:
                    self.__day()
            self.__events_handler(frames)

            pygame.display.update()
            sleep(0.01)
            frames += 1

    # Niveis
    def lvl1(self):
        self.pais = 'China'
        self.sem_leito = 0.5
        self.com_leito = 0.2
        self.__lvl(1)

    def lvl2(self):
        self.pais = 'Italia'
        self.sem_leito = 0.8
        self.com_leito = 0.4
        self.__lvl(1)

    def lvl3(self):
        self.pais = 'EUA'
        self.sem_leito = 0.8
        self.com_leito = 0.4
        self.__lvl(2)

    def tutorial(self):
        lista = [
            "Saudaveis",
            "Infectados",
            "Mortos",
            "Imunes",
            "Geral",
            "Taxa de Morte",
        ]
        for nome in lista:
            image = self.imgs[f"Tutorial/{nome}"]
            self.tela.blit(pygame.transform.scale(image, (self.dp_width, self.dp_height)), (0, 0))
            pygame.display.update()
            click = False
            while not click:
                for event in self.__events_handler(1):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        click = True
                        break
                if not self.running:
                    return

    def credits(self):
        self.tela.fill((0, 0, 0))
        text = """
        Design: Alauan Travain
        Programação: Rafael Setton e Alauan Travain
        """

        img = Fonts.FONT95.render("Anti-Plague Simulator", True, Colors.WHITE)
        self.tela.blit(img, ((self.dp_width - img.get_width()) // 2, 10))

        for ind, line in enumerate(text.split('\n')):
            img = Fonts.FONT70.render(line, True, Colors.GRAY100)
            self.tela.blit(img, ((self.dp_width-img.get_width())//2, (img.get_height()+25)*(ind+1)))
        pygame.display.update()

        click = False
        self.running = True
        while self.running and not click:
            for event in self.__events_handler(1):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    click = True

    def main_menu(self):
        def blit():
            def rect(color, text, position):
                pygame.draw.rect(self.tela, color,
                                 (position, (self.dp_width // 2, self.dp_height // 2)))
                text = Fonts.FONT95.render(text, True, Colors.WHITE)
                position = [position[0] + self.dp_width // 4 - text.get_width() // 2,
                            position[1] + self.dp_height // 4 - text.get_height() // 2]
                self.tela.blit(text, position)

            rect(Colors.GREEN, "Tutorial", (0, 0))
            rect(Colors.BLUE, "Nível 1 (China)", (self.dp_width // 2, 0))
            rect(Colors.ORANGE, "Nível 2 (Itália)", (0, self.dp_height // 2))
            rect(Colors.RED, "Nível 3 (EUA)", (self.dp_width // 2, self.dp_height // 2))
            pygame.draw.rect(self.tela, Colors.BLACK, ((self.dp_width//2-80, self.dp_height//2-45), (160, 90)))
            creds = Fonts.FONT40.render("Créditos", True, Colors.WHITE)
            self.tela.blit(creds, ((self.dp_width-creds.get_width())//2, (self.dp_height-creds.get_height())//2))

            credits_img = Fonts.FONT30.render("Créditos: Alauan Travain e Rafael Setton", True, Colors.BLACK)
            pos = (self.dp_width-credits_img.get_width()-8, self.dp_height-credits_img.get_height())
            self.tela.blit(credits_img, pos)

            pygame.display.update()

        blit()
        lvls = [[self.tutorial, self.lvl1], [self.lvl2, self.lvl3]]
        self.quit = False
        while not self.quit:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if abs(event.pos[0]-self.dp_width//2) <= 80 and abs(event.pos[1]-self.dp_height//2) <= 45:
                        self.credits()
                    else:
                        lvls[event.pos[1]//(self.dp_height//2)][event.pos[0]//(self.dp_width//2)]()
                    blit()
                elif event.type == pygame.QUIT:
                    self.quit = True


if __name__ == '__main__':
    Game().main_menu()
