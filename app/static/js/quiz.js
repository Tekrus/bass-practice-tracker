let currentQuiz = null;
let quizType = window.initialQuizType || 'fretboard';
let startTime = null;

// Note names for fretboard
const notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
const openStrings = ['G', 'D', 'A', 'E'];  // String 1 to 4

function getNoteAtFret(stringNum, fret) {
    const openNote = openStrings[stringNum - 1];
    const openIndex = notes.indexOf(openNote);
    return notes[(openIndex + fret) % 12];
}

function drawFretboard(highlightString, highlightFret) {
    const svg = document.getElementById('fretboardSvg');
    if (!svg) return;

    const fretCount = 12;
    const stringCount = 4;
    const startX = 40;
    const startY = 20;
    const fretWidth = 35;
    const stringSpacing = 25;

    let html = '';

    // Draw nut
    html += `<rect x="${startX}" y="${startY}" width="4" height="${(stringCount - 1) * stringSpacing}" fill="#d4a574"/>`;

    // Draw frets
    for (let f = 1; f <= fretCount; f++) {
        const x = startX + f * fretWidth;
        html += `<line x1="${x}" y1="${startY}" x2="${x}" y2="${startY + (stringCount - 1) * stringSpacing}" stroke="#888" stroke-width="2"/>`;

        // Fret number
        html += `<text x="${x - fretWidth / 2}" y="${startY + (stringCount - 1) * stringSpacing + 18}" text-anchor="middle" fill="#888" font-size="10">${f}</text>`;
    }

    // Draw fret markers (dots)
    const markerFrets = [3, 5, 7, 9, 12];
    markerFrets.forEach(f => {
        const x = startX + (f - 0.5) * fretWidth;
        const y = startY + (stringCount - 1) * stringSpacing / 2;
        if (f === 12) {
            html += `<circle cx="${x}" cy="${y - 12}" r="4" fill="#555"/>`;
            html += `<circle cx="${x}" cy="${y + 12}" r="4" fill="#555"/>`;
        } else {
            html += `<circle cx="${x}" cy="${y}" r="4" fill="#555"/>`;
        }
    });

    // Draw strings
    for (let s = 0; s < stringCount; s++) {
        const y = startY + s * stringSpacing;
        const thickness = 1 + s * 0.5;
        html += `<line x1="${startX}" y1="${y}" x2="${startX + fretCount * fretWidth}" y2="${y}" stroke="#ccc" stroke-width="${thickness}"/>`;

        // String label
        html += `<text x="${startX - 20}" y="${y + 4}" text-anchor="middle" fill="#aaa" font-size="12">${openStrings[s]}</text>`;
    }

    // Highlight the target position
    if (highlightString && highlightFret !== undefined) {
        const x = highlightFret === 0 ? startX - 10 : startX + (highlightFret - 0.5) * fretWidth;
        const y = startY + (highlightString - 1) * stringSpacing;
        html += `<circle cx="${x}" cy="${y}" r="10" fill="#0d6efd" stroke="#fff" stroke-width="2"/>`;
        html += `<text x="${x}" y="${y + 4}" text-anchor="middle" fill="#fff" font-size="10" font-weight="bold">?</text>`;
    }

    svg.innerHTML = html;
}

function drawTab(stringNum, fret) {
    const tabDiv = document.getElementById('tabNotation');
    if (!tabDiv) return;

    let lines = ['G|', 'D|', 'A|', 'E|'];

    const dashCount = 5;
    for (let i = 0; i < 4; i++) {
        for (let j = 0; j < dashCount; j++) {
            if (j === Math.floor(dashCount / 2) && i === stringNum - 1) {
                lines[i] += fret.toString().padStart(2, '-');
            } else {
                lines[i] += '--';
            }
        }
        lines[i] += '|';
    }

    tabDiv.textContent = lines.join('\n');
}

const newQuestionBtn = document.getElementById('newQuestionBtn');
if (newQuestionBtn) newQuestionBtn.addEventListener('click', loadNewQuestion);

