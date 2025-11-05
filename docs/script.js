// ==========================================
// Theme Toggle
// ==========================================
const themeToggle = document.getElementById('themeToggle');
const htmlElement = document.documentElement;

// Check for saved theme preference or default to 'light' mode
const currentTheme = localStorage.getItem('theme') || 'light';
htmlElement.setAttribute('data-theme', currentTheme);

// Update button icon
updateThemeIcon(currentTheme);

themeToggle.addEventListener('click', function() {
    const theme = htmlElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
    htmlElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    updateThemeIcon(theme);
});

function updateThemeIcon(theme) {
    const icon = themeToggle.querySelector('i');
    if (theme === 'dark') {
        icon.classList.remove('fa-moon');
        icon.classList.add('fa-sun');
    } else {
        icon.classList.remove('fa-sun');
        icon.classList.add('fa-moon');
    }
}

// ==========================================
// Mobile Menu Toggle
// ==========================================
const mobileMenuToggle = document.getElementById('mobileMenuToggle');
const navMenu = document.querySelector('.nav-menu');

mobileMenuToggle.addEventListener('click', function() {
    navMenu.classList.toggle('active');
    const icon = this.querySelector('i');
    icon.classList.toggle('fa-bars');
    icon.classList.toggle('fa-times');
});

// Close mobile menu when clicking outside
document.addEventListener('click', function(event) {
    if (!event.target.closest('.navbar')) {
        navMenu.classList.remove('active');
        const icon = mobileMenuToggle.querySelector('i');
        icon.classList.add('fa-bars');
        icon.classList.remove('fa-times');
    }
});

// ==========================================
// Particles Animation
// ==========================================
const canvas = document.getElementById('particlesCanvas');
if (canvas) {
    const ctx = canvas.getContext('2d');

    // Set canvas size
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Particles array
    const particles = [];
    const particleCount = 80;

    // Particle class
    class Particle {
        constructor() {
            this.reset();
        }

        reset() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.vx = (Math.random() - 0.5) * 0.5;
            this.vy = (Math.random() - 0.5) * 0.5;
            this.size = Math.random() * 2 + 1;
            this.opacity = Math.random() * 0.5 + 0.2;
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;

            // Wrap around edges
            if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
            if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
        }

        draw() {
            const theme = htmlElement.getAttribute('data-theme');
            const color = theme === 'dark' ? '99, 102, 241' : '99, 102, 241';

            ctx.fillStyle = `rgba(${color}, ${this.opacity})`;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    // Create particles
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }

    // Connect particles
    function connectParticles() {
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < 120) {
                    const theme = htmlElement.getAttribute('data-theme');
                    const color = theme === 'dark' ? '99, 102, 241' : '99, 102, 241';
                    const opacity = (1 - distance / 120) * 0.2;

                    ctx.strokeStyle = `rgba(${color}, ${opacity})`;
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }
    }

    // Animation loop
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        particles.forEach(particle => {
            particle.update();
            particle.draw();
        });

        connectParticles();

        requestAnimationFrame(animate);
    }

    animate();
}

// ==========================================
// Scroll Animations
// ==========================================
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.animation = 'fadeInUp 0.6s ease-out forwards';
        }
    });
}, observerOptions);

// Observe all feature cards, stat cards, etc.
document.querySelectorAll('.feature-card, .stat-card, .arch-layer').forEach(element => {
    observer.observe(element);
});

// ==========================================
// Code Bar Animations
// ==========================================
const codeBarObserver = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.width = entry.target.dataset.percentage + '%';
        }
    });
}, { threshold: 0.5 });

document.querySelectorAll('.code-bar-fill').forEach(bar => {
    bar.style.width = '0%';
    codeBarObserver.observe(bar);
});

// ==========================================
// Smooth Scroll for Navigation Links
// ==========================================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });

            // Close mobile menu if open
            navMenu.classList.remove('active');
            const icon = mobileMenuToggle.querySelector('i');
            icon.classList.add('fa-bars');
            icon.classList.remove('fa-times');
        }
    });
});

// ==========================================
// Navbar Scroll Effect
// ==========================================
let lastScroll = 0;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', function() {
    const currentScroll = window.pageYOffset;

    if (currentScroll > 100) {
        navbar.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
    } else {
        navbar.style.boxShadow = 'none';
    }

    lastScroll = currentScroll;
});

// ==========================================
// Terminal Typing Animation
// ==========================================
const terminalCommands = document.querySelectorAll('.terminal-command');
let commandIndex = 0;

function typeCommand(element, text, callback) {
    let index = 0;
    element.textContent = '';
    element.style.borderRight = '2px solid #fff';

    const interval = setInterval(function() {
        if (index < text.length) {
            element.textContent += text.charAt(index);
            index++;
        } else {
            element.style.borderRight = 'none';
            clearInterval(interval);
            if (callback) callback();
        }
    }, 50);
}

