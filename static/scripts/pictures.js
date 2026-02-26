// ── Gallery batching ──────────────────────────────────────────────────────────
const BATCH_SIZE = 15;
let allImages = [];
let loadedCount = 0;
let isAdmin = false;

function initGallery(images, adminFlag) {
    allImages = images;
    isAdmin = adminFlag;
    loadNextBatch();
    updateLoadMoreButton();
}

function loadNextBatch() {
    const batch = allImages.slice(loadedCount, loadedCount + BATCH_SIZE);
    batch.forEach(img => addImageToGallery(img.filename, img.title, img.description));
    loadedCount += batch.length;
    updateLoadMoreButton();
}

function updateLoadMoreButton() {
    const btn = document.getElementById('loadMoreBtn');
    if (!btn) return;
    if (loadedCount >= allImages.length) {
        btn.style.display = 'none';
    } else {
        btn.style.display = 'inline-flex';
        const remaining = allImages.length - loadedCount;
        btn.textContent = `Load More (${remaining} remaining)`;
    }
}

// ── addImageToGallery ─────────────────────────────────────────────────────────
function addImageToGallery(filename, title, description, prepend) {
    title = title || filename;
    description = description || '';

    const emptyGallery = document.querySelector('.empty-gallery');
    if (emptyGallery) emptyGallery.remove();

    let gallery = document.querySelector('.gallery-grid');
    if (!gallery) {
        gallery = document.createElement('div');
        gallery.className = 'gallery-grid';
        const container = document.querySelector('.pictures-section .container');
        const dropZone = document.getElementById('dropZone');
        const loadMore = document.getElementById('loadMoreBtn');
        if (dropZone) {
            dropZone.insertAdjacentElement('afterend', gallery);
        } else if (loadMore) {
            loadMore.insertAdjacentElement('beforebegin', gallery);
        } else {
            container.appendChild(gallery);
        }
    }

    const imageUrl = `/data/pictures/${filename}`;
    const galleryItem = document.createElement('div');
    galleryItem.className = 'gallery-item';
    galleryItem.setAttribute('data-filename', filename);
    if (prepend) galleryItem.style.animation = 'fadeInUp 0.5s ease-out';

    const adminButtons = isAdmin ? `
        <button class="icon-btn edit-btn" onclick="editImage(this, '${esc(filename)}')" title="Edit">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
        </button>` : '';

    const adminActions = isAdmin ? `
        <div class="admin-actions" style="display:none;">
            <button class="icon-btn save-btn" onclick="saveImage(this, '${esc(filename)}')" title="Save">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="20 6 9 17 4 12"/>
                </svg>
            </button>
            <button class="icon-btn cancel-btn" onclick="cancelEdit(this)" title="Cancel">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
            </button>
            <button class="icon-btn delete-btn" onclick="deleteImage(this, '${esc(filename)}')" title="Delete">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"/>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
            </button>
        </div>` : '';

    galleryItem.innerHTML = `
        <img src="${imageUrl}" alt="${esc(title)}" loading="lazy"
             onclick="openLightbox('${imageUrl}', '${escJs(title)}', '${escJs(description)}')">
        <div class="image-info">
            <div class="image-title-wrapper">
                <h3 class="image-title" data-original="${esc(title)}">${esc(title)}</h3>
                ${adminButtons}
            </div>
            <p class="image-description" data-original="${esc(description)}">${esc(description)}</p>
            ${adminActions}
        </div>`;

    if (prepend) {
        gallery.insertBefore(galleryItem, gallery.firstChild);
    } else {
        gallery.appendChild(galleryItem);
    }
}

function esc(str) {
    return String(str)
        .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
        .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}
