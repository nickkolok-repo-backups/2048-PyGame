# -*-coding: utf-8-*-
import os
import sys
from random import *
import pygame
from pygame import *

# Логика игры
class Game2048:
	def __init__(self):
		pass

	# Заполняет матрицу 4x4 нулями
	def newGame(self):
		matrix = []
		for i in range(4):
			matrix.append([0] * 4)
		return matrix
	
	# Создаёт новую плитку
	def addTile(self, matrix):
		x = randint(0, len(matrix) - 1)
		y = randint(0, len(matrix) - 1)
		while matrix[x][y]:
			x = randint(0, len(matrix) - 1)
			y = randint(0, len(matrix) - 1)
		matrix[x][y] = 2 if random() < 0.9 else 4
		return matrix
	
	# Создаём начальную матрицу
	def createMatrix(self):
		global gMatrix
		global gScore
		gScore = 0
		gMatrix = self.newGame()
		gMatrix = self.addTile(gMatrix)
		gMatrix = self.addTile(gMatrix)
	
	# "Состояние" игры
	def gameStatus(self, matrix):
		# Проверка на плитку 2048
		for x in range(len(matrix)):
			for y in range(len(matrix[0])):
				if matrix[x][y] == 2048:
					return 'win'
		# Проверка на одинаковые соседние элементы
		for x in range(len(matrix) - 1):
			for y in range(len(matrix[0]) - 1):
				if matrix[x][y] == matrix[x + 1][y] or matrix[x][y + 1] == matrix[x][y]:
					return 'continue'
		# Проверка на наличие 0
		for x in range(len(matrix)):
			for y in range(len(matrix[0])):
				if matrix[x][y] == 0:
					return 'continue'
		# Проверка на одинаковые элементы в последней строке
		for x in range(len(matrix) - 1):
			if matrix[len(matrix) - 1][x] == matrix[len(matrix) - 1][x + 1]:
				return 'continue'
		# Проверка на одинаковые элементы в последнем столбце
		for j in range(len(matrix) - 1):
			if matrix[j][len(matrix) - 1] == matrix[j + 1][len(matrix) - 1]:
				return 'continue'
		return 'lose'
	
	# Действия с матрицами
	# --------------------
	def reverse(self, matrix):
		newMatrix = []
		for x in range(len(matrix)):
			newMatrix.append([])
			for y in range(len(matrix[0])):
				newMatrix[x].append(matrix[x][len(matrix[0]) - y - 1])
		return newMatrix
	
	def transpose(self, matrix):
		newMatrix = []
		for x in range(len(matrix[0])):
			newMatrix.append([])
			for y in range(len(matrix)):
				newMatrix[x].append(matrix[y][x])
		return newMatrix
	
	def coverUp(self, matrix):
		newMatrix = self.newGame()
		isDone = False
		for x in range(4):
			count = 0
			for y in range(4):
				if matrix[x][y]:
					newMatrix[x][count] = matrix[x][y]
					if (y != count):
						isDone = True
					count += 1
		return (newMatrix, isDone)
	
	def merge(self, matrix):
		global gScore
		isDone = False
		for x in range(4):
			for y in range(3):
				if (matrix[x][y] == matrix[x][y + 1]) and matrix[x][y]:
					matrix[x][y] *= 2
					# Обновляем счёт
					gScore += matrix[x][y]
					matrix[x][y + 1] = 0
					isDone = True
		return (matrix, isDone)
	# --------------------
	
	# Меняет матрицу, при нажатии "Вверх"
	def up(self, matrix):
		matrix = self.transpose(matrix)
		matrix, isDone = self.coverUp(matrix)
		temp = self.merge(matrix)
		matrix = temp[0]
		isDone = isDone or temp[1]
		matrix = self.coverUp(matrix)[0]
		matrix = self.transpose(matrix)
		return (matrix, isDone)
	
	# Меняет матрицу, при нажатии "Вниз"
	def down(self, matrix):
		matrix = self.reverse(self.transpose(matrix))
		matrix, isDone = self.coverUp(matrix)
		temp = self.merge(matrix)
		matrix = temp[0]
		isDone = isDone or temp[1]
		matrix = self.coverUp(matrix)[0]
		matrix = self.transpose(self.reverse(matrix))
		return (matrix, isDone)
	
		# Меняет матрицу, при нажатии "Влево"
	def left(self, matrix):
		matrix, isDone = self.coverUp(matrix)
		temp = self.merge(matrix)
		matrix = temp[0]
		isDone = isDone or temp[1]
		matrix = self.coverUp(matrix)[0]
		return (matrix, isDone)
	
	# Меняет матрицу, при нажатии "Вправо"
	def right(self, matrix):
		matrix = self.reverse(matrix)
		matrix, isDone = self.coverUp(matrix)
		temp = self.merge(matrix)
		matrix = temp[0]
		isDone = isDone or temp[1]
		matrix = self.coverUp(matrix)[0]
		matrix = self.reverse(matrix)
		return (matrix, isDone)

