"""
파이썬 엔진(assets/py) 단위 테스트

    python -m unittest discover tests

브라우저 없이 일반 CPython으로 실행합니다. 엔진은 DOM을 사용하지 않기 때문에
Web Worker(Pyodide)에서와 같은 결과를 냅니다.
"""

import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "assets", "py"))

import runner  # noqa: E402


def make_state(height=5, width=5, **extra):
    state = {
        "map": {"height": height, "width": width},
        "characters": [
            {"character": "licat", "x": 0, "y": 0, "directions": 0, "items": {}, "hp": 100, "mp": 100}
        ],
        "mobs": [],
        "items": [],
        "walls": [],
        "print_data": [],
        "say_data": [],
    }
    state.update(extra)
    return state


def run(code, state=None, inputs=None, label="셀 1"):
    result = runner.run_cell(code, json.dumps(state or make_state()), json.dumps(inputs or []), 1, label)
    return json.loads(result)


def events_of(result, t):
    return [e for e in result["events"] if e["t"] == t]


class PrintTest(unittest.TestCase):
    def setUp(self):
        runner.reset_namespace()

    def test_print_uses_python_semantics(self):
        r = run("print('hello', 'world')\nprint(1, 2, sep='-')\nprint('a', end='')\nprint('b')")
        self.assertEqual([e["text"] for e in events_of(r, "print")], ["hello world", "1-2", "ab"])
        self.assertEqual(r["state"]["print_data"], ["hello world", "1-2", "ab"])

    def test_unterminated_line_is_flushed(self):
        r = run("print('x', end='')")
        self.assertEqual([e["text"] for e in events_of(r, "print")], ["x"])

    def test_last_expression_result(self):
        r = run("a = 3\na + 4")
        self.assertEqual(r["result"], "7")
        self.assertIsNone(run("move()")["result"])

    def test_namespace_is_shared_between_cells(self):
        run("count = 10")
        self.assertEqual(run("count * 2")["result"], "20")


class MoveTest(unittest.TestCase):
    def setUp(self):
        runner.reset_namespace()

    def test_move_and_turn(self):
        r = run("move()\nmove()\nturn_left()\nturn_left()\nturn_left()\nrepeat(2, move)")
        licat = r["state"]["characters"][0]
        self.assertEqual((licat["x"], licat["y"], licat["directions"]), (2, 2, 3))
        self.assertEqual([e["t"] for e in r["events"]], ["move", "move", "turn", "turn", "turn", "move", "move"])

    def test_out_of_world_stops_with_error_event(self):
        r = run("turn_left()\nmove()\nprint('never')")
        self.assertEqual(r["error"]["name"], "OutOfWorld")
        self.assertEqual(r["error"]["line"], 2)
        self.assertTrue(r["error"]["hint"])
        self.assertEqual(r["events"][-1]["t"], "error")
        self.assertEqual(events_of(r, "print"), [])

    def test_wall_blocks(self):
        state = make_state(walls=[[0, 0.5, "wall"]])
        r = run("front_is_clear()", state)
        self.assertEqual(r["result"], "False")
        r = run("typeof_wall()", state)
        self.assertEqual(r["result"], "'wall'")
        self.assertEqual(run("move()", state)["error"]["name"], "WallIsExist")

    def test_typeof_wall_out_of_world_on_every_edge(self):
        # 아래쪽/오른쪽 끝에서도 'OutOfWorld'를 돌려줘야 합니다.
        for x, y, d in [(0, 0, 1), (0, 0, 2), (4, 4, 0), (4, 4, 3)]:
            chars = [{"character": "licat", "x": x, "y": y, "directions": d, "items": {}, "hp": 100, "mp": 100}]
            r = run("typeof_wall()", make_state(characters=chars))
            self.assertEqual(r["result"], "'OutOfWorld'", (x, y, d))

    def test_open_door(self):
        state = make_state(walls=[[0, 0.5, "door"]])
        r = run("open_door()\nmove()", state)
        self.assertIsNone(r["error"])
        self.assertEqual(r["state"]["walls"], [])
        self.assertEqual(run("open_door()")["error"]["name"], "DoorIsNotExist")

    def test_too_many_actions(self):
        r = run("while True:\n    turn_left()")
        self.assertEqual(r["error"]["name"], "TooManyActions")

    def test_jump_updates_position_immediately(self):
        r = run("from modules import jump\njump()\nfront_is_clear()\nprint(character_data[0]['y'])")
        self.assertEqual(events_of(r, "print")[0]["text"], "2")
        self.assertEqual(r["state"]["characters"][0]["y"], 2)
        r = run("from modules import jump\njump()\njump()\njump()")
        self.assertEqual(r["error"]["name"], "OutOfWorld")

    def test_modules(self):
        r = run("from modules import turn_right, turn_around, move_to_wall\nturn_right()\nmove_to_wall()")
        self.assertEqual(r["state"]["characters"][0]["x"], 4)