document.querySelectorAll('.quiz-type-btn').forEach(btn => {
    btn.addEventListener('click', function () {
        document.querySelectorAll('.quiz-type-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        quizType = this.dataset.type;
        loadNewQuestion();
    });
});

function loadNewQuestion() {
    fetch(`/quiz/question?type=${quizType}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                const title = document.getElementById('quizTitle');
                const question = document.getElementById('quizQuestion');
                if (title) title.textContent = 'No questions available';
                if (question) question.textContent = 'Try selecting a different quiz type.';
                const optionsArea = document.getElementById('optionsArea');
                const fretboardDisplay = document.getElementById('fretboardDisplay');
                const tabDisplay = document.getElementById('tabDisplay');
                if (optionsArea) optionsArea.classList.add('d-none');
                if (fretboardDisplay) fretboardDisplay.classList.add('d-none');
                if (tabDisplay) tabDisplay.classList.add('d-none');
                currentQuiz = null;
                return;
            }

            currentQuiz = data;
            startTime = Date.now();

            // Update level display
            const currentLevel = document.getElementById('currentLevel');
            if (data.difficulty && currentLevel) {
                currentLevel.textContent = data.difficulty;
            }

            const quizTitle = document.getElementById('quizTitle');
            const quizQuestion = document.getElementById('quizQuestion');
            if (quizTitle) quizTitle.textContent = data.title;
            if (quizQuestion) quizQuestion.textContent = data.question;

            // Handle fretboard display
            const fretboardDisplay = document.getElementById('fretboardDisplay');
            const tabDisplay = document.getElementById('tabDisplay');
            if (data.type === 'fretboard' && data.string_number && data.fret_number !== null) {
                if (fretboardDisplay) fretboardDisplay.classList.remove('d-none');
                if (tabDisplay) tabDisplay.classList.remove('d-none');
                drawFretboard(data.string_number, data.fret_number);
                drawTab(data.string_number, data.fret_number);
            } else {
                if (fretboardDisplay) fretboardDisplay.classList.add('d-none');
                if (tabDisplay) tabDisplay.classList.add('d-none');
            }

            // Parse options
            let options;
            try {
                options = typeof data.options === 'string' ? JSON.parse(data.options) : data.options;
            } catch (e) {
                console.error('Error parsing options:', e);
                options = [];
            }

            // Create option buttons
            const optionsArea = document.getElementById('answerOptions');
            if (optionsArea) {
                optionsArea.innerHTML = '';

                options.forEach(opt => {
                    const btn = document.createElement('button');
                    btn.className = 'btn btn-outline-primary btn-lg m-1';
                    btn.textContent = opt;
                    btn.onclick = () => submitAnswer(opt);
                    optionsArea.appendChild(btn);
                });
            }

            const optionsAreaContainer = document.getElementById('optionsArea');
            if (optionsAreaContainer) optionsAreaContainer.classList.remove('d-none');
            const resultArea = document.getElementById('resultArea');
            if (resultArea) resultArea.classList.add('d-none');
        })
        .catch(err => {
            console.error('Error loading question:', err);
            const quizTitle = document.getElementById('quizTitle');
            const quizQuestion = document.getElementById('quizQuestion');
            if (quizTitle) quizTitle.textContent = 'Error loading question';
            if (quizQuestion) quizQuestion.textContent = 'Please try again.';
        });
}

function submitAnswer(answer) {
    if (!currentQuiz) return;

    const responseTime = startTime ? Date.now() - startTime : 0;

    fetch('/quiz/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            quiz_id: currentQuiz.id,
            answer: answer,
            response_time: responseTime
        })
    })
        .then(response => response.json())
        .then(data => {
            const resultArea = document.getElementById('resultArea');
            const resultMessage = document.getElementById('resultMessage');
            const explanation = document.getElementById('explanation');

            if (resultArea) resultArea.classList.remove('d-none');

            if (resultMessage) {
                if (data.correct) {
                    resultMessage.className = 'alert alert-success';
                    resultMessage.innerHTML = `<i class="bi bi-check-circle-fill"></i> Correct! The answer is <strong>${data.correct_answer}</strong>`;
                } else {
                    resultMessage.className = 'alert alert-danger';
                    resultMessage.innerHTML = `<i class="bi bi-x-circle-fill"></i> Incorrect. The answer was: <strong>${data.correct_answer}</strong>`;
                }
            }

            if (explanation) {
                if (data.explanation) {
                    explanation.textContent = data.explanation;
                    explanation.classList.remove('d-none');
                } else {
                    explanation.classList.add('d-none');
                }
            }

            // Auto-load next question after 3 seconds
            setTimeout(loadNewQuestion, 3000);
        })
        .catch(err => {
            console.error('Error submitting answer:', err);
        });
}

// Load initial question when page loads
document.addEventListener('DOMContentLoaded', () => {
    loadNewQuestion();
});
