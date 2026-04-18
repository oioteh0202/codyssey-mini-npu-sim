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