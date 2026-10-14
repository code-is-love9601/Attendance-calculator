document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".message").forEach((message) => {
        setTimeout(() => {
            message.style.transition = "opacity 0.4s ease";
            message.style.opacity = "0.8";
        }, 4000);
    });
});