// Observer for terminal
const terminalObserver = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting && commandIndex === 0) {
            animateTerminal();
        }
    });
}, { threshold: 0.5 });

const terminal = document.querySelector('.terminal');
if (terminal) {
    terminalObserver.observe(terminal);
}

function animateTerminal() {
    const commands = [
        'git clone https://github.com/MauveAndromeda/AI_Agents_Forex.git',
        'cd AI_Agents_Forex',
        'pip install -r requirements.txt',
        'python run_backtest.py'
    ];

    function typeNextCommand() {
        if (commandIndex < terminalCommands.length) {
            typeCommand(terminalCommands[commandIndex], commands[commandIndex], function() {
                commandIndex++;
                setTimeout(typeNextCommand, 300);

                // Show output after last command
                if (commandIndex === terminalCommands.length) {
                    setTimeout(function() {
                        document.querySelector('.terminal-output').style.display = 'block';
                        document.querySelector('.terminal-output').style.animation = 'fadeInUp 0.6s ease-out';
                    }, 500);
                }
            });
        }
    }

    typeNextCommand();
}

// ==========================================
// Counter Animation for Stats
// ==========================================
function animateCounter(element, target, duration) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;

    const timer = setInterval(function() {
        current += increment;
        if (current >= target) {
            element.textContent = target.toLocaleString();
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current).toLocaleString();
        }
    }, 16);
}

const statsObserver = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const statNumber = entry.target.querySelector('.stat-number');
            const statValue = entry.target.querySelector('.stat-value');

            if (statNumber && !statNumber.dataset.animated) {
                const value = parseInt(statNumber.textContent.replace(/[^0-9]/g, ''));
                statNumber.dataset.animated = 'true';
                animateCounter(statNumber, value, 2000);
            }

            if (statValue && !statValue.dataset.animated) {
                const value = parseInt(statValue.textContent.replace(/[^0-9]/g, ''));
                statValue.dataset.animated = 'true';
                animateCounter(statValue, value, 2000);
            }
        }
    });
}, { threshold: 0.5 });

document.querySelectorAll('.stat-item, .stat-card').forEach(element => {
    statsObserver.observe(element);
});

// ==========================================
// Copy Code Functionality (if you add code blocks later)
// ==========================================
document.querySelectorAll('pre code').forEach(block => {
    const copyButton = document.createElement('button');
    copyButton.className = 'copy-button';
    copyButton.innerHTML = '<i class="fas fa-copy"></i>';
    copyButton.addEventListener('click', function() {
        navigator.clipboard.writeText(block.textContent).then(function() {
            copyButton.innerHTML = '<i class="fas fa-check"></i>';
            setTimeout(function() {
                copyButton.innerHTML = '<i class="fas fa-copy"></i>';
            }, 2000);
        });
    });
    block.parentElement.style.position = 'relative';
    block.parentElement.appendChild(copyButton);
});

// ==========================================
// Add Loading Animation
// ==========================================
window.addEventListener('load', function() {
    document.body.classList.add('loaded');
});

// ==========================================
// Easter Egg: Konami Code
// ==========================================
let konamiCode = [];
const konamiSequence = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];

document.addEventListener('keydown', function(e) {
    konamiCode.push(e.key);
    konamiCode = konamiCode.slice(-konamiSequence.length);

    if (konamiCode.join('') === konamiSequence.join('')) {
        activateEasterEgg();
    }
});

function activateEasterEgg() {
    // Add rainbow animation to all gradient text
    const style = document.createElement('style');
    style.textContent = `
        @keyframes rainbow {
            0% { filter: hue-rotate(0deg); }
            100% { filter: hue-rotate(360deg); }
        }
        .gradient-text, .btn-primary, .feature-icon {
            animation: rainbow 3s linear infinite !important;
        }
    `;
    document.head.appendChild(style);

    // Show a fun message
    const message = document.createElement('div');
    message.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        padding: 2rem 3rem;
        border-radius: 1rem;
        font-size: 1.5rem;
        font-weight: bold;
        z-index: 10000;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
        animation: fadeInUp 0.6s ease-out;
    `;
    message.textContent = '🎉 You found the secret! 🚀';
    document.body.appendChild(message);

    setTimeout(function() {
        message.style.animation = 'fadeOut 0.6s ease-out';
        setTimeout(function() {
            message.remove();
        }, 600);
    }, 3000);
}

console.log('%c🤖 AI Agents Forex', 'font-size: 20px; font-weight: bold; color: #6366f1;');
console.log('%cResearch-Grade Multi-Agent Trading System', 'font-size: 14px; color: #8b5cf6;');
console.log('%c8,200+ lines of code | 8 AI components | 100+ alpha factors', 'font-size: 12px; color: #64748b;');
console.log('%cTry the Konami code for a surprise! ⬆️⬆️⬇️⬇️⬅️➡️⬅️➡️BA', 'font-size: 10px; color: #94a3b8;');
