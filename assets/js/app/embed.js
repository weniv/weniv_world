// 위니버시티 안(iframe)에서 열렸을 때 부모 창(위니버시티)에 알리기
//
// 위니버시티 /tools/world 는 같은 출처(weniversity.co.kr/tools/world/app/)로 위니브월드를 iframe에 띄운다.
// host.js 가 '부모가 같은 출처이고 ?embed=weniversity' 일 때만 WENIV_WORLD_HOST를 'weniversity'로 정하므로,
// 다른 사이트가 위니브월드를 띄워도 여기서는 아무것도 보내지 않는다. 받는 쪽도 같은 출처인지 다시 확인한다.
//
// 보내는 메시지 (모두 { source: 'weniv-world', version: 1, type, ... })
//   ready          앱이 준비됨 (스토리 목록을 불러온 뒤)
//   story-cleared  스토리 제출 통과 { storyId, attempts } — attempts는 이 브라우저에서 센 제출 횟수
//
// 위니버시티는 로그인한 사람이면 통과 기록을 계정에 남긴다. 답안 코드는 보내지 않는다.

export const MESSAGE_SOURCE = 'weniv-world';
export const MESSAGE_VERSION = 1;

export const isEmbedded = () => window.WENIV_WORLD_HOST === 'weniversity';

export function notifyHost(type, payload = {}) {
    if (!isEmbedded()) return false;
    try {
        window.parent.postMessage(
            { source: MESSAGE_SOURCE, version: MESSAGE_VERSION, type, ...payload },
            window.location.origin,
        );
        return true;
    } catch (e) {
        return false;
    }
}
