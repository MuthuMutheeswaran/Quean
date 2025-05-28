document.getElementById("quiz-form").addEventListener("submit", async function (e) {
  e.preventDefault();

  const data = {
    questions: document.getElementById("question-count").value,
    options: document.getElementById("option-count").value,
    difficulty: document.getElementById("difficulty").value,
    topic: document.getElementById("topic").value
  };

  const res = await fetch("/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });

  const output = await res.json();

  if (output.error) {
    document.getElementById("output").innerText = "Error: " + output.error;
    document.getElementById("download-link").style.display = "none";
  } else {
    document.getElementById("output").innerText = output.questions;

    // enable download
    const downloadLink = document.getElementById("download-link");
    downloadLink.href = "/download/" + output.file;
    downloadLink.style.display = "inline-block";
  }
});
