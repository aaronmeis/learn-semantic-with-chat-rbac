// Video tab removed - slides only

// Slides setup - using images instead of PDF
let slides = [];
let currentSlide = 0;
let autoplayInterval = null;
let autoplaySpeed = 3000; // 3 seconds per slide
let slidesLoaded = false;

const slideImage = document.getElementById('slide-image');
const slidesContainer = document.querySelector('.slides-container');

// Discover slides by trying to load images
async function discoverSlides() {
    const discoveredSlides = [];
    let slideNum = 1;
    let consecutiveFailures = 0;
    const maxFailures = 3; // Stop after 3 consecutive failures
    
    while (consecutiveFailures < maxFailures) {
        const slidePath = `slides/slide-${String(slideNum).padStart(3, '0')}.png`;
        
        try {
            const exists = await checkImageExists(slidePath);
            if (exists) {
                discoveredSlides.push(slidePath);
                consecutiveFailures = 0;
                slideNum++;
            } else {
                consecutiveFailures++;
                if (consecutiveFailures < maxFailures) {
                    slideNum++;
                }
            }
        } catch (error) {
            consecutiveFailures++;
            if (consecutiveFailures < maxFailures) {
                slideNum++;
            }
        }
    }
    
    return discoveredSlides;
}

// Check if an image exists
function checkImageExists(url) {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => resolve(true);
        img.onerror = () => resolve(false);
        img.src = url;
        // Timeout after 2 seconds
        setTimeout(() => resolve(false), 2000);
    });
}

// Load slides
async function loadSlides() {
    if (slidesLoaded) return;
    
    // Show loading message
    const loadingMsg = document.createElement('div');
    loadingMsg.id = 'loading-msg';
    loadingMsg.style.cssText = 'text-align: center; padding: 50px; color: #666; font-size: 1.2em;';
    loadingMsg.textContent = 'Loading slides...';
    slidesContainer.insertBefore(loadingMsg, slideImage);
    
    try {
        slides = await discoverSlides();
        
        if (slides.length === 0) {
            // Try alternative naming convention
            for (let i = 1; i <= 200; i++) {
                const altPath = `slide-${String(i).padStart(3, '0')}.png`;
                const exists = await checkImageExists(altPath);
                if (exists) {
                    slides.push(altPath);
                } else if (slides.length > 0) {
                    // If we found some slides but this one doesn't exist, we're done
                    break;
                }
            }
        }
        
        const loadingMsgEl = document.getElementById('loading-msg');
        if (loadingMsgEl) {
            loadingMsgEl.remove();
        }
        
        if (slides.length === 0) {
            slideImage.style.display = 'none';
            const errorMsg = document.createElement('div');
            errorMsg.style.cssText = 'text-align: center; padding: 50px; color: #dc2626; font-size: 1.1em; background: #fef2f2; border: 1px solid #fecaca; border-radius: 6px;';
            errorMsg.innerHTML = `
                <h3 style="color: #991b1b; margin-bottom: 15px; font-size: 1.3em;">No Slides Found</h3>
                <p style="color: #7f1d1d; margin-bottom: 20px;">Please convert your PDF to images first.</p>
                <div style="background: white; padding: 20px; border-radius: 4px; margin: 20px 0; text-align: left; max-width: 600px; margin-left: auto; margin-right: auto;">
                    <p style="color: #1e293b; font-weight: 600; margin-bottom: 10px;">Quick Steps:</p>
                    <ol style="color: #475569; line-height: 1.8; margin-left: 20px;">
                        <li>Open <a href="convert-pdf-to-images.html" style="color: #1e40af; text-decoration: underline;" target="_blank">convert-pdf-to-images.html</a> in your browser</li>
                        <li>Select <code style="background: #f1f5f9; padding: 2px 6px; border-radius: 3px;">Engineering_Production_AI_Systems.pdf</code></li>
                        <li>Click "Convert PDF"</li>
                        <li>Download each image and save to <code style="background: #f1f5f9; padding: 2px 6px; border-radius: 3px;">slides/</code> folder as <code style="background: #f1f5f9; padding: 2px 6px; border-radius: 3px;">slide-001.png</code>, <code style="background: #f1f5f9; padding: 2px 6px; border-radius: 3px;">slide-002.png</code>, etc.</li>
                        <li>Refresh this page</li>
                    </ol>
                </div>
                <p style="font-size: 0.9em; color: #64748b; margin-top: 20px;">
                    See <code style="background: #f1f5f9; padding: 2px 6px; border-radius: 3px;">CONVERT_SLIDES.md</code> for detailed instructions.
                </p>
            `;
            slidesContainer.insertBefore(errorMsg, slideImage);
            return;
        }
        
        console.log(`Found ${slides.length} slides`);
        slidesLoaded = true;
        currentSlide = 0;
        showSlide(0);
        startAutoplay();
    } catch (error) {
        console.error('Error loading slides:', error);
        const loadingMsgEl = document.getElementById('loading-msg');
        if (loadingMsgEl) {
            loadingMsgEl.textContent = `Error loading slides: ${error.message}`;
            loadingMsgEl.style.color = '#dc3545';
        }
    }
}

