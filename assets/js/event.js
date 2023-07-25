const $btnQue = document.querySelectorAll(".btn-que");

// tutorial 로딩
$btnQue.forEach((element) => {
    element.addEventListener("click", function (e) {
        document.getElementById("t" + PAGE_NAME).classList.remove("active");
        PAGE_NAME = e.target.id.slice(1);
        document.getElementById("t" + PAGE_NAME).classList.add("active");
        history.pushState(null, PAGE_NAME, `?page=${PAGE_NAME}`);
        // // 문제 이동 시 에러 메시지 초기화
        // document.getElementById("result_desc").textContent = "";
        render(); // parser에 문제 렌더링
    });
});