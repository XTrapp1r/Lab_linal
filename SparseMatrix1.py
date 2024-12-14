class SparseMatrix:

    # Задача №1
    
    def __init__(self, rows, cols, data):
        """
        Инициализация матрицы.
        :param rows: Количество строк.
        :param cols: Количество столбцов.
        :param data: Либо список списков (обычная матрица), либо CSR-структура (data, col_indices, row_ptr).
        """
        if not (isinstance(rows, int) and rows > 0 and isinstance(cols, int) and cols > 0):
            raise ValueError("Количество строк и столбцов должно быть положительными целыми числами.")
        
        # Если передана обычная матрица
        if isinstance(data, list) and all(isinstance(row, list) for row in data):
            if not all(len(row) == cols for row in data):
                raise ValueError("Все строки должны иметь одинаковую длину (cols).")

            self.rows = rows
            self.cols = cols
            self.data = []        # Значения ненулевых элементов
            self.col_indices = [] # Индексы столбцов ненулевых элементов
            self.row_ptr = [0]    # Указатели на начало строки в data и col_indices

            for i in range(rows):
                for j in range(cols):
                    if data[i][j] != 0:
                        self.data.append(data[i][j])
                        self.col_indices.append(j)
                self.row_ptr.append(len(self.data))

        # Если передана CSR-структура
        elif isinstance(data, tuple) and len(data) == 3:
            self.data, self.col_indices, self.row_ptr = data
            # Проверка корректности размеров row_ptr для CSR представления
            if len(self.row_ptr) != rows + 1:
                raise ValueError("Некорректная CSR-структура: row_ptr должен содержать rows + 1 элементов.")
            self.rows = rows
            self.cols = cols

        else:
            raise ValueError("data должно быть либо списком списков, либо CSR-структурой.")

    def trace(self):
        """
        Подсчет следа матрицы (сумма элементов на главной диагонали).
        """
        if self.rows != self.cols:
            raise ValueError("След можно считать только для квадратной матрицы.")
        
        trace_sum = 0
        for i in range(self.rows):
            start = self.row_ptr[i]
            end = self.row_ptr[i + 1]
            for k in range(start, end):
                if self.col_indices[k] == i:
                    trace_sum += self.data[k]
        return trace_sum

    def get_element(self, row, col):
        """
        Получение элемента по строке и столбцу (нумерация с 1).
        :param row: Номер строки (с 1).
        :param col: Номер столбца (с 1).
        :return: Значение элемента.
        """
        if not (1 <= row <= self.rows and 1 <= col <= self.cols):
            raise IndexError("Индексы строки или столбца вне допустимого диапазона.")
        
        row -= 1
        col -= 1
        start = self.row_ptr[row]
        end = self.row_ptr[row + 1]
        
        for k in range(start, end):
            if self.col_indices[k] == col:
                return self.data[k]
        return 0
    
    # Задача №2

    def add(self, other):
        """
        Сложение двух матриц.
        :param other: Другая матрица (SparseMatrix).
        :return: Новая матрица (SparseMatrix), результат сложения.
        """
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Матрицы должны иметь одинаковые размеры для сложения.")

        result_data = []
        result_col_indices = []
        result_row_ptr = [0]

        for i in range(self.rows):
            row_a = {self.col_indices[k]: self.data[k] for k in range(self.row_ptr[i], self.row_ptr[i + 1])}
            row_b = {other.col_indices[k]: other.data[k] for k in range(other.row_ptr[i], other.row_ptr[i + 1])}

            # Сложение элементов строк
            row_result = {}
            for col in set(row_a.keys()).union(row_b.keys()):
                row_result[col] = row_a.get(col, 0) + row_b.get(col, 0)
                if row_result[col] != 0:  # Только ненулевые элементы
                    result_data.append(row_result[col])
                    result_col_indices.append(col)

            result_row_ptr.append(len(result_data))

        return SparseMatrix(self.rows, self.cols, (result_data, result_col_indices, result_row_ptr))

    def multiply_scalar(self, scalar: float):
        """
        Умножение матрицы на скаляр.
        :param scalar: Число, на которое умножается матрица.
        :return: Новая матрица (SparseMatrix), результат умножения.
        """
        result_data = []
        result_col_indices = []
        result_row_ptr = [0]

        for i in range(self.rows):
            row_result = {}
            start, end = self.row_ptr[i], self.row_ptr[i + 1]
            for k in range(start, end):
                col = self.col_indices[k]
                value = self.data[k] * scalar
                if value != 0:
                    row_result[col] = value
                    result_data.append(value)
                    result_col_indices.append(col)

            result_row_ptr.append(len(result_data))

        return SparseMatrix(self.rows, self.cols, (result_data, result_col_indices, result_row_ptr))

    def multiply_matrix(self, other):
        """
        Умножение двух разреженных матриц (CSR-формат) и возврат результата в CSR-формате.
        :param other: Другая матрица (SparseMatrix).
        :return: Новая матрица (SparseMatrix), результат умножения.
        """
        if self.cols != other.rows:
            raise ValueError("Число столбцов первой матрицы должно совпадать с числом строк второй.")

        result_data = []
        result_col_indices = []
        result_row_ptr = [0]

        # Пройдем по строкам первой матрицы
        for i in range(self.rows):
            row_result = {}

            # Перебираем элементы строки i в первой матрице
            start_a, end_a = self.row_ptr[i], self.row_ptr[i + 1]
            for k in range(start_a, end_a):
                col_a = self.col_indices[k]  # Столбец из первой матрицы
                val_a = self.data[k]          # Значение из первой матрицы

                # Перебираем элементы столбца col_a во второй матрице
                start_b, end_b = other.row_ptr[col_a], other.row_ptr[col_a + 1]
                for j in range(start_b, end_b):
                    col_b = other.col_indices[j]  # Строка из второй матрицы
                    val_b = other.data[j]         # Значение из второй матрицы

                    # Вычисляем произведение элементов val_a и val_b и добавляем его к элементу, результирующей матрицы в позиции (i, col_b), где col_b - номер столбца результирующей матрицы
                    if col_b not in row_result:
                        row_result[col_b] = 0
                    row_result[col_b] += val_a * val_b

            # Добавляем строку в CSR-формат
            for col in sorted(row_result.keys()):
                if row_result[col] != 0: # Добавляем только ненулевые элементы
                    result_data.append(row_result[col])
                    result_col_indices.append(col)

            result_row_ptr.append(len(result_data)) # Обновляем значение row_ptr для следующей строки

        return SparseMatrix(self.rows, other.cols, (result_data, result_col_indices, result_row_ptr))
    
    # Задача №3

    def determinant(self):
        """
        Вычисляет определитель матрицы в формате CSR.
        :return: Определитель матрицы.
        """
        if self.rows != self.cols:
            raise ValueError("Невозможно вычислить определитель для матрицы, не являющейся квадратной.")
        
        # Базовый случай для 1x1 матрицы
        if self.rows == 1:
            return self.get_element(1, 1)
        
        # Базовый случай для 2x2 матрицы
        if self.rows == 2:
            a = self.get_element(1, 1)
            b = self.get_element(1, 2)
            c = self.get_element(2, 1)
            d = self.get_element(2, 2)
            return a * d - b * c

        # Рекурсивный случай для матрицы размера 3x3 и больше
        det = 0
        # Разложение по первой строке
        for col in range(1, self.cols + 1):
            minor_data = []
            minor_col_indices = []
            minor_row_ptr = [0]
            
            # Создание минора матрицы, исключая первую строку и текущий столбец
            for row in range(2, self.rows + 1):
                start, end = self.row_ptr[row - 1], self.row_ptr[row]
                for k in range(start, end):
                    if self.col_indices[k] != col - 1:
                        minor_data.append(self.data[k])
                        minor_col_indices.append(self.col_indices[k] if self.col_indices[k] < col - 1 else self.col_indices[k] - 1)
                minor_row_ptr.append(len(minor_data))
            
            # Рекурсивное вычисление детерминанта для минора
            cofactor = self.get_element(1, col) * (-1) ** (col + 1) # (-1)^(row + col) - знак минора
            minor_matrix = SparseMatrix(self.rows - 1, self.cols - 1, (minor_data, minor_col_indices, minor_row_ptr))
            det += cofactor * minor_matrix.determinant()
        
        return det

    def is_invertible(self):
        """
        Проверяет, существует ли обратная матрица.
        :return: "да" если матрица обратима, иначе "нет".
        """
        det = self.determinant()
        return "да" if det != 0 else "нет"