// Show a specific slide
function showSlide(index) {
    if (slides.length === 0) return;
    
    if (index < 0) index = 0;
    if (index >= slides.length) index = slides.length - 1;
    
    currentSlide = index;
    slideImage.src = slides[currentSlide];
    slideImage.style.display = 'block';
    
    document.getElementById('slide-counter').textContent = `${currentSlide + 1} / ${slides.length}`;
    
    // Update button states
    document.getElementById('prev-slide').disabled = currentSlide === 0;
    document.getElementById('next-slide').disabled = currentSlide === slides.length - 1;
}

// Previous slide
function onPrevSlide() {
    if (currentSlide > 0) {
        showSlide(currentSlide - 1);
        resetAutoplay();
    }
}

// Next slide
function onNextSlide() {
    if (currentSlide < slides.length - 1) {
        showSlide(currentSlide + 1);
        resetAutoplay();
    }
}

// Autoplay functionality
function startAutoplay() {
    if (autoplayInterval || slides.length === 0) return;
    
    autoplayInterval = setInterval(() => {
        if (currentSlide < slides.length - 1) {
            showSlide(currentSlide + 1);
        } else {
            // Loop back to first slide
            showSlide(0);
        }
    }, autoplaySpeed);
    
    updateAutoplayButton(true);
}

function stopAutoplay() {
    if (autoplayInterval) {
        clearInterval(autoplayInterval);
        autoplayInterval = null;
        updateAutoplayButton(false);
    }
}

function resetAutoplay() {
    stopAutoplay();
    startAutoplay();
}

function toggleAutoplay() {
    if (autoplayInterval) {
        stopAutoplay();
    } else {
        startAutoplay();
    }
}

function updateAutoplayButton(isPlaying) {
    const btn = document.getElementById('toggle-autoplay');
    if (btn) {
        if (isPlaying) {
            btn.textContent = 'Pause';
            btn.classList.remove('paused');
        } else {
            btn.textContent = 'Play';
            btn.classList.add('paused');
        }
    }
}

// Event listeners
document.getElementById('prev-slide').addEventListener('click', onPrevSlide);
document.getElementById('next-slide').addEventListener('click', onNextSlide);
document.getElementById('toggle-autoplay').addEventListener('click', toggleAutoplay);

// Load slides automatically since slides is the default tab
let slidesInitialized = false;

// Ensure DOM is ready before setting up event listeners
function setupEventListeners() {
    // Check if slides tab is active (default)
    const slidesTab = document.getElementById('slides-tab');
    if (slidesTab && slidesTab.classList.contains('active')) {
        // Load slides automatically since it's the default tab
        setTimeout(() => {
            if (!slidesInitialized) {
                loadSlides();
                slidesInitialized = true;
            }
        }, 100);
    }
    
    // Also load slides when slides tab is clicked (in case user switches away and back)
    const slidesTabButton = document.querySelector('[data-tab="slides"]');
    if (slidesTabButton) {
        slidesTabButton.addEventListener('click', () => {
            if (!slidesInitialized) {
                // Wait a bit for the tab to be visible, then load slides
                setTimeout(() => {
                    loadSlides();
                    slidesInitialized = true;
                }, 100);
            }
        });
    }
}

// Run setup when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupEventListeners);
} else {
    setupEventListeners();
}

// Keyboard navigation
document.addEventListener('keydown', (e) => {
    const slidesTab = document.getElementById('slides-tab');
    if (slidesTab.classList.contains('active') && slides.length > 0) {
        if (e.key === 'ArrowLeft') {
            onPrevSlide();
        } else if (e.key === 'ArrowRight') {
            onNextSlide();
        } else if (e.key === ' ') {
            e.preventDefault();
            toggleAutoplay();
        }
    }
});
