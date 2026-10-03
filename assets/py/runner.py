"""
노트북 셀 실행기 (Web Worker 안에서 호출됩니다)

    run_cell(code, state_json, inputs_json, seed, label) -> json 문자열

1. 화면이 보낸 월드 상태를 전역 데이터에 불러옵니다.
2. 학습자 코드를 실행하면서 이벤트(이동, 출력 등)를 기록합니다.
3. 기록된 이벤트, 실행 후 월드 상태, 마지막 식의 값, 오류 정보를 돌려줍니다.
"""

import ast
import builtins
import copy
import difflib
import json
import linecache
import math
import random
import sys
import traceback
import types
from datetime import datetime

import engine
import coordinate
import error as error_module
import built_in_functions as bif
from coordinate import (
    map_data,
    character_data,
    mob_data,
    item_data,
    wall_data,
    print_data,
    say_data,
)
from character import Character
from mob import Mob
from error import WorldError, InputNotAllowed

MAX_RESULT_LENGTH = 10000
MAX_LINE_LENGTH = 10000

# 파이썬 기본 오류에 대한 한글 힌트
PYTHON_HINTS = {
    "NameError": "이름의 철자가 맞는지, 사용하기 전에 정의했는지 확인하세요.",
    "SyntaxError": "괄호, 따옴표, 콜론(:)이 빠지거나 짝이 맞지 않는지 확인하세요.",
    "IndentationError": "들여쓰기(스페이스 4칸)가 맞는지 확인하세요.",
    "TabError": "들여쓰기에 탭과 스페이스를 섞어 쓰지 않았는지 확인하세요.",
    "TypeError": "함수에 넣은 값의 개수와 종류(숫자, 문자열 등)를 확인하세요.",
    "KeyError": "딕셔너리에 그 키가 있는지 확인하세요.",
    "IndexError": "리스트의 범위를 벗어났습니다. 인덱스는 0부터 시작합니다.",
    "ValueError": "값의 형식이 올바른지 확인하세요. 예: int('3')은 되지만 int('삼')은 안 됩니다.",
    "ZeroDivisionError": "0으로 나눌 수 없습니다.",
    "AttributeError": "객체에 그 속성이나 메서드가 있는지 철자를 확인하세요.",
    "RecursionError": "함수가 자기 자신을 끝없이 호출하고 있지 않은지 확인하세요.",
    "ModuleNotFoundError": "모듈 이름을 확인하세요. 예: from modules import turn_right",
    "ImportError": "가져오려는 이름의 철자를 확인하세요. 예: from modules import turn_right",
}


class _NeedInput(BaseException):
    """input()에 줄 값이 없을 때 화면에 입력을 요청하기 위한 신호"""

    def __init__(self, prompt):
        super().__init__(prompt)
        self.prompt = prompt


class _WorldStdout:
    """print() 출력을 줄 단위로 모아 터미널 이벤트로 보냅니다."""

    def __init__(self):
        self.buffer = ""
        self.truncated = False

    def write(self, text):
        text = str(text)
        parts = text.split("\n")
        for index, part in enumerate(parts):
            remaining = MAX_LINE_LENGTH - len(self.buffer)
            self.buffer += part[:remaining]
            self.truncated |= len(part) > remaining
            if index < len(parts) - 1:
                line = self.buffer + (" …(생략)" if self.truncated else "")
                self.buffer, self.truncated = "", False
                self._emit(line)
        return len(text)

    def flush(self):
        pass

    def flush_all(self):
        if self.buffer:
            line = self.buffer + (" …(생략)" if self.truncated else "")
            self.buffer, self.truncated = "", False
            self._emit(line, force=True)

    def isatty(self):
        return False

    def _emit(self, line, force=False):
        if len(line) > MAX_LINE_LENGTH:
            line = line[:MAX_LINE_LENGTH] + " …(생략)"
        print_data.append(line)
        if force:
            engine.events.append({"t": "print", "text": line})
        else:
            engine.emit("print", text=line)