class ItemTest(unittest.TestCase):
    def setUp(self):
        runner.reset_namespace()

    def test_pick_and_put_keep_counts(self):
        state = make_state(items=[[0, 0, "fish-1", 3]])
        r = run("pick()\npick()\npick()\nput('fish-1')\nput('fish-1')\nitem()", state)
        self.assertEqual(r["state"]["items"], [[0, 0, "fish-1", 2]])
        self.assertEqual(r["result"], "{'fish-1': 1}")

    def test_put_on_existing_pile_adds_count(self):
        # 이전 버전에서는 마지막 하나를 내려놓을 때만 개수가 늘었습니다.
        chars = [{"character": "licat", "x": 0, "y": 0, "directions": 0, "items": {"fish-1": 3}, "hp": 100, "mp": 100}]
        state = make_state(characters=chars, items=[[0, 0, "fish-1", 1]])
        r = run("put('fish-1')\nput('fish-1')", state)
        self.assertEqual(r["state"]["items"], [[0, 0, "fish-1", 3]])
        self.assertEqual(r["state"]["characters"][0]["items"], {"fish-1": 1})

    def test_put_errors(self):
        self.assertEqual(run("put('fish-1')")["error"]["name"], "ItemIsNotExist")
        self.assertEqual(run("put('rock')")["error"]["name"], "InvalidItem")
        chars = [{"character": "licat", "x": 0, "y": 0, "directions": 0, "items": {"apple": 1}, "hp": 100, "mp": 100}]
        state = make_state(characters=chars, items=[[0, 0, "fish-1", 1]])
        self.assertEqual(run("put('apple')", state)["error"]["name"], "AnotherItemIsExist")

    def test_set_item(self):
        r = run("set_item(2, 2, 'fish-1')\nset_item(2, 2, 'fish-1', 2)\nset_item(1, 1, 'apple')\nset_item(1, 1, 'diamond')")
        self.assertEqual(sorted(r["state"]["items"]), [[1, 1, "diamond", 1], [2, 2, "fish-1", 3]])
        self.assertEqual(run("set_item(9, 9, 'apple')")["error"]["name"], "OutOfWorld")
        self.assertEqual(run("set_item(1, 1, 'apple', 0)")["error"]["name"], "ArgumentsError")

    def test_eat(self):
        chars = [{"character": "licat", "x": 0, "y": 0, "directions": 0, "items": {"hp-potion": 1}, "hp": 50, "mp": 100}]
        r = run("eat('hp-potion')", make_state(characters=chars))
        self.assertEqual(r["state"]["characters"][0]["hp"], 70)
        self.assertEqual(r["state"]["say_data"], ["냠냠"])


class MobTest(unittest.TestCase):
    def setUp(self):
        runner.reset_namespace()

    def test_add_mob_and_attack(self):
        r = run("leo = add_mob(0, 1, 'lion', 'leo', 2)\nattack()\nmob_data[0]['hp']")
        self.assertEqual(r["result"], "240")
        self.assertEqual(r["state"]["mobs"][0]["directions"], 2)
        self.assertEqual(r["state"]["characters"][0]["mp"], 90)

    def test_mob_handle_survives_between_cells(self):
        run("py1 = add_mob(3, 3, 'py', 'py1')")
        state = make_state(mobs=[{"name": "py1", "mob": "py", "x": 3, "y": 3, "directions": 0, "hp": 50}])
        r = run("py1.move()\npy1.x, py1.y", state)
        self.assertEqual(r["result"], "(3, 4)")
        # 화면에서 몹을 지운 뒤 같은 변수를 쓰면 친절한 오류가 납니다.
        self.assertEqual(run("py1.move()")["error"]["name"], "MobIsNotExist")

    def test_kill_mob(self):
        state = make_state(mobs=[{"name": "g", "mob": "gary", "x": 0, "y": 1, "directions": 0, "hp": 20}])
        r = run("attack('explosion')", state)
        self.assertEqual(r["state"]["mobs"], [])
        self.assertTrue(events_of(r, "attack")[0]["victim"]["removed"])

    def test_mob_kills_licat(self):
        chars = [{"character": "licat", "x": 0, "y": 1, "directions": 0, "items": {}, "hp": 10, "mp": 100}]
        state = make_state(characters=chars, mobs=[{"name": "w", "mob": "wizard", "x": 0, "y": 0, "directions": 0, "hp": 50}])
        r = run("mob_data[0]['mob_obj'].attack()", state)
        self.assertEqual(r["error"]["name"], "CharacterIsDead")
        self.assertEqual(r["state"]["characters"][0]["hp"], 0)

    def test_obstacle(self):
        state = make_state(mobs=[{"name": "g", "mob": "gary", "x": 0, "y": 1, "directions": 0, "hp": 50}])
        self.assertEqual(run("move()", state)["error"]["name"], "ObstacleExist")
        self.assertEqual(run("add_mob(0, 1, 'py', 'p')", state)["error"]["name"], "ObstacleExist")


