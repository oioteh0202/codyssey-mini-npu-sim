import json
import time

EPSILON = 1e-9

# 라벨 통일
def normalize_label(value):
    text = str(value).strip().lower()

    if text in ("+", "cross"):
        return "Cross"
    if text == "x":
        return "X"
    return None

# case_id에서 행렬 크기 추출
def extract_size_from_case_id(case_id):
    parts = str(case_id).split("_")

    if len(parts) < 3:
        return None
    if parts[0] != "size":
        return None

    try:
        return int(parts[1])
    except ValueError:
        return None

# 정상 행렬 검증
def validate_matrix(matrix, expected_size=None):
    if not isinstance(matrix, list) or len(matrix) == 0:
        return False, "행렬이 비어 있거나 리스트 형식이 아닙니다."

    row_count = len(matrix)

    if expected_size is not None and row_count != expected_size:
        return False, f"행 수 불일치: expected={expected_size}, actual={row_count}"

    for row in matrix:
        if not isinstance(row, list):
            return False, "행렬의 각 행은 리스트여야 합니다."

    for row in matrix:
        expected_cols = expected_size if expected_size is not None else row_count
        if len(row) != expected_cols:
            return False, f"열 수 불일치: expected={expected_cols}, actual={len(row)}"

    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            if not isinstance(value, (int, float)):
                return False, f"숫자 아님: ({i}, {j}) = {value}"

    return True, ""

# MAC 점수 계산
def mac_score(pattern, filt):
    total = 0.0
    n = len(pattern)

    for i in range(n):
        for j in range(n):
            total += pattern[i][j] * filt[i][j]

    return total

# Cross 점수와 X 점수를 비교, 최종 라벨 결정
def decide_label(score_cross, score_x, epsilon=EPSILON):
    if abs(score_cross - score_x) < epsilon:
        return "UNDECIDED"
    if score_cross > score_x:
        return "Cross"
    return "X"

# MAC 함수만 반복 측정, 평균 실행 시간 ms 단위로 계산
def measure_average_ms(pattern, filt, repeat=10):
    total_ms = 0.0

    for _ in range(repeat):
        start = time.perf_counter()
        _ = mac_score(pattern, filt)
        end = time.perf_counter()
        total_ms += (end - start) * 1000

    return total_ms / repeat

# 행렬 만들기 함수들
# cross, x로 기준 패턴 생성 / read_matrix_from_console()로 사용자 입력받기

# Cross 형태 기본 패턴 행렬 만들기
def build_cross_pattern(n):
    matrix = []
    mid = n // 2

    for i in range(n):
        row = []
        for j in range(n):
            if i == mid or j == mid:
                row.append(1.0)
            else:
                row.append(0.0)
        matrix.append(row)

    return matrix

# X 형태 기본 패턴 행렬 만들기
def build_x_pattern(n):
    matrix = []

    for i in range(n):
        row = []
        for j in range(n):
            if i == j or i + j == n - 1:
                row.append(1.0)
            else:
                row.append(0.0)
        matrix.append(row)

    return matrix

# 행렬 한 줄씩 입력받기
def read_matrix_from_console(n, title):
    print(title)
    matrix = []
    row_index = 0

    while row_index < n:
        line = input(f"{row_index + 1}번째 줄 입력: ").strip()
        parts = line.split()

        if len(parts) != n:
            print(f"입력 형식 오류: 숫자 {n}개를 공백으로 구분해 입력하세요.")
            continue

        try:
            row = [float(value) for value in parts]
        except ValueError:
            print("입력 형식 오류: 숫자만 입력하세요.")
            continue

        matrix.append(row)
        row_index += 1

    return matrix

# 수동 입력 모드: Cross/X 필터와 패턴을 받아 결과를 출력
# read_matrix_from_console()로 행렬 입력받기, mac_score()로 점수 계산, decide_label()로 판정, measure_average_ms()로 실행 시간 측정
def run_manual_mode():
    print("\n#---------------------------------------")
    print("# [1] 필터 입력")
    print("#---------------------------------------")

    cross_filter = read_matrix_from_console(3, "Cross 필터를 입력하세요. (3줄)")
    x_filter = read_matrix_from_console(3, "\nX 필터를 입력하세요. (3줄)")

    print("\n#---------------------------------------")
    print("# [2] 패턴 입력")
    print("#---------------------------------------")

    pattern = read_matrix_from_console(3, "판별할 패턴을 입력하세요. (3줄)")

    score_cross = mac_score(pattern, cross_filter)
    score_x = mac_score(pattern, x_filter)

    avg_cross_ms = measure_average_ms(pattern, cross_filter, repeat=10)
    avg_x_ms = measure_average_ms(pattern, x_filter, repeat=10)
    avg_ms = (avg_cross_ms + avg_x_ms) / 2

    predicted = decide_label(score_cross, score_x)

    print("\n#---------------------------------------")
    print("# [3] MAC 결과")
    print("#---------------------------------------")
    print(f"Cross 점수: {score_cross}")
    print(f"X 점수: {score_x}")
    print(f"판정: {predicted}")
    print(f"연산 시간(평균/10회): {avg_ms:.6f} ms")