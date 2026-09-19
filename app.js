// ተጠቃሚው ቁጥር መርጦ ባላንሱን አረጋግጦ ስታርት ሲል ወደ ጨዋታው የሚያስገባ
document.addEventListener("DOMContentLoaded", () => {
    const grid = document.getElementById("numbers-grid");
    const startBtn = document.getElementById("start-game-btn");
    let selectedBoard = null;

    // ከ1 እስከ 200 ቁጥሮችን መፍጠር
    for (let i = 1; i <= 200; i++) {
        const btn = document.createElement("button");
        btn.classList.add("num-cell");
        btn.innerText = i;
        btn.addEventListener("click", () => {
            document.querySelectorAll(".num-cell").forEach(b => b.classList.remove("selected"));
            btn.classList.add("selected");
            selectedBoard = i;
            startBtn.disabled = false;
        });
        grid.appendChild(btn);
    }

    startBtn.addEventListener("click", () => {
        if (selectedBoard) {
            alert(`ቦርድ ቁጥር ${selectedBoard} ተመርጧል። ጨዋታው ይጀመራል!`);
            // ወደ ጨዋታ ማያ ገጽ ማሸጋገር
            document.getElementById("board-selection").style.display = "none";
            document.getElementById("game-play-section").style.display = "block";
        }
    });

    // ቢንጎ ማረጋገጫ ቁልፍ ሎጂክ
    document.getElementById("bingo-claim-btn").addEventListener("click", () => {
        // ቦቱ ትክክለኛ መሆኑን አረጋግጦ ቢንጎ ወይም ከዙር የሚያባርርበት ጥያቄ
        fetch('/api/check-bingo', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if(data.isBingo) {
                    alert("እንኳን ደስ አለዎት! ትክክለኛ ቢንጎ ነው!");
                } else {
                    alert("የተሳሳተ ቢንጎ! ከዚህ ዙር ውጪ ሆናለ።");
                }
            });
    });
});