# Запуск кода 

if __name__ == "__main__":
    task = int(input("Введите номер задачи: "))

    if task == 1:
        num_rows = int(input("Введите количество строк: "))
        num_cols = int(input("Введите количество столбцов: "))

        matrix = []
        print("Введите элементы матрицы построчно, через пробел:")
        for _ in range(num_rows):
            row = list(map(float, input().split()))
            if len(row) != num_cols:
                raise ValueError("Неверное количество элементов")
            matrix.append(row)

        sparse_matrix = SparseMatrix(num_rows, num_cols, matrix)

        while True:
            print("Что вы хотите сделать с матрицей:")
            print("1. Вывести матрицу")
            print("2. Найти и вывести след матрицы")
            print("3. Найти и вывести элемент матрицы по индексу")
            print("4. Выход")

            choice = int(input("Введите номер действия: "))
            if choice == 1:
                print("Ваша матрица:")
                for row in matrix:
                    print(" ".join(map(str, row)))

            elif choice == 2:
                print("След матрицы:", sparse_matrix.trace())

            elif choice == 3:
                row = int(input("Введите индекс строки: "))
                col = int(input("Введите индекс столбца: "))
                print(sparse_matrix.get_element(row, col))

            elif choice == 4:
                break

            else:
                print("Неверное значение")

    elif task == 2:
        num_rows1 = int(input("Введите количество строк матрицы №1: "))
        num_cols1 = int(input("Введите количество столбцов матрицы №1: "))

        num_rows2 = int(input("Введите количество строк матрицы №2: "))
        num_cols2 = int(input("Введите количество столбцов матрицы №2: "))

        matrix1 = []
        matrix2 = []
        print("Введите элементы матрицы №1 построчно, через пробел:")
        for _ in range(num_rows1):
            row = list(map(float, input().split()))
            if len(row) != num_cols1:
                raise ValueError("Неверное количество элементов")
            matrix1.append(row)

        sparse_matrix1 = SparseMatrix(num_rows1, num_cols1, matrix1)

        print("Введите элементы матрицы №2 построчно, через пробел:")
        for _ in range(num_rows2):
            row = list(map(float, input().split()))
            if len(row) != num_cols2:
                raise ValueError("Неверное количество элементов")
            matrix2.append(row)

        sparse_matrix2 = SparseMatrix(num_rows2, num_cols2, matrix2)

        while True:
            print("Что вы хотите сделать с матрицами")
            print("1. Сложить матрицы")
            print("2. Умножить матрицу на скаляр")
            print("3. Перемножить матрицы")

            choice = int(input("Введите номер действия: "))
            if choice == 1:
                result = sparse_matrix1.add(sparse_matrix2)
                print("Результат сложения матриц:")
                print("Values:", result.data)
                print("Col_index:", result.col_indices)
                print("Row_pointers:", result.row_ptr)
            elif choice == 2:
                scalar = float(input("Введите скаляр: "))
                result = sparse_matrix1.multiply_scalar(scalar)
                print("Результат умножения матрицы на скаляр:")
                print("Values:", result.data)
                print("Col_index:", result.col_indices)
                print("Row_pointers:", result.row_ptr)
            elif choice == 3:
                result = sparse_matrix1.multiply_matrix(sparse_matrix2)
                print("Результат перемножения матриц:")
                print("Values:", result.data)
                print("Col_index:", result.col_indices)
                print("Row_pointers:", result.row_ptr)
            else:
                print("Неверное значение")

    elif task == 3:
        num_rows = int(input("Введите количество строк: "))
        num_cols = int(input("Введите количество столбцов: "))

        matrix = []
        print("Введите элементы матрицы построчно, через пробел:")
        for _ in range(num_rows):
            row = list(map(float, input().split()))
            if len(row) != num_cols:
                raise ValueError("Неверное количество элементов")
            matrix.append(row)

        sparse_matrix = SparseMatrix(num_rows, num_cols, matrix)

        det = sparse_matrix.determinant()
        print(f"Определитель матрицы: {det}")
        if sparse_matrix.is_invertible() == "да":
            print("Обратная матрица: да")
        else:
            print("Обратная матрица: нет")