class ErrorAndInputTest(unittest.TestCase):
    def setUp(self):
        runner.reset_namespace()

    def test_name_error_has_hint_and_suggestion(self):
        r = run("mvoe()")
        self.assertEqual(r["error"]["name"], "NameError")
        self.assertIn("'move'", r["error"]["hint"])
        self.assertIn("<셀 1>", r["error"]["traceback"])
        self.assertNotIn("runner.py", r["error"]["traceback"])

    def test_error_in_function_from_other_cell(self):
        run("def go():\n    turn_left()\n    move()", label="셀 1")
        r = run("go()", label="셀 2")
        self.assertEqual((r["error"]["file"], r["error"]["line"]), ("셀 1", 3))

    def test_syntax_error_line(self):
        r = run("move()\nif True\n    move()")
        self.assertEqual(r["error"]["name"], "SyntaxError")
        self.assertEqual(r["error"]["line"], 2)
        self.assertEqual(r["events"], [r["events"][-1]])  # 아무것도 실행되지 않음

    def test_world_errors_can_be_caught(self):
        r = run("try:\n    turn_left()\n    move()\nexcept OutOfWorld:\n    print('잡았다')")
        self.assertIsNone(r["error"])
        self.assertEqual(events_of(r, "print")[0]["text"], "잡았다")

    def test_input_requests_value_and_replays(self):
        code = "x = 1\nname = input('이름? ')\nprint(name)"
        r = run(code)
        self.assertEqual(r, {"need_input": "이름? "})
        r = run(code, inputs=["라이캣"])
        self.assertEqual([e["text"] for e in events_of(r, "print")], ["이름? 라이캣", "라이캣"])
        r = run(code, inputs=[None])
        self.assertEqual(r["error"]["name"], "InputNotAllowed")

    def test_input_rolls_back_nested_mutations_and_preserves_aliases(self):
        run("values = []\nalias = values\ndata = {'values': values}")
        code = "data['values'].append(1)\ninput('first')\nvalues.append(2)\ninput('second')\n(values, alias is values)"
        self.assertEqual(run(code), {"need_input": "first"})
        self.assertEqual(run(code, inputs=["a"]), {"need_input": "second"})
        result = run(code, inputs=["a", "b"])
        self.assertEqual(result["result"], "([1, 2], True)")

    def test_input_rolls_back_function_defaults_and_object_attributes(self):
        run("class Counter:\n    pass\nc = Counter()\nc.n = 0\ndef append(values=[]):\n    values.append(1)\n    return values")
        code = "c.n += 1\nvalues = append()\ninput('?')\n(c.n, values)"
        self.assertEqual(run(code), {"need_input": "?"})
        self.assertEqual(run(code, inputs=["yes"])["result"], "(1, [1])")

    def test_unterminated_output_buffer_is_bounded(self):
        out = runner._WorldStdout()
        for _ in range(100):
            out.write('x' * 1000)
        self.assertLessEqual(len(out.buffer), runner.MAX_LINE_LENGTH)

    def test_long_print_line_is_truncated_once(self):
        result = run("print('x' * 12000, end=''); print('tail')")
        lines = result["state"]["print_data"]
        self.assertEqual(lines, ['x' * runner.MAX_LINE_LENGTH + ' …(생략)'])

    def test_mission_functions_still_work(self):
        # 화면에서는 뺐지만 교안 코드에 남아 있어도 오류가 나지 않아야 합니다.
        self.assertIsNone(run("mission_start()\nmove()\nmission_end()")["error"])

    def test_state_round_trip_keeps_wall_keys(self):
        state = make_state(walls=[[2, 0.5, "wall"], [0.5, 1, "fence"]])
        r = run("sorted(wall_data['world'].items())", state)
        self.assertEqual(r["result"], "[((0.5, 1), 'fence'), ((2, 0.5), 'wall')]")
        self.assertEqual(sorted(r["state"]["walls"]), [[0.5, 1.0, "fence"], [2.0, 0.5, "wall"]])


