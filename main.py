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



# JSON 분석 함수
# load_json_data(), analyze_case(), summarize_results(), run_json_mode()

# JSON 파일 읽기
def load_json_data(path="data.json"):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

# 케이스 하나 분석
def analyze_case(case_id, pattern, cross_filter, x_filter, expected):
    size = extract_size_from_case_id(case_id)
    if size is None:
        return {
            "case_id": case_id,
            "score_cross": None,
            "score_x": None,
            "predicted": "UNDECIDED",
            "expected": normalize_label(expected),
            "passed": False,
            "reason": "case_id에서 크기 추출 실패",
        }

    ok, reason = validate_matrix(pattern, expected_size=size)
    if not ok:
        return {
            "case_id": case_id,
            "score_cross": None,
            "score_x": None,
            "predicted": "UNDECIDED",
            "expected": normalize_label(expected),
            "passed": False,
            "reason": f"pattern 검증 실패: {reason}",
        }

    ok, reason = validate_matrix(cross_filter, expected_size=size)
    if not ok:
        return {
            "case_id": case_id,
            "score_cross": None,
            "score_x": None,
            "predicted": "UNDECIDED",
            "expected": normalize_label(expected),
            "passed": False,
            "reason": f"Cross 필터 검증 실패: {reason}",
        }

    ok, reason = validate_matrix(x_filter, expected_size=size)
    if not ok:
        return {
            "case_id": case_id,
            "score_cross": None,
            "score_x": None,
            "predicted": "UNDECIDED",
            "expected": normalize_label(expected),
            "passed": False,
            "reason": f"X 필터 검증 실패: {reason}",
        }

    normalized_expected = normalize_label(expected)
    if normalized_expected is None:
        return {
            "case_id": case_id,
            "score_cross": None,
            "score_x": None,
            "predicted": "UNDECIDED",
            "expected": None,
            "passed": False,
            "reason": "expected 라벨 정규화 실패",
        }

    score_cross = mac_score(pattern, cross_filter)
    score_x = mac_score(pattern, x_filter)
    predicted = decide_label(score_cross, score_x)

    passed = (predicted == normalized_expected)
    reason = ""

    if predicted == "UNDECIDED":
        reason = "동점 규칙으로 UNDECIDED 처리"
    elif not passed:
        reason = "예상 라벨과 판정 결과 불일치"

    return {
        "case_id": case_id,
        "score_cross": score_cross,
        "score_x": score_x,
        "predicted": predicted,
        "expected": normalized_expected,
        "passed": passed,
        "reason": reason,
    }

# 전체 결과 요약
def summarize_results(results):
    total = len(results)
    passed = sum(1 for item in results if item["passed"])
    failed = total - passed
    failed_cases = [item for item in results if not item["passed"]]

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "failed_cases": failed_cases,
    }

# json 모드 실행
def run_json_mode():

    print("\n#---------------------------------------")
    print("# [1] JSON 데이터 로드")
    print("#---------------------------------------")

    try:
        data = load_json_data("data.json")
    except FileNotFoundError:
        print("data.json 파일을 찾을 수 없습니다.")
        return
    except json.JSONDecodeError:
        print("data.json 파싱에 실패했습니다.")
        return

    filters = data.get("filters", {})
    patterns = data.get("patterns", {})

    if not isinstance(filters, dict):
        print("filters 형식이 올바르지 않습니다.")
        return

    if not isinstance(patterns, dict):
        print("patterns 형식이 올바르지 않습니다.")
        return

    filter_map = {}
    results = []

    print("\n#---------------------------------------")
    print("# [2] 필터 정리")
    print("#---------------------------------------")

    for size_key, filter_bundle in filters.items():
        parts = str(size_key).split("_")

        if len(parts) < 2:
            print(f"- {size_key}: 필터 키 형식 오류")
            continue

        try:
            size = int(parts[1])
        except ValueError:
            print(f"- {size_key}: 필터 크기 파싱 실패")
            continue

        if not isinstance(filter_bundle, dict):
            print(f"- {size_key}: 필터 구조 오류")
            continue

        cross_filter = None
        x_filter = None

        for raw_name, matrix in filter_bundle.items():
            label = normalize_label(raw_name)

            if label == "Cross":
                cross_filter = matrix
            elif label == "X":
                x_filter = matrix

        if cross_filter is None or x_filter is None:
            print(f"- {size_key}: Cross/X 필터 누락")
            continue

        filter_map[size] = {
            "Cross": cross_filter,
            "X": x_filter,
        }
        print(f"✓ {size_key} 필터 로드 완료")

    print("\n#---------------------------------------")
    print("# [3] 패턴 분석")
    print("#---------------------------------------")

    for case_id, case_data in patterns.items():
        print(f"--- {case_id} ---")

        if not isinstance(case_data, dict):
            result = {
                "case_id": case_id,
                "score_cross": None,
                "score_x": None,
                "predicted": "UNDECIDED",
                "expected": None,
                "passed": False,
                "reason": "case_data 구조 오류",
            }
            results.append(result)
            print("FAIL: case_data 구조 오류")
            continue

        size = extract_size_from_case_id(case_id)

        if size is None:
            result = {
                "case_id": case_id,
                "score_cross": None,
                "score_x": None,
                "predicted": "UNDECIDED",
                "expected": normalize_label(case_data.get("expected")),
                "passed": False,
                "reason": "case_id 형식 오류",
            }
            results.append(result)
            print("FAIL: case_id 형식 오류")
            continue

        if size not in filter_map:
            result = {
                "case_id": case_id,
                "score_cross": None,
                "score_x": None,
                "predicted": "UNDECIDED",
                "expected": normalize_label(case_data.get("expected")),
                "passed": False,
                "reason": f"size_{size} 필터 없음",
            }
            results.append(result)
            print(f"FAIL: size_{size} 필터 없음")
            continue

        pattern = case_data.get("input")
        expected = case_data.get("expected")

        result = analyze_case(
            case_id=case_id,
            pattern=pattern,
            cross_filter=filter_map[size]["Cross"],
            x_filter=filter_map[size]["X"],
            expected=expected,
        )
        results.append(result)

        if result["score_cross"] is not None:
            print(f"Cross 점수: {result['score_cross']}")
        if result["score_x"] is not None:
            print(f"X 점수: {result['score_x']}")

        print(
            f"판정: {result['predicted']} | "
            f"expected: {result['expected']} | "
            f"{'PASS' if result['passed'] else 'FAIL'}"
        )

        if result["reason"]:
            print(f"사유: {result['reason']}")

    summary = summarize_results(results)

    print("\n#---------------------------------------")
    print("# [4] 결과 요약")
    print("#---------------------------------------")
    print(f"총 테스트: {summary['total']}개")
    print(f"통과: {summary['passed']}개")
    print(f"실패: {summary['failed']}개")

    if summary["failed_cases"]:
        print("\n실패 케이스:")
        for item in summary["failed_cases"]:
            print(f"- {item['case_id']}: {item['reason']}")


# 성능 분석 출력기
def print_performance_table():
    print("\n#---------------------------------------")
    print("# [성능 분석]")
    print("#---------------------------------------")
    print("크기       평균 시간(ms)    연산 횟수")
    print("---------------------------------------")

    for n in (3, 5, 13, 25):
        pattern = build_cross_pattern(n)
        filt = build_cross_pattern(n)
        avg_ms = measure_average_ms(pattern, filt, repeat=10)

        print(f"{n}x{n}      {avg_ms:>12.6f}      {n * n}")

