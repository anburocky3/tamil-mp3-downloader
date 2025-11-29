document.addEventListener("DOMContentLoaded", () => {
  const devToggle = document.querySelector("#developerToggle");

  devToggle.addEventListener("change", (e) => {
    const devDoc = document.querySelector("#developer-documentation");
    const newbieDoc = document.querySelector("#newbie-documentation");

    if (devToggle.checked) {
      console.log("Show Dev contents");
      newbieDoc.classList.add("d-none");
      devDoc.classList.remove("d-none");
      devDoc.classList.add("d-block");
    } else {
      console.log("Show newbie");
      devDoc.classList.add("d-none");
      newbieDoc.classList.remove("d-none");
    }
  });
});
