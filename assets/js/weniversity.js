// 위니버시티 안내
// 위니브월드는 위니버시티 학습 도구 > 위니브월드에서도 할 수 있다(로그인하면 진행률·인증서가 계정에 남음).
// 웹(world.weniv.co.kr)으로 연 사람에게만 처음 한 번 안내 창을 띄우고(닫으면 다시 띄우지 않음),
// data-wv-track 링크 클릭을 애널리틱스에 남긴다. 설치판·위니버시티 안에서는 띄우지 않는다.
(function () {
  if ((window.WENIV_WORLD_HOST || "web") !== "web") return;
  const WORLD_URL = "https://weniversity.co.kr/tools/world/";
  const NOTICE_KEY = "weniversity-moved-notice";

  function sendClick(link, type) {
    try {
      fetch("https://dev.wenivops.co.kr/api/weniv_analytics/collect/anchor-click", {
        method: "POST",
        keepalive: true,
        headers: {
          "Content-Type": "application/json",
          "Session-Id": sessionStorage.getItem("session_id") || "",
        },
        body: JSON.stringify({
          source_url: location.href,
          target_url: link,
          type: `위니브월드: ${type}`,
        }),
      }).catch(() => {});
    } catch (e) {
      /* 수집 실패는 이동에 영향을 주지 않는다 */
    }
  }

  function bindLinks(root) {
    root.querySelectorAll("a[data-wv-track]").forEach((a) => {
      a.addEventListener("click", () => sendClick(a.href, a.dataset.wvTrack));
    });
  }

  function readNotice() {
    try {
      return localStorage.getItem(NOTICE_KEY);
    } catch (e) {
      return "1";
    }
  }

  function showNotice() {
    if (readNotice()) return;

    const notice = document.createElement("div");
    notice.className = "wv-notice";
    notice.setAttribute("role", "dialog");
    notice.setAttribute("aria-labelledby", "wv-notice-title");
    notice.innerHTML = `
      <button type="button" class="wv-notice__close" aria-label="안내 닫기">
        <svg viewBox="0 0 20 20" aria-hidden="true"><path d="M5 5l10 10M15 5L5 15" /></svg>
      </button>
      <p class="wv-notice__eyebrow">weniversity</p>
      <strong id="wv-notice-title" class="wv-notice__title">위니브월드, 이제 위니버시티에서도 해요</strong>
      <p class="wv-notice__desc">
        위니버시티에 로그인하고 하면 진행률과 인증서가 계정에 남아 어느 기기에서든 이어서 할 수 있어요.
        교재와 다른 학습 도구도 한곳에서 만나 보세요.
      </p>
      <div class="wv-notice__actions">
        <a class="wv-notice__go" data-wv-track="안내 창 > 위니버시티 위니브월드" href="${WORLD_URL}">위니버시티에서 하기</a>
        <button type="button" class="wv-notice__stay">여기서 계속하기</button>
      </div>
    `;

    const close = () => {
      try {
        localStorage.setItem(NOTICE_KEY, new Date().toISOString());
      } catch (e) {
        /* 저장이 막혀 있으면 다음에 다시 보일 뿐이다 */
      }
      notice.classList.add("is-hidden");
      setTimeout(() => notice.remove(), 300);
    };

    notice.querySelector(".wv-notice__close").addEventListener("click", close);
    notice.querySelector(".wv-notice__stay").addEventListener("click", close);
    notice.querySelector(".wv-notice__go").addEventListener("click", close);
    document.addEventListener("keydown", function onKey(e) {
      if (e.key === "Escape" && document.body.contains(notice)) {
        close();
        document.removeEventListener("keydown", onKey);
      }
    });

    document.body.appendChild(notice);
    bindLinks(notice);
    requestAnimationFrame(() => notice.classList.add("is-shown"));
  }

  function init() {
    bindLinks(document);
    setTimeout(showNotice, 1200);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
