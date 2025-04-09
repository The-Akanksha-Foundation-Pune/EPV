// Loading Screen JavaScript

// Global loading screen controller
const LoadingScreen = {
    // Store start time when showing the loading screen
    startTime: 0,
    // Minimum display time in milliseconds (ensures animation completes)
    minDisplayTime: 1000,
    // Animation duration in milliseconds (from CSS)
    animationDuration: 4000,
    // Reference to the loading screen element
    element: null,
    // CSS variables for animation control
    cssVars: {
        fillDuration: '--fill-duration'
    },
    // Track if we're currently measuring load time
    isMeasuring: false,
    // Store measured load times for different operations
    loadTimes: {
        login: 3, // Default starting value in seconds
        dashboard: 2,
        expenseForm: 2,
        dataLoad: 2
    },
    // Track the current operation being timed
    currentOperation: null,

    // Initialize the loading screen
    init: function() {
        this.element = document.getElementById('loadingScreen');

        // Set up default event listener for page load
        if (this.element) {
            window.addEventListener('load', function() {
                // If we were measuring, stop and record the time
                if (LoadingScreen.isMeasuring) {
                    LoadingScreen.stopMeasuring();
                }

                // Only hide automatically if we're on the login page and not measuring
                if ((window.location.pathname === '/' || window.location.pathname === '/login') && !LoadingScreen.isMeasuring) {
                    LoadingScreen.hide();
                }
            });

            // Add event listener for login form submission
            const loginForm = document.getElementById('loginForm');
            if (loginForm) {
                loginForm.addEventListener('submit', function() {
                    LoadingScreen.startMeasuring('login');
                });
            }

            // Listen for Google login button click
            const googleLoginBtn = document.querySelector('.google-login-btn');
            if (googleLoginBtn) {
                googleLoginBtn.addEventListener('click', function() {
                    LoadingScreen.startMeasuring('login');
                });
            }
        }
    },

    // Start measuring load time for a specific operation
    startMeasuring: function(operation) {
        this.currentOperation = operation;
        this.isMeasuring = true;
        this.startTime = Date.now();

        // Use the previously measured time (or default) for this operation
        const estimatedTime = this.loadTimes[operation] || 3;
        this.show(estimatedTime);
    },

    // Stop measuring and record the time
    stopMeasuring: function() {
        if (!this.isMeasuring || !this.currentOperation) return;

        const elapsedTime = (Date.now() - this.startTime) / 1000; // Convert to seconds

        // Update the stored load time with a weighted average (80% new, 20% old)
        // This helps smooth out variations while still adapting quickly
        const oldTime = this.loadTimes[this.currentOperation] || 3;
        const newTime = oldTime * 0.2 + elapsedTime * 0.8;

        // Cap between 1-10 seconds
        this.loadTimes[this.currentOperation] = Math.max(1, Math.min(10, newTime));

        console.log(`Measured load time for ${this.currentOperation}: ${elapsedTime.toFixed(2)}s, new average: ${this.loadTimes[this.currentOperation].toFixed(2)}s`);

        this.isMeasuring = false;
        this.currentOperation = null;

        // Hide the loading screen
        this.hide();
    },

    // Show the loading screen
    show: function(estimatedLoadTime) {
        if (!this.element) {
            this.element = document.getElementById('loadingScreen');
        }

        if (this.element) {
            // Store the current time if not already measuring
            if (!this.isMeasuring) {
                this.startTime = Date.now();
            }

            // Adjust animation speed based on estimated load time
            if (estimatedLoadTime && estimatedLoadTime > 0) {
                // Cap the animation duration between 1-10 seconds
                const duration = Math.max(1, Math.min(10, estimatedLoadTime)) + 's';
                this.element.style.setProperty(this.cssVars.fillDuration, duration);
                this.animationDuration = estimatedLoadTime * 1000;
            } else {
                // Default animation duration
                this.element.style.setProperty(this.cssVars.fillDuration, '3s');
                this.animationDuration = 3000;
            }

            // Show the loading screen
            this.element.style.display = 'flex';
            this.element.classList.remove('fade-out');
        }
    },

    // Hide the loading screen
    hide: function() {
        if (!this.element) {
            this.element = document.getElementById('loadingScreen');
        }

        if (this.element) {
            const elapsedTime = Date.now() - this.startTime;
            const remainingTime = Math.max(0, this.minDisplayTime - elapsedTime);

            // Ensure the loading screen is displayed for at least the minimum time
            setTimeout(() => {
                this.element.classList.add('fade-out');

                // Remove from DOM after transition completes
                setTimeout(() => {
                    this.element.style.display = 'none';
                }, 500); // Match with CSS transition time
            }, remainingTime);
        }
    }
};

// Initialize loading screen on DOM content loaded
document.addEventListener('DOMContentLoaded', function() {
    LoadingScreen.init();
});
