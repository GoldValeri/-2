"""
Лабораторная работа № 2. Вариант 6.
Эмпирический анализ временной сложности:
сортировка пузырьком и сортировка вставками.

Дисциплина: Основы алгоритмизации и программирование
Студент: Голдаева Валерия Валентиновна, группа БИ 2-1

Тип данных: D (много повторов, [0; 10])
Размеры: 500, 1000, 2000, 4000
Повторов: 5
Доп. задание М1: подсчёт сравнений и обменов/сдвигов
"""

import random
import statistics
import time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def generate_data(n, kind="duplicates", lo=0, hi=10, seed=42):
    """Генерирует массив длины n заданного типа."""
    rng = random.Random(seed + n)
    data = [rng.randint(lo, hi) for _ in range(n)]
    if kind == "sorted":
        data.sort()
    elif kind == "reversed":
        data.sort(reverse=True)
    elif kind == "nearly_sorted":
        data.sort()
        for _ in range(max(1, n // 20)):
            i, j = rng.randrange(n), rng.randrange(n)
            data[i], data[j] = data[j], data[i]
    # kind == "duplicates" or "random" — уже готово
    return data


def bubble_sort(arr, count_ops=False):
    """Сортировка пузырьком с флагом досрочного выхода.
    Не изменяет исходный массив. Возвращает новый список.
    """
    a = arr.copy()
    n = len(a)
    comparisons = 0
    swaps = 0
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            comparisons += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swaps += 1
                swapped = True
        if not swapped:
            break
    if count_ops:
        return a, comparisons, swaps
    return a


def insertion_sort(arr, count_ops=False):
    """Сортировка вставками.
    Не изменяет исходный массив. Возвращает новый список.
    """
    a = arr.copy()
    comparisons = 0
    shifts = 0
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0:
            comparisons += 1
            if a[j] > key:
                a[j + 1] = a[j]
                shifts += 1
                j -= 1
            else:
                break
        a[j + 1] = key
    if count_ops:
        return a, comparisons, shifts
    return a


def measure(sort_func, data, repeats=5):
    """Медианное время работы sort_func на data (секунды)."""
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        result = sort_func(data)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        assert result == sorted(data), f"{sort_func.__name__}: ошибка сортировки"
    return statistics.median(times)


def main():
    SIZES = [500, 1000, 2000, 4000]
    REPEATS = 5
    KIND = "duplicates"
    LO, HI = 0, 10

    algorithms = {
        "Пузырьком": bubble_sort,
        "Вставками": insertion_sort,
    }
    results_time = {name: [] for name in algorithms}
    results_ops = {name: [] for name in algorithms}

    print("=" * 90)
    print("ЛАБОРАТОРНАЯ РАБОТА № 2 — ВАРИАНТ 6")
    print("Сортировка пузырьком и сортировка вставками")
    print("Тип данных: D (много повторов [0; 10]), k = 5")
    print("=" * 90)

    header = f"{'n':>6}"
    for name in algorithms:
        header += f"{name + ' (с)':>16}"
    header += f"{'Cmp пузыр.':>12}{'Swp пузыр.':>12}{'Cmp встав.':>12}{'Shf встав.':>12}"
    print(header)
    print("-" * 90)

    for n in SIZES:
        data = generate_data(n, kind=KIND, lo=LO, hi=HI)
        row = f"{n:>6}"
        for name, func in algorithms.items():
            t = measure(func, data, REPEATS)
            results_time[name].append(t)
            row += f"{t:>16.6f}"
        # М1: операции
        _, cmp_b, swp_b = bubble_sort(data, count_ops=True)
        _, cmp_i, shf_i = insertion_sort(data, count_ops=True)
        results_ops["Пузырьком"].append((cmp_b, swp_b))
        results_ops["Вставками"].append((cmp_i, shf_i))
        row += f"{cmp_b:>12}{swp_b:>12}{cmp_i:>12}{shf_i:>12}"
        print(row)

    print("\nПроверка квадратичности: T(2n)/T(n)")
    for i in range(len(SIZES) - 1):
        if SIZES[i + 1] == 2 * SIZES[i]:
            for name in algorithms:
                ratio = results_time[name][i + 1] / results_time[name][i]
                print(f"  {name}: {SIZES[i]} → {SIZES[i+1]}: {ratio:.2f} (теория ≈ 4)")

    print("\nОтношение T(n)/n² (должно быть ≈ const):")
    for i, n in enumerate(SIZES):
        for name in algorithms:
            val = results_time[name][i] / (n * n)
            print(f"  n={n}, {name}: {val:.2e}")

    print("\nМ1: сравнения vs теория:")
    for i, n in enumerate(SIZES):
        cmp_b, swp_b = results_ops["Пузырьком"][i]
        cmp_i, shf_i = results_ops["Вставками"][i]
        print(f"  n={n}:")
        print(f"    Пузырёк: cmp={cmp_b} (≈n²/2={n*n//2}), swp={swp_b}")
        print(f"    Вставки: cmp={cmp_i} (≈n²/4={n*n//4}), shf={shf_i}")

    # График
    plt.figure(figsize=(8, 5))
    for name, times in results_time.items():
        marker = "o" if "Пузыр" in name else "s"
        plt.plot(SIZES, times, marker=marker, label=name, linewidth=2)
    plt.xlabel("Размер массива n")
    plt.ylabel("Время, с")
    plt.title("Зависимость времени сортировки от n\n(тип D: много повторов [0; 10])")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("lr2_plot.png", dpi=150)
    print("\nГрафик сохранён: lr2_plot.png")


if __name__ == "__main__":
    main()
