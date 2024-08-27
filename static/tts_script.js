const playBtn = document.getElementById('play-btn');
const pauseBtn = document.getElementById('pause-btn');
const fullText = document.getElementById('full-text').textContent;

playBtn.addEventListener('click', () => {
    console.log("Play is Clicked")
    fetch('/speak', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: fullText })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log('Speech synthesis started.');
        } else {
            console.error('Error:', data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