_inputs = []


def _input(prompt=""):
    prompt = str(prompt)
    if not _inputs:
        raise _NeedInput(prompt)
    value = _inputs.pop(0)
    if value is None:
        raise InputNotAllowed()
    sys.stdout.write(f"{prompt}{value}\n")
    return value


def _make_namespace():
    ns = {"__name__": "__main__", "__builtins__": builtins}
    exports = [
        "say", "directions", "item", "set_item", "move", "turn_left", "pick", "put",
        "repeat", "attack", "front_is_clear", "left_is_clear", "right_is_clear",
        "back_is_clear", "open_door", "typeof_wall", "mission_start", "mission_end",
        "on_item", "mob_exist", "character_exist", "show_modal_alert", "eat",
        "add_mob", "add_ch",
    ]
    for name in exports:
        ns[name] = getattr(bif, name)

    for name in [
        "map_data", "character_data", "default_character", "mob_data", "item_data",
        "wall_data", "valid_items", "edible_items", "wall_types", "wall_blocked",
        "skill_data", "character_info", "mob_info", "print_data", "say_data",
        "error_message",
    ]:
        ns[name] = getattr(coordinate, name)

    for name in dir(error_module):
        value = getattr(error_module, name)
        if isinstance(value, type) and issubclass(value, Exception):
            ns[name] = value

    ns.update(
        Character=Character,
        Mob=Mob,
        licat=Character("licat"),
        input=_input,
        # 이전 버전에서 따로 import하지 않아도 쓸 수 있던 모듈
        math=math,
        json=json,
        copy=copy,
        datetime=datetime,
    )
    return ns


namespace = _make_namespace()


def _snapshot_mutables(ns):
    """입력 재실행 전 컨테이너를 제자리에서 복구해 별칭/함수 참조를 보존합니다.

    모듈 내부 상태, 파일, 제너레이터 같은 외부 자원의 부작용은 복구하지 않습니다.
    """
    pending = [ns]
    seen = set()
    snapshots = []
    while pending:
        value = pending.pop()
        if id(value) in seen:
            continue
        seen.add(id(value))
        if type(value) is dict:
            saved = value.copy()
            snapshots.append((value, saved))
            pending.extend(saved.keys())
            pending.extend(saved.values())
        elif type(value) in (list, set, bytearray):
            saved = value.copy() if type(value) is not bytearray else value[:]
            snapshots.append((value, saved))
            pending.extend(saved)
        elif type(value) in (tuple, frozenset):
            pending.extend(value)
        elif isinstance(value, types.FunctionType) and value.__globals__ is ns:
            pending.extend((value.__defaults__, value.__kwdefaults__, value.__dict__))
            for cell in value.__closure__ or ():
                try:
                    saved = cell.cell_contents
                except ValueError:
                    continue
                snapshots.append((cell, saved))
                pending.append(saved)
        elif not isinstance(value, (type, types.ModuleType)) and type(value).__module__ == "__main__":
            pending.append(getattr(value, "__dict__", None))
    return snapshots


def _restore_mutables(snapshots):
    for value, saved in snapshots:
        if type(value) is dict or type(value) is set:
            value.clear()
            value.update(saved)
        elif isinstance(value, types.CellType):
            value.cell_contents = saved
        else:
            value[:] = saved


def reset_namespace():
    """학습자가 만든 변수를 모두 지웁니다."""
    namespace.clear()
    namespace.update(_make_namespace())


# ----------------------------------------------------------------------
# 상태 불러오기 / 내보내기
def _num(value):
    value = float(value)
    return int(value) if value.is_integer() else value


def _merge(target, incoming, name_key, obj_key, factory, order):
    old = {d.get(name_key): d for d in target if isinstance(d, dict)}
    merged = []
    for src in incoming:
        name = src.get(name_key)
        d = old.get(name)
        if d is None:
            d = {}
        obj = d.get(obj_key)
        if not (isinstance(obj, factory) and obj.name == name):
            obj = factory(name)

        items = d.get("items") if isinstance(d.get("items"), dict) else None
        d.clear()
        for key in order:
            if key == obj_key:
                d[key] = obj
            elif key in src:
                d[key] = src[key]
        if "items" in d:
            if items is not None:
                items.clear()
                items.update(d["items"])
                d["items"] = items
        merged.append(d)
    target[:] = merged