if __name__ == "__main__":
    unittest.main()


def run_all(codes, state=None, inputs=None):
    result = runner.run_all(json.dumps(codes), json.dumps(state or make_state()), json.dumps(inputs or []), 1)
    return json.loads(result)


class RunAllTest(unittest.TestCase):
    """제출 채점용 전체 실행"""

    def setUp(self):
        runner.reset_namespace()

    def test_runs_cells_in_order_from_given_state(self):
        r = run_all(["n = 2", "", "for i in range(n):\n    move()\nprint('끝')"])
        self.assertIsNone(r["error"])
        self.assertEqual(r["state"]["characters"][0]["y"], 2)
        self.assertEqual(r["state"]["print_data"], ["끝"])

    def test_does_not_use_learner_variables(self):
        run("n = 3")  # 학습자가 노트북에서 만든 변수
        r = run_all(["for i in range(n):\n    move()"])
        self.assertEqual(r["error"]["name"], "NameError")
        # 학습자 환경의 변수는 그대로 남아 있습니다.
        self.assertEqual(run("n")["result"], "3")

    def test_stops_at_first_error_with_cell_and_line(self):
        r = run_all(["move()", "print('a')\nturn_left()\nmove()", "print('never')"])
        self.assertEqual((r["error"]["name"], r["error"]["file"], r["error"]["line"]), ("OutOfWorld", "셀 2", 3))
        self.assertEqual(r["state"]["print_data"], ["a"])

    def test_action_limit_is_per_cell(self):
        loop = "for i in range(3000):\n    turn_left()"
        r = run_all([loop, loop, loop, loop])
        self.assertIsNone(r["error"])

    def test_input(self):
        self.assertEqual(run_all(["x = input('값? ')"]), {"need_input": "값? "})
        r = run_all(["x = input('값? ')\nprint(x)"], inputs=["7"])
        self.assertEqual(r["state"]["print_data"], ["값? 7", "7"])

    def test_engine_changes_from_cells_do_not_affect_grading(self):
        walled = make_state(walls=[[0.5, 0, "wall"]])
        down = "turn_left()\nturn_left()\nturn_left()\nmove()"
        for poison in [
            "wall_blocked.clear()",
            "import engine\nengine.MAX_EVENTS = 10**9",
            "Character.move = lambda self: None",
            "import built_in_functions as b\nb.move = lambda c=None: None",
            "import builtins\nbuiltins.print = lambda *a, **k: None",
        ]:
            with self.subTest(poison=poison):
                run(poison, walled)
                r = run_all([down + "\nprint('a')"], walled)
                self.assertEqual(r["error"]["name"], "WallIsExist")
                runner.reset_namespace()
                r = run_all(["print('a')\nwhile True:\n    turn_left()"])
                self.assertEqual(r["error"]["name"], "TooManyActions")
                self.assertEqual(r["state"]["print_data"], ["a"])


class CallLimitTest(unittest.TestCase):
    def setUp(self):
        runner.reset_namespace()

    def test_failed_moves_in_except_exception_loop_stop(self):
        r = run("while True:\n    try:\n        move()\n    except Exception:\n        pass")
        self.assertEqual(r["error"]["name"], "TooManyActions")
        self.assertTrue(r["error"]["world"])
        self.assertIn("100,000", r["error"]["hint"])

    def test_query_only_loop_stops(self):
        r = run("while not on_item():\n    pass")
        self.assertEqual(r["error"]["name"], "TooManyActions")

    def test_many_queries_below_limit_are_fine(self):
        r = run("for _ in range(20000):\n    front_is_clear()\nprint('ok')")
        self.assertIsNone(r["error"])

    def test_world_errors_are_still_catchable(self):
        r = run("try:\n    repeat(5, move)\nexcept OutOfWorld:\n    print('caught')")
        self.assertEqual(r["state"]["print_data"], ["caught"])
