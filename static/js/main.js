// main.js — students will add JavaScript here as features are built

document.addEventListener("DOMContentLoaded", function () {
    var openBtn = document.getElementById("demo-video-btn");
    var overlay = document.getElementById("demo-modal-overlay");
    var closeBtn = document.getElementById("demo-modal-close");
    var iframe = document.getElementById("demo-modal-iframe");

    if (!openBtn || !overlay || !closeBtn || !iframe) {
        return;
    }

    var videoSrc = iframe.getAttribute("data-src");

    function openModal() {
        iframe.src = videoSrc + "?autoplay=1";
        overlay.hidden = false;
    }

    function closeModal() {
        overlay.hidden = true;
        iframe.src = "";
    }

    openBtn.addEventListener("click", openModal);
    closeBtn.addEventListener("click", closeModal);

    overlay.addEventListener("click", function (event) {
        if (event.target === overlay) {
            closeModal();
        }
    });
});
