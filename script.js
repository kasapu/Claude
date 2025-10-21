// DOM Elements
const dateInput = document.getElementById('note-date');
const noteContent = document.getElementById('note-content');
const saveBtn = document.getElementById('save-btn');
const clearBtn = document.getElementById('clear-btn');
const deleteBtn = document.getElementById('delete-btn');
const notesList = document.getElementById('notes-list');

// Initialize app
let notes = loadNotes();
let currentDate = getTodayDate();

// Set today's date as default
dateInput.value = currentDate;

// Load note for today if it exists
loadNoteForDate(currentDate);

// Display all saved notes
displayNotes();

// Event Listeners
saveBtn.addEventListener('click', saveNote);
clearBtn.addEventListener('click', clearForm);
deleteBtn.addEventListener('click', deleteNote);
dateInput.addEventListener('change', function() {
    currentDate = dateInput.value;
    loadNoteForDate(currentDate);
});

// Functions
function getTodayDate() {
    const today = new Date();
    return today.toISOString().split('T')[0];
}

function loadNotes() {
    const savedNotes = localStorage.getItem('dailyNotes');
    return savedNotes ? JSON.parse(savedNotes) : {};
}

function saveNotes() {
    localStorage.setItem('dailyNotes', JSON.stringify(notes));
}

function saveNote() {
    const date = dateInput.value;
    const content = noteContent.value.trim();

    if (!date) {
        alert('Please select a date');
        return;
    }

    if (!content) {
        alert('Please write something before saving');
        return;
    }

    notes[date] = {
        content: content,
        lastModified: new Date().toISOString()
    };

    saveNotes();
    displayNotes();

    // Show success message
    showMessage('Note saved successfully!');
}

function deleteNote() {
    const date = dateInput.value;

    if (!notes[date]) {
        alert('No note exists for this date');
        return;
    }

    if (confirm(`Are you sure you want to delete the note for ${formatDate(date)}?`)) {
        delete notes[date];
        saveNotes();
        noteContent.value = '';
        displayNotes();
        showMessage('Note deleted successfully!');
    }
}

function clearForm() {
    noteContent.value = '';
    noteContent.focus();
}

function loadNoteForDate(date) {
    if (notes[date]) {
        noteContent.value = notes[date].content;
    } else {
        noteContent.value = '';
    }
    noteContent.focus();
}

function displayNotes() {
    if (Object.keys(notes).length === 0) {
        notesList.innerHTML = '<p class="empty-state">No notes saved yet. Start writing!</p>';
        return;
    }

    // Sort notes by date (newest first)
    const sortedDates = Object.keys(notes).sort().reverse();

    notesList.innerHTML = sortedDates.map(date => {
        const note = notes[date];
        const isActive = date === dateInput.value;

        return `
            <div class="note-item ${isActive ? 'active' : ''}" onclick="selectNote('${date}')">
                <div class="note-date">${formatDate(date)}</div>
                <div class="note-preview">${escapeHtml(note.content)}</div>
            </div>
        `;
    }).join('');
}

function selectNote(date) {
    dateInput.value = date;
    currentDate = date;
    loadNoteForDate(date);
    displayNotes();
}

function formatDate(dateString) {
    const date = new Date(dateString + 'T00:00:00');
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function showMessage(message) {
    const existingMessage = document.querySelector('.success-message');
    if (existingMessage) {
        existingMessage.remove();
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = 'success-message';
    messageDiv.textContent = message;
    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #10b981;
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    `;

    document.body.appendChild(messageDiv);

    setTimeout(() => {
        messageDiv.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => messageDiv.remove(), 300);
    }, 2000);
}

// Add CSS animations for messages
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+S or Cmd+S to save
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        saveNote();
    }
});
