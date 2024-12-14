import unittest
from SparseMatrix1 import SparseMatrix

class TestSparseMatrixCSR(unittest.TestCase):

#Тесты для задачи №1

    def test_trace_square_matrix(self):
        data = [[1, 0, 0], [0, 2, 0], [0, 0, 3]]
        sm = SparseMatrix(3, 3, data)
        self.assertEqual(sm.trace(), 6)

    def test_trace_zero_matrix(self):
        data = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        sm = SparseMatrix(3, 3, data)
        self.assertEqual(sm.trace(), 0)

    def test_trace_non_square_matrix(self):
        data = [[1, 2, 3], [4, 5, 6]]
        sm = SparseMatrix(2, 3, data)
        with self.assertRaises(ValueError):
            sm.trace()

    def test_get_element_valid_indices(self):
        data = [[1, 2], [3, 4]]
        sm = SparseMatrix(2, 2, data)
        self.assertEqual(sm.get_element(1, 1), 1)
        self.assertEqual(sm.get_element(2, 2), 4)
        self.assertEqual(sm.get_element(1, 2), 2)
        self.assertEqual(sm.get_element(2, 1), 3)

    def test_get_element_zero_element(self):
        data = [[1, 0], [0, 4]]
        sm = SparseMatrix(2, 2, data)
        self.assertEqual(sm.get_element(1, 2), 0)
        self.assertEqual(sm.get_element(2, 1), 0)


    def test_get_element_invalid_indices(self):
        data = [[1, 2], [3, 4]]
        sm = SparseMatrix(2, 2, data)
        with self.assertRaises(IndexError):
            sm.get_element(0, 0)  # Индексы вне диапазона
        with self.assertRaises(IndexError):
            sm.get_element(3, 3)  # Индексы вне диапазона

    def test_large_sparse_matrix(self):  # Добавлен тест для большой разреженной матрицы
        rows = 100
        cols = 100
        data = [[0] * cols for _ in range(rows)]
        data[0][0] = 1
        data[50][50] = 2
        data[99][99] = 3
        sm = SparseMatrix(rows, cols, data)
        self.assertEqual(sm.trace(), 6)
        self.assertEqual(sm.get_element(1, 1), 1)
        self.assertEqual(sm.get_element(51, 51), 2)
        self.assertEqual(sm.get_element(100, 100), 3)
        self.assertEqual(sm.get_element(2, 2), 0)

    def test_empty_matrix(self):
        data = []
        with self.assertRaises(ValueError):  # Ожидается ошибка, так как data пустой
            sm = SparseMatrix(0, 0, data)

    def test_inconsistent_dimensions(self):
        data = [[1, 2], [3, 4, 5]]  # Неправильные размерности
        with self.assertRaises(ValueError):
            sm = SparseMatrix(2, 2, data)
    
