document.getElementById("upload-form").onsubmit = async function (event) {
    event.preventDefault();
    
    const formData = new FormData();
    const videoFile = document.querySelector('input[type="file"]').files[0];
    formData.append("video", videoFile);
    
    // 「準備中」と表示
    const messageElement = document.getElementById("message");
    messageElement.textContent = "準備中...... 2分ほど待ってね♪";
    
    const response = await fetch("/upload", {
        method: "POST",
        body: formData
    });
    
    const result = await response.json();
    
    // アップロードが成功した場合
    if (response.ok) {
        const videoElement = document.getElementById("output-video");
        videoElement.src = result.output_url;
        videoElement.style.display = "block";
        messageElement.textContent = result.message; // 成功メッセージを表示
    } else {
        // アップロードが失敗した場合
        messageElement.textContent = "アップロードに失敗しました。もう一度お試しください。";
    }
};