function escJs(str) {
    return String(str).replace(/\\/g,'\\\\').replace(/'/g,"\\'").replace(/\n/g,'\\n');
}

// ── Lightbox ──────────────────────────────────────────────────────────────────
function openLightbox(src, title, description) {
    document.getElementById('lightbox-img').src = src;
    document.getElementById('lightbox-title').textContent = title;
    document.getElementById('lightbox-description').textContent = description;
    document.getElementById('lightbox').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}
function closeLightbox() {
    document.getElementById('lightbox').style.display = 'none';
    document.body.style.overflow = 'auto';
}
document.addEventListener('keydown', e => { if (e.key === 'Escape') { closeLightbox(); closeConfirmModal(); } });

// ── Custom delete confirmation modal ─────────────────────────────────────────
let _pendingDeleteBtn = null;
let _pendingDeleteFilename = null;

function deleteImage(btn, filename) {
    _pendingDeleteBtn = btn;
    _pendingDeleteFilename = filename;
    const modal = document.getElementById('confirmModal');
    modal.style.display = 'flex';
}

function closeConfirmModal() {
    document.getElementById('confirmModal').style.display = 'none';
    _pendingDeleteBtn = null;
    _pendingDeleteFilename = null;
}

async function confirmDelete() {
    const btn = _pendingDeleteBtn;
    const filename = _pendingDeleteFilename;
    closeConfirmModal();
    if (!filename) return;

    try {
        const response = await fetch(`/admin/delete/${filename}`, { method: 'DELETE' });
        if (response.ok) {
            const item = btn.closest('.gallery-item');
            item.style.animation = 'fadeOut 0.3s ease-out';
            setTimeout(() => {
                item.remove();
                // Also remove from allImages array
                const idx = allImages.findIndex(i => i.filename === filename);
                if (idx !== -1) { allImages.splice(idx, 1); loadedCount = Math.max(0, loadedCount - 1); }
                const gallery = document.querySelector('.gallery-grid');
                if (gallery && gallery.children.length === 0) location.reload();
            }, 300);
            showNotification('Image deleted successfully', 'success');
        } else {
            showNotification('Failed to delete image', 'error');
        }
    } catch (error) {
        showNotification('Error: ' + error.message, 'error');
    }
}

// ── Edit / Save / Cancel ──────────────────────────────────────────────────────
function editImage(btn, filename) {
    const item = btn.closest('.gallery-item');
    item.querySelector('.image-title').setAttribute('contenteditable', 'true');
    item.querySelector('.image-description').setAttribute('contenteditable', 'true');
    item.querySelector('.image-title').focus();
    btn.style.display = 'none';
    item.querySelector('.admin-actions').style.display = 'flex';
}
function cancelEdit(btn) {
    const item = btn.closest('.gallery-item');
    const titleEl = item.querySelector('.image-title');
    const descEl  = item.querySelector('.image-description');
    titleEl.textContent = titleEl.dataset.original;
    descEl.textContent  = descEl.dataset.original;
    titleEl.setAttribute('contenteditable', 'false');
    descEl.setAttribute('contenteditable',  'false');
    item.querySelector('.edit-btn').style.display = 'block';
    item.querySelector('.admin-actions').style.display = 'none';
}
async function saveImage(btn, filename) {
    const item = btn.closest('.gallery-item');
    const titleEl = item.querySelector('.image-title');
    const descEl  = item.querySelector('.image-description');
    const title = titleEl.textContent.trim();
    const description = descEl.textContent.trim();
    try {
        const response = await fetch('/admin/update-metadata', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-cache, no-store, must-revalidate', 'Pragma': 'no-cache' },
            body: JSON.stringify({ filename, title, description })
        });
        if (response.ok) {
            titleEl.dataset.original = title;
            descEl.dataset.original  = description;
            titleEl.setAttribute('contenteditable', 'false');
            descEl.setAttribute('contenteditable',  'false');
            item.querySelector('.edit-btn').style.display = 'block';
            item.querySelector('.admin-actions').style.display = 'none';
            const img = item.querySelector('img');
            img.setAttribute('onclick', `openLightbox('${img.src}','${escJs(title)}','${escJs(description)}')`);
            showNotification('Saved successfully!', 'success');
        } else {
            showNotification('Failed to save changes', 'error');
        }
    } catch (error) {
        showNotification('Error: ' + error.message, 'error');
    }
}

// ── Upload ────────────────────────────────────────────────────────────────────
async function uploadFile(file) {
    if (!file.type.startsWith('image/')) { showNotification('Only image files are allowed', 'error'); return; }
    const formData = new FormData();
    formData.append('file', file);
    try {
        showNotification('Uploading ' + file.name + '...', 'info');
        const response = await fetch('/admin/upload', { method: 'POST', body: formData });
        if (response.ok) {
            const data = await response.json();
            showNotification('Upload successful!', 'success');
            allImages.unshift({ filename: data.filename, title: data.filename, description: '' });
            loadedCount++;
            addImageToGallery(data.filename, data.filename, '', true);
        } else {
            const data = await response.json();
            showNotification('Upload failed: ' + data.error, 'error');
        }
    } catch (error) { showNotification('Error: ' + error.message, 'error'); }
}
async function uploadImage(input) {
    if (!input.files || !input.files[0]) return;
    await uploadFile(input.files[0]);
    input.value = '';
}

// ── Drag & drop ───────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    if (!dropZone) return;
    ['dragenter','dragover','dragleave','drop'].forEach(e => {
        dropZone.addEventListener(e, ev => { ev.preventDefault(); ev.stopPropagation(); }, false);
        document.body.addEventListener(e, ev => { ev.preventDefault(); ev.stopPropagation(); }, false);
    });
    ['dragenter','dragover'].forEach(e => dropZone.addEventListener(e, () => dropZone.classList.add('drop-zone-active')));
    ['dragleave','drop'].forEach(e => dropZone.addEventListener(e, () => dropZone.classList.remove('drop-zone-active')));
    dropZone.addEventListener('drop', e => [...e.dataTransfer.files].forEach(uploadFile));
});

// ── Notifications ─────────────────────────────────────────────────────────────
function showNotification(message, type) {
    const n = document.createElement('div');
    n.className = `notification notification-${type}`;
    n.textContent = message;
    document.body.appendChild(n);
    setTimeout(() => n.classList.add('show'), 10);
    setTimeout(() => { n.classList.remove('show'); setTimeout(() => n.remove(), 300); }, 3000);
}