#Тесты для задачи №2

    def test_add_matrices(self):
        data1 = [[1, 0, 0], [0, 2, 0], [0, 0, 3]]
        data2 = [[0, 1, 0], [3, 0, 4], [0, 0, 0]]
        sm1 = SparseMatrix(3, 3, data1)
        sm2 = SparseMatrix(3, 3, data2)
        
        sm_sum = sm1.add(sm2)
        expected_sum = SparseMatrix(3, 3, [[1, 1, 0], [3, 2, 4], [0, 0, 3]]) # Ожидаемый результат
        self.assertEqual(sm_sum.data, expected_sum.data)
        self.assertEqual(sm_sum.col_indices, expected_sum.col_indices)
        self.assertEqual(sm_sum.row_ptr, expected_sum.row_ptr)

    
    def multiply_scalar(self, scalar: float):
        result_data = []
        result_col_indices = []
        result_row_ptr = [0]
        for i in range(self.rows):
            for k in range(self.row_ptr[i], self.row_ptr[i + 1]):
                result_data.append(self.data[k] * scalar)
                result_col_indices.append(self.col_indices[k])
            result_row_ptr.append(len(result_data))
        return SparseMatrix(self.rows, self.cols, (result_data, result_col_indices, result_row_ptr))


    def test_multiply_matrices(self):
        # Умножение двух матриц
        data1 = [[1, 0, 2], [0, 3, 0]]
        data2 = [[0, 1], [4, 0], [5, 0]]
        sm1 = SparseMatrix(2, 3, data1)
        sm2 = SparseMatrix(3, 2, data2)
        
        sm_mult = sm1.multiply_matrix(sm2)
        self.assertEqual(sm_mult.data, [10, 1, 12])
        self.assertEqual(sm_mult.col_indices, [0, 1, 0])  # Исправлено
        self.assertEqual(sm_mult.row_ptr, [0, 2, 3])

        # Невозможно умножить матрицы (несоответствие размеров)
        data3 = [[1, 2], [3, 4]]
        sm3 = SparseMatrix(2, 2, data3)
        with self.assertRaises(ValueError):
            sm1.multiply_matrix(sm3)

    
    def test_edge_cases(self):
        # Одноэлементные матрицы
        sm1 = SparseMatrix(1, 1, [[5]])
        sm2 = SparseMatrix(1, 1, [[3]])
        
        sm_sum = sm1.add(sm2)
        self.assertEqual(sm_sum.data, [8])
        self.assertEqual(sm_sum.col_indices, [0])
        self.assertEqual(sm_sum.row_ptr, [0, 1])

        sm_scaled = sm1.multiply_scalar(2)
        self.assertEqual(sm_scaled.data, [10])
        self.assertEqual(sm_scaled.col_indices, [0])
        self.assertEqual(sm_scaled.row_ptr, [0, 1])
        
        sm_mult = sm1.multiply_matrix(sm2)
        self.assertEqual(sm_mult.data, [15])
        self.assertEqual(sm_mult.col_indices, [0])
        self.assertEqual(sm_mult.row_ptr, [0, 1])

        # Нулевые матрицы
        sm_zero1 = SparseMatrix(2, 2, [[0, 0], [0, 0]])
        sm_zero2 = SparseMatrix(2, 2, [[0, 0], [0, 0]])
        sm_sum_zero = sm_zero1.add(sm_zero2)
        self.assertEqual(sm_sum_zero.data, [])
        self.assertEqual(sm_sum_zero.col_indices, [])
        self.assertEqual(sm_sum_zero.row_ptr, [0, 0, 0])

# Тесты для задачи №3

    def test_determinant_3x3(self):
        data = [[2, 0, 0], [0, 3, 0], [0, 0, 1]]
        sm = SparseMatrix(3, 3, data)
        self.assertEqual(sm.determinant(), 6)

    def test_determinant_3x3_2(self):  # more complex 3x3
        data = [[1, 2, 3], [0, 4, 5], [1, 0, 6]]
        sm = SparseMatrix(3, 3, data)
        self.assertEqual(sm.determinant(), 22)

    def test_determinant_4x4(self):
        data = [[1, 0, 0, 0], [0, 2, 0, 0], [0, 0, 3, 0], [0, 0, 0, 4]]
        sm = SparseMatrix(4, 4, data)
        self.assertEqual(sm.determinant(), 24)

    def test_determinant_singular_matrix(self):
        data = [[1, 2], [2, 4]]
        sm = SparseMatrix(2, 2, data)
        self.assertEqual(sm.determinant(), 0)

    def test_is_invertible_true(self):
        data = [[1, 0], [0, 1]]
        sm = SparseMatrix(2, 2, data)
        self.assertEqual(sm.is_invertible(), "да")

    def test_is_invertible_false(self):
        data = [[1, 2], [2, 4]]  # Сингулярная матрица ( вырожденная )
        sm = SparseMatrix(2, 2, data)
        self.assertEqual(sm.is_invertible(), "нет")

    def test_determinant_non_square(self):
        data = [[1, 2, 3], [4, 5, 6]]
        sm = SparseMatrix(2, 3, data)
        with self.assertRaises(ValueError):
            sm.determinant()