def load_state(state):
    map_data.clear()
    map_data.update(height=int(state["map"]["height"]), width=int(state["map"]["width"]))

    _merge(
        character_data,
        state.get("characters", []),
        "character",
        "character_obj",
        Character,
        ["character", "character_obj", "x", "y", "directions", "items", "hp", "mp"],
    )
    _merge(
        mob_data,
        state.get("mobs", []),
        "name",
        "mob_obj",
        Mob,
        ["name", "mob", "mob_obj", "x", "y", "directions", "hp"],
    )

    old_items = dict(item_data)
    item_data.clear()
    for x, y, name, count in state.get("items", []):
        pos = (int(x), int(y))
        d = old_items.get(pos)
        if not isinstance(d, dict):
            d = {}
        d.clear()
        d.update(item=name, count=int(count))
        item_data[pos] = d

    walls = wall_data["world"] if isinstance(wall_data.get("world"), dict) else {}
    walls.clear()
    for x, y, wall_type in state.get("walls", []):
        walls[(_num(x), _num(y))] = wall_type
    wall_data.clear()
    wall_data["world"] = walls

    print_data[:] = [str(v) for v in state.get("print_data", [])]
    say_data[:] = [str(v) for v in state.get("say_data", [])]


def _plain(value):
    """JSON으로 보낼 수 있는 값으로 바꿉니다."""
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    return str(value)


def dump_state():
    characters = []
    for c in character_data:
        if isinstance(c, dict) and "character" in c:
            characters.append(
                {k: _plain(c.get(k)) for k in ["character", "x", "y", "directions", "items", "hp", "mp"]}
            )
    mobs = []
    for m in mob_data:
        if isinstance(m, dict) and "name" in m:
            mobs.append({k: _plain(m.get(k)) for k in ["name", "mob", "x", "y", "directions", "hp"]})

    items = []
    for pos, v in item_data.items():
        try:
            x, y = pos
            items.append([int(x), int(y), str(v["item"]), int(v["count"])])
        except (TypeError, ValueError, KeyError):
            continue

    walls = []
    for pos, wall_type in wall_data.get("world", {}).items():
        try:
            x, y = pos
            walls.append([float(x), float(y), str(wall_type)])
        except (TypeError, ValueError):
            continue

    return {
        "map": {"height": map_data.get("height", 5), "width": map_data.get("width", 5)},
        "characters": characters,
        "mobs": mobs,
        "items": items,
        "walls": walls,
        "print_data": [str(v) for v in print_data],
        "say_data": [str(v) for v in say_data],
    }


# ----------------------------------------------------------------------
# 실행
def _exec(code, filename, ns=None):
    ns = namespace if ns is None else ns
    tree = ast.parse(code, filename, "exec")
    last_expr = None
    if tree.body and isinstance(tree.body[-1], ast.Expr):
        last_expr = ast.Expression(tree.body.pop().value)
    exec(compile(tree, filename, "exec"), ns)
    if last_expr is not None:
        return eval(compile(last_expr, filename, "eval"), ns)
    return None


def _is_learner_file(filename):
    return filename.startswith("<셀")


