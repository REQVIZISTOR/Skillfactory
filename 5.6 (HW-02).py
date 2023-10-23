# Создаем игровое поле
board = {i+1: ' ' for i in range(9)}

# Функция, которая выводит игровое поле
def print_board():
    row_separator = '-' * 9
    print(f"{board[1]} | {board[2]} | {board[3]}")
    print(row_separator)
    print(f"{board[4]} | {board[5]} | {board[6]}")
    print(row_separator)
    print(f"{board[7]} | {board[8]} | {board[9]}")

# Функция, которая проверяет выигрышные комбинации
def check_win(player):
    winning_positions = [
        [1, 2, 3], [4, 5, 6], [7, 8, 9],    # горизонтальные
        [1, 4, 7], [2, 5, 8], [3, 6, 9],    # вертикальные
        [1, 5, 9], [3, 5, 7]                # диагональные
    ]

    for positions in winning_positions:
        if all(board[p] == player for p in positions):
            return True

    return False

# Функция, которая запускает игру
def play_game():
    current_player = 'X'
    print_board()

    while True:
        # Ход текущего игрока
        position = int(input(f'Ход игрока {current_player}. Введите номер ячейки (от 1 до 9): '))

        # Проверка на корректность введенной позиции
        if position in board and board[position] == ' ':
            board[position] = current_player
        else:
            print('Некорректный ход. Попробуйте снова.')
            continue

        print_board()

        # Проверяем, выиграл ли текущий игрок
        if check_win(current_player):
            print(f'Игрок {current_player} выиграл!')
            break

        # Проверяем, возможен ли еще ход
        if ' ' not in board.values():
            print('Ничья!')
            break

        # Меняем текущего игрока
        current_player = 'O' if current_player == 'X' else 'X'

# Запускаем игру
play_game()