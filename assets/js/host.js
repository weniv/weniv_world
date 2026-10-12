// 위니브월드가 어디에서 열렸는지 정합니다. 다른 스크립트보다 먼저 불러옵니다(index.html <head> 맨 위).
//
//  web         world.weniv.co.kr 등에서 단독으로 연 경우 (기본)
//  weniversity 위니버시티 학습 도구(/tools/world) 안의 iframe으로 연 경우
//              - 주소에 ?embed=weniversity 가 있고, 부모 창이 같은 출처일 때만 (다른 사이트가 띄우면 web)
//  desktop     설치판(Electron) 앱 — 앱 전용 주소(weniv-world://)로 열린다
//
// 결과는 <html data-host="..."> 와 window.WENIV_WORLD_HOST 에 둡니다.
// CSS는 [data-host='weniversity'] 로 화면을 조금 바꾸고, analytics.js·gtag는 web에서만 방문을 셉니다.
(function () {
    var host = 'web';
    if (location.protocol === 'weniv-world:') {
        host = 'desktop';
    } else {
        try {
            var embed = new URLSearchParams(location.search).get('embed');
            // 다른 출처의 부모 창이면 parent.location.origin을 읽을 때 오류가 나서 web으로 남는다
            if (
                embed === 'weniversity' &&
                window.parent !== window &&
                window.parent.location.origin === location.origin
            ) {
                host = 'weniversity';
            }
        } catch (e) {
            host = 'web';
        }
    }
    window.WENIV_WORLD_HOST = host;
    document.documentElement.setAttribute('data-host', host);
})();