def _format_error(exc, ns=None):
    ns = namespace if ns is None else ns
    name = type(exc).__name__
    te = traceback.TracebackException.from_exception(exc)
    frames = [f for f in te.stack if _is_learner_file(f.filename)]
    te.stack = traceback.StackSummary.from_list(frames)
    text = "".join(te.format()).rstrip()

    if isinstance(exc, WorldError):
        message, hint = exc.message, exc.hint
    else:
        last = "".join(te.format_exception_only()).strip().splitlines()
        message = last[-1] if last else str(exc)
        if message.startswith(name + ":"):
            message = message[len(name) + 1 :].strip()
        hint = PYTHON_HINTS.get(name, "")
        if isinstance(exc, NameError) and getattr(exc, "name", None) and "Did you mean" not in message:
            candidates = [k for k in ns if not k.startswith("_")] + dir(builtins)
            close = difflib.get_close_matches(exc.name, candidates, n=1, cutoff=0.6)
            if close:
                hint = f"혹시 '{close[0]}'를 쓰려고 했나요? " + hint

    # 오류가 난 셀과 줄 (다른 셀에서 정의한 함수 안에서 났을 수도 있습니다)
    line = file = None
    if isinstance(exc, SyntaxError) and exc.filename and _is_learner_file(exc.filename):
        line, file = exc.lineno, exc.filename
    elif frames:
        line, file = frames[-1].lineno, frames[-1].filename

    return {
        "name": name,
        "message": message,
        "hint": hint,
        "traceback": text,
        "line": line,
        "file": file[1:-1] if file else None,
        "world": isinstance(exc, WorldError),
    }


def run_cell(code, state_json, inputs_json="[]", seed=0, label="셀"):
    load_state(json.loads(state_json))
    engine.reset()
    _inputs[:] = json.loads(inputs_json)
    random.seed(seed)

    filename = f"<{label}>"
    linecache.cache[filename] = (len(code), None, code.splitlines(True), filename)
    snapshot = _snapshot_mutables(namespace)

    out = _WorldStdout()
    old_stdout, old_stderr, old_input = sys.stdout, sys.stderr, builtins.input
    sys.stdout = sys.stderr = out
    builtins.input = _input

    result = None
    err = None
    try:
        value = _exec(code, filename)
        if value is not None:
            result = repr(value)
            if len(result) > MAX_RESULT_LENGTH:
                result = result[:MAX_RESULT_LENGTH] + " …(생략)"
    except _NeedInput as signal:
        _restore_mutables(snapshot)
        return json.dumps({"need_input": signal.prompt}, ensure_ascii=False)
    except BaseException as exc:  # SystemExit, KeyboardInterrupt까지 학습자 오류로 보여 줍니다.
        err = _format_error(exc)
    finally:
        out.flush_all()
        sys.stdout, sys.stderr, builtins.input = old_stdout, old_stderr, old_input

    if err:
        engine.events.append(dict(err, t="error"))

    return json.dumps(
        {"events": engine.events, "state": dump_state(), "result": result, "error": err},
        ensure_ascii=False,
        default=str,
    )


def run_all(codes_json, state_json, inputs_json="[]", seed=0):
    """
    제출 채점용: 학습자 변수와 섞이지 않는 새 환경에서 셀 전체를 위에서부터 실행합니다.

    오류가 나면 그 셀에서 멈추고 오류 정보를 돌려줍니다. 동작 한도는 셀마다 적용합니다.
    """
    codes = json.loads(codes_json)
    load_state(json.loads(state_json))
    _inputs[:] = json.loads(inputs_json)
    random.seed(seed)
    ns = _make_namespace()

    out = _WorldStdout()
    old_stdout, old_stderr, old_input = sys.stdout, sys.stderr, builtins.input
    sys.stdout = sys.stderr = out
    builtins.input = _input

    err = None
    try:
        for index, code in enumerate(codes):
            if not code.strip():
                continue
            filename = f"<셀 {index + 1}>"
            linecache.cache[filename] = (len(code), None, code.splitlines(True), filename)
            engine.reset()
            _exec(code, filename, ns)
    except _NeedInput as signal:
        return json.dumps({"need_input": signal.prompt}, ensure_ascii=False)
    except BaseException as exc:
        err = _format_error(exc, ns)
    finally:
        out.flush_all()
        sys.stdout, sys.stderr, builtins.input = old_stdout, old_stderr, old_input
        engine.reset()

    return json.dumps({"state": dump_state(), "error": err}, ensure_ascii=False, default=str)