# Всё, что касается вывода на экран и управления
class GameWindow:
	BACKGROUND_COLOR = "#92877d"
	CELL_EMPTY_COLOR = "#9e948a"
	BG_COLORS = {2:"#eee4da", 4:"#ede0c8", 8:"#f2b179", 16:"#f59563", \
				32:"#f67c5f", 64:"#f65e3b", 128:"#edcf72", 256:"#edcc61", \
				512:"#edc850", 1024:"#edc53f", 2048:"#edc22e"}
	FG_COLORS = {2:"#776e65", 4:"#776e65", 8:"#f9f6f2", 16:"#f9f6f2", \
				32:"#f9f6f2", 64:"#f9f6f2", 128:"#f9f6f2", 256:"#f9f6f2", \
				512:"#f9f6f2", 1024:"#f9f6f2", 2048:"#f9f6f2"}
	
	def __init__(self, width, height, caption):
		self.width = width
		self.height = height
		self.caption = caption
		self.components = []

	# Для рисования клеток, т.к PyGame из коробки не умеет скруглять края у прямоугольников
	def roundedRect(self, surface, rect, color, radius = 0.4):
		rect = Rect(rect)
		color = Color(*color)
		alpha = color.a
		color.a = 0
		pos = rect.topleft
		rect.topleft = 0,0
		rectangle = Surface(rect.size, SRCALPHA)
		circle = Surface([min(rect.size) * 3] * 2, SRCALPHA)
		draw.ellipse(circle, (0, 0, 0), circle.get_rect(), 0)
		circle = transform.smoothscale(circle, [int(min(rect.size)*radius)] * 2)
		radius = rectangle.blit(circle, (0, 0))
		radius.bottomright = rect.bottomright
		rectangle.blit(circle, radius)
		radius.topright = rect.topright
		rectangle.blit(circle, radius)
		radius.bottomleft = rect.bottomleft
		rectangle.blit(circle, radius)
		rectangle.fill((0, 0, 0), rect.inflate(-radius.w, 0))
		rectangle.fill((0, 0, 0), rect.inflate(0, -radius.h))
		rectangle.fill(color, special_flags = BLEND_RGBA_MAX)
		rectangle.fill((255, 255, 255, alpha), special_flags = BLEND_RGBA_MIN)
		return surface.blit(rectangle, pos)

	# Рисует пустую клетку
	def addEmptyCell(self, y, x):
		cells = Surface((128, 128))
		cells.fill(Color(self.BACKGROUND_COLOR))
		self.roundedRect(cells, (0, 0, 128, 128), Color(self.CELL_EMPTY_COLOR), 0.1)
		self.add(cells, 128 * x + 10 * (x + 1), 128 * y + 10 * (y + 1))

	# Рисует клетку со значением
	def addCell(self, y, x, cellText, bgColor, fgColor):
		cells = Surface((128, 128))
		cells.fill(Color(self.BACKGROUND_COLOR))
		self.roundedRect(cells, (0, 0, 128, 128), Color(bgColor), 0.1)
		
		font = pygame.font.Font(None, 64)
		text = font.render(cellText, 1, Color(fgColor))
		textPos = text.get_rect()
		textPos.centerx = cells.get_rect().centerx
		textPos.centery = cells.get_rect().centery
		cells.blit(text, textPos)

		self.add(cells, 128 * x + 10 * (x + 1), 128 * y + 10 * (y + 1))

	# Интерфейс окна
	def gameInterface(self):

		# Поле с клетками
		gameField = Surface((self.width, self.height))
		gameField.fill(Color(self.BACKGROUND_COLOR))

		self.add(gameField, 0, 0)

		# Фон для плиток
		x = y = 0
		while (y < 4):
			self.addEmptyCell(x, y)
			x += 1
			if (x == 4):
				x = 0
				y += 1

	# Показ результата
	def showResult(self, resText):
		pygame.display.set_caption(resText)
		loseScreen = Surface((self.width, self.height))
		loseScreen.fill(Color(self.BACKGROUND_COLOR))
		font = pygame.font.Font(None, 128)
		text = font.render(resText, 1, Color("#ede0c8"))
		textPos = text.get_rect()
		textPos.centerx = loseScreen.get_rect().centerx
		textPos.centery = loseScreen.get_rect().centery
		loseScreen.blit(text, textPos)
		self.add(loseScreen, 0, 0)

	# Перерисовка поля
	def redraw(self):
		global gMatrix
		for x in range(4):
			for y in range(4):
				value = gMatrix[x][y]
				if (value == 0):
					self.addEmptyCell(x, y)
				else:
					self.addCell(x, y, str(value), self.BG_COLORS[value], self.FG_COLORS[value])

	# Нажатие на кнопку
	def keyDown(self, key):
		global gMatrix
		global gScore
		if (key == K_UP):
			gMatrix, isDone = Game2048().up(gMatrix)
		elif (key == K_DOWN):
			gMatrix, isDone = Game2048().down(gMatrix)
		elif (key == K_LEFT):
			gMatrix, isDone = Game2048().left(gMatrix)
		elif (key == K_RIGHT):
			gMatrix, isDone = Game2048().right(gMatrix)
		else:
			return
		if isDone:
			gMatrix = Game2048().addTile(gMatrix)
			self.redraw()
			# Выводим счёт
			pygame.display.set_caption("Счёт: " + str(gScore))
			isDone = False
		if Game2048().gameStatus(gMatrix) == "win":
			self.showResult("You Won!")
		if Game2048().gameStatus(gMatrix) == "lose":
			self.showResult("You Lose!")
			

	# Добавление компонента в окно
	def add(self, surface, x, y):
		self.components.append([surface, x, y])

	# Запуск
	def run(self):
		os.environ['SDL_VIDEO_CENTERED'] = '1' # Центрируем при запуске
		pygame.init()
		screen = pygame.display.set_mode((self.width, self.height))
		pygame.display.set_caption(self.caption)
		pygame.mouse.set_visible(True)

		game = Game2048()
		game.createMatrix()
		
		self.gameInterface()
		self.redraw()

		while 1:
			for e in pygame.event.get():
				# Обработка нажатий клавиш
				if e.type == KEYDOWN:
					self.keyDown(e.key)
				
				# При нажатии на "Закрыть"
				if e.type == QUIT:
					pygame.quit()
					sys.exit()
			
			# Отрисовка всех элементов
			for i in self.components:
				screen.blit(i[0], (i[1], i[2]))
			
			pygame.display.update()

if __name__ == "__main__":
	gw = GameWindow(562, 562, "2048")
	gw.run()