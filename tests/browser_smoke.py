"""Run manually with: python tests/browser_smoke.py (requires Playwright and Chrome)."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import unittest

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class BrowserSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(channel='chrome', headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.page = self.browser.new_page()
        self.errors = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        self.page.route('**/*wenivops.co.kr/**', lambda route: route.abort())
        self.page.goto(f'http://127.0.0.1:{self.server.server_port}', wait_until='domcontentloaded')
        self.page.wait_for_function("window.__wenivDebug?.engine.status === 'ready' && __wenivDebug.stories.stories.length === 22", timeout=60000)

    def tearDown(self):
        self.page.close()
        self.assertEqual(self.errors, [])

    def set_codes(self, *codes):
        self.page.evaluate('(codes) => __wenivDebug.notebook.setCodes(codes)', list(codes))

    def open_story(self, index):
        self.page.locator(f'.story-list > li[data-id="{index}"] .btn-toggle').click()

    def test_basic_execution_and_input_mutations(self):
        self.set_codes('values = []', "values.append(1)\nname = input('name?')\nmove()\nprint(values)")
        self.page.on('dialog', lambda dialog: dialog.accept('licat'))
        self.page.evaluate('''async () => {
            const d = __wenivDebug;
            d.notebook.run(d.notebook.cells[0]);
            d.notebook.run(d.notebook.cells[1]);
            await d.engine.chain;
            d.player.skip();
            await d.player.whenIdle();
        }''')
        self.assertEqual(self.page.evaluate('__wenivDebug.world.state.characters[0].y'), 1)
        self.assertEqual(self.page.evaluate('__wenivDebug.world.state.print_data.at(-1)'), '[1]')

    def test_collapsing_story_preserves_separate_drafts(self):
        self.set_codes('free_draft = 1')
        self.page.locator('.btn-story').click()
        self.open_story(1)
        self.set_codes('story_draft = 2')
        self.open_story(1)
        self.page.locator('.btn-close-story').click()
        self.assertEqual(self.page.evaluate('__wenivDebug.notebook.getCodes()'), ['free_draft = 1'])
        self.set_codes('free_draft = 3')
        self.page.evaluate('__wenivDebug.notebook.flushSave()')
        self.assertEqual(self.page.evaluate("JSON.parse(localStorage.getItem('1_draft'))"), ['story_draft = 2'])

    def test_story_switch_cancels_queued_grading(self):
        self.page.locator('.btn-story').click()
        self.open_story(1)
        self.set_codes('while True:\n    pass')
        self.page.evaluate('__wenivDebug.notebook.run(__wenivDebug.notebook.cells[0])')
        self.page.wait_for_function('__wenivDebug.engine.running')
        self.set_codes('move()')
        self.page.evaluate("void __wenivDebug.stories.submit(document.querySelector('.story-list > li.active'))")
        self.open_story(2)
        self.page.wait_for_function("!__wenivDebug.isBusy() && !__wenivDebug.stories.grading && __wenivDebug.engine.status === 'ready'")
        self.assertEqual(self.page.evaluate('__wenivDebug.world.story.index'), 2)
        self.assertEqual(self.page.evaluate('__wenivDebug.world.state.characters[0].y'), 0)
        self.assertEqual(self.page.locator('.result-dialog').count(), 0)
        self.assertIsNone(self.page.evaluate("localStorage.getItem('1_code')"))

    def test_grading_then_cell_uses_graded_world(self):
        self.page.locator('.btn-story').click()
        self.open_story(13)
        self.set_codes("turn_left()\nsay('JEJU')", 'turn_left()')
        self.page.evaluate('''async () => {
            const d = __wenivDebug;
            const submit = d.stories.submit(document.querySelector('.story-list > li.active'));
            d.notebook.run(d.notebook.cells[1]);
            await submit;
            await d.engine.chain;
            d.player.skip();
            await d.player.whenIdle();
        }''')
        self.assertEqual(self.page.evaluate('__wenivDebug.world.state.characters[0].directions'), 3)
        self.assertEqual(self.page.locator('.result-dialog.passed').count(), 1)

    def test_import_does_not_overlap_default_character_with_mob(self):
        self.page.locator('#worldFileInput').set_input_files({
            'name': 'world_data.json', 'mimeType': 'application/json',
            'buffer': b'{"map_data":{"height":7,"width":7},"character_data":[],"mob_data":[{"mob":"py","name":"p","x":0,"y":0}]}'
        })
        self.page.wait_for_function('__wenivDebug.world.state.map.height === 7')
        self.assertEqual(self.page.evaluate('__wenivDebug.world.state.mobs'), [])

    def test_header_story_button_and_world_menu(self):
        # 스토리 버튼: 창을 열면 월드 편집 버튼이 막히고, 접기 버튼으로 닫으면 풀린다
        self.page.locator('.btn-story').click()
        self.page.wait_for_function('__wenivDebug.storyMode === true')
        self.assertTrue(self.page.locator('.btn-story.active').count() == 1)
        self.assertTrue(self.page.locator('.story.show').count() == 1)
        self.assertTrue(self.page.locator('.btn-wall').is_disabled())
        self.page.locator('.btn-close-story').click()
        self.page.wait_for_function('__wenivDebug.storyMode === false')
        self.assertEqual(self.page.locator('.btn-story.active').count(), 0)
        self.assertFalse(self.page.locator('.btn-wall').is_disabled())
        # 월드 메뉴: 버튼을 누르면 창이 열리고, 바깥을 누르면 닫힌다
        self.page.locator('.btn-speed').click()
        self.assertEqual(self.page.locator('.btn-speed.active').count(), 1)
        self.page.mouse.click(5, 400)
        self.assertEqual(self.page.locator('.btn-speed.active').count(), 0)
        # 툴팁
        self.page.locator('.btn-reset#init').hover()
        self.assertEqual(self.page.locator('#init .tooltip').inner_text(), '월드, 캐릭터 초기화')

    def test_header_theme_profile_certificate_report(self):
        self.page.locator('.btn-dark-mode').click()
        theme = self.page.evaluate("document.documentElement.getAttribute('color-theme')")
        self.assertEqual(self.page.evaluate("localStorage.getItem('color-theme')"), theme)
        # 프로필 이름 저장
        self.page.locator('.btn-profile').click()
        self.page.locator('.profile-modal .btn-edit').click()
        self.page.locator('#profile-name').fill('라이캣')
        self.page.locator('.profile-modal .btn-confirm').click()
        self.assertEqual(self.page.locator('.profile-modal .txt-name').inner_text(), '라이캣')
        self.assertEqual(self.page.evaluate("JSON.parse(localStorage.getItem('profile')).name"), '라이캣')
        # 보고서: 제출 기록이 있으면 내려받는다
        self.page.evaluate("""() => { localStorage.setItem('1_code', JSON.stringify(['move()'])); localStorage.setItem('1_check', '정답'); }""")
        with self.page.expect_download() as info:
            self.page.locator('.btn-report').click()
        self.assertTrue(info.value.suggested_filename.endswith('_보고서_라이캣.md'))
        # 인증서 창: 장마다 진행률, 다 풀지 않으면 받기 버튼이 막힘
        self.page.mouse.click(5, 400)
        self.page.locator('.btn-certif').click()
        self.page.wait_for_function("document.querySelectorAll('.certif-item').length === 2")
        self.assertEqual(self.page.locator('.certif-item').first.locator('.solved').inner_text(), '1')
        self.assertTrue(self.page.locator('.certif-item .btn-download-certif').first.is_disabled())


if __name__ == '__main__':
    unittest.main(verbosity=2)
