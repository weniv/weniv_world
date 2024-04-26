const BASE_URL = 'https://www.analytics.weniv.co.kr';

function collectPageView() {
    fetch(`${BASE_URL}/collect/pageview`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: window.location.href }),
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then((data) => {
            sessionStorage.setItem('session_id', data.session_id);
        })
        .catch((error) => console.error('Error:', error));
}
window.addEventListener('load', collectPageView);

function collectAnchorClick(event) {
    const ANCHOR = event.target.closest('a');
    if (ANCHOR) {
        event.preventDefault(); // 기본 동작 막기

        const session_id = sessionStorage.getItem('session_id');

        const source_url = window.location.href;
        const target_url = ANCHOR.href;
        const target_tar = ANCHOR.target || '_self';

        fetch(`${BASE_URL}/collect/anchor-click`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Session-Id': session_id,
            },
            body: JSON.stringify({ source_url, target_url }),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then((data) => {
                window.open(target_url, target_tar);
            })
            .catch((error) => console.error('Error:', error));
    }
}

document.addEventListener('click', (event) => {
    if (event.target.closest('a')) {
        collectAnchorClick(event);
    }
});
