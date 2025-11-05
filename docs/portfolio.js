// ==========================================
// Portfolio Specific JavaScript
// ==========================================

// Animate skill bars when they come into view
const skillObserver = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const skillFill = entry.target;
            const level = skillFill.dataset.level;
            skillFill.style.width = level + '%';
            skillObserver.unobserve(skillFill);
        }
    });
}, { threshold: 0.5 });

document.querySelectorAll('.skill-fill').forEach(skill => {
    skillObserver.observe(skill);
});

// Animate timeline items
const timelineObserver = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.animation = 'fadeInLeft 0.6s ease-out forwards';
        }
    });
}, { threshold: 0.2 });

document.querySelectorAll('.timeline-item').forEach(item => {
    timelineObserver.observe(item);
});

// Add animation keyframes for timeline
const timelineStyle = document.createElement('style');
timelineStyle.textContent = `
    @keyframes fadeInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
`;
document.head.appendChild(timelineStyle);

// Project card hover effects
document.querySelectorAll('.project-card').forEach(card => {
    card.addEventListener('mouseenter', function() {
        const icon = this.querySelector('.project-icon');
        if (icon) {
            icon.style.transform = 'scale(1.1) rotate(5deg)';
            icon.style.transition = 'transform 0.3s ease-out';
        }
    });

    card.addEventListener('mouseleave', function() {
        const icon = this.querySelector('.project-icon');
        if (icon) {
            icon.style.transform = 'scale(1) rotate(0deg)';
        }
    });
});

// Contact card hover effects
document.querySelectorAll('.contact-card').forEach(card => {
    card.addEventListener('mouseenter', function() {
        const icon = this.querySelector('i');
        if (icon) {
            icon.style.transform = 'translateY(-8px) scale(1.1)';
            icon.style.transition = 'transform 0.3s ease-out';
        }
    });

    card.addEventListener('mouseleave', function() {
        const icon = this.querySelector('i');
        if (icon) {
            icon.style.transform = 'translateY(0) scale(1)';
        }
    });
});

// Smooth reveal for sections
const revealObserver = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('revealed');
        }
    });
}, {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
});

document.querySelectorAll('.about-section, .skills-section, .projects-section, .experience-section, .contact-section').forEach(section => {
    section.style.opacity = '0';
    section.style.transform = 'translateY(20px)';
    section.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
    revealObserver.observe(section);
});

// Add revealed class style
const revealStyle = document.createElement('style');
revealStyle.textContent = `
    .revealed {
        opacity: 1 !important;
        transform: translateY(0) !important;
    }
`;
document.head.appendChild(revealStyle);

// Tech badge animation
document.querySelectorAll('.tech-badge').forEach((badge, index) => {
    badge.style.animation = `fadeIn 0.4s ease-out ${index * 0.05}s both`;
});

const techBadgeStyle = document.createElement('style');
techBadgeStyle.textContent = `
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: scale(0.8);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
`;
document.head.appendChild(techBadgeStyle);

// Add particle effect to hero
const portfolioHero = document.querySelector('.portfolio-hero');
if (portfolioHero) {
    const canvas = document.createElement('canvas');
    canvas.style.position = 'absolute';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.pointerEvents = 'none';
    canvas.style.opacity = '0.3';

    portfolioHero.style.position = 'relative';
    portfolioHero.insertBefore(canvas, portfolioHero.firstChild);

    const ctx = canvas.getContext('2d');

    function resizeCanvas() {
        canvas.width = portfolioHero.offsetWidth;
        canvas.height = portfolioHero.offsetHeight;
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    const stars = [];
    for (let i = 0; i < 50; i++) {
        stars.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            radius: Math.random() * 2,
            vx: (Math.random() - 0.5) * 0.2,
            vy: (Math.random() - 0.5) * 0.2
        });
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        const theme = document.documentElement.getAttribute('data-theme');
        const color = theme === 'dark' ? '139, 92, 246' : '99, 102, 241';

        stars.forEach(star => {
            star.x += star.vx;
            star.y += star.vy;

            if (star.x < 0 || star.x > canvas.width) star.vx *= -1;
            if (star.y < 0 || star.y > canvas.height) star.vy *= -1;

            ctx.fillStyle = `rgba(${color}, 0.8)`;
            ctx.beginPath();
            ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
            ctx.fill();
        });

        requestAnimationFrame(animate);
    }

    animate();
}

// Add typing effect to portfolio title
const portfolioTitle = document.querySelector('.portfolio-title');
if (portfolioTitle) {
    const text = portfolioTitle.textContent;
    portfolioTitle.textContent = '';
    portfolioTitle.style.borderRight = '2px solid currentColor';

    let index = 0;
    function typeText() {
        if (index < text.length) {
            portfolioTitle.textContent += text.charAt(index);
            index++;
            setTimeout(typeText, 100);
        } else {
            portfolioTitle.style.borderRight = 'none';
        }
    }

    // Start typing after a delay
    setTimeout(typeText, 1000);
}

// Add hover effect to social buttons
document.querySelectorAll('.social-btn').forEach(btn => {
    btn.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-8px) rotate(15deg)';
    });

    btn.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0) rotate(0deg)';
    });
});

// Scroll progress indicator
const progressBar = document.createElement('div');
progressBar.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 0%;
    height: 3px;
    background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
    z-index: 9999;
    transition: width 0.1s ease-out;
`;
document.body.appendChild(progressBar);

window.addEventListener('scroll', function() {
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight - windowHeight;
    const scrolled = window.scrollY;
    const progress = (scrolled / documentHeight) * 100;
    progressBar.style.width = progress + '%';
});

// Add download resume button functionality (if you have a resume PDF)
const downloadButtons = document.querySelectorAll('[data-download="resume"]');
downloadButtons.forEach(button => {
    button.addEventListener('click', function(e) {
        // Uncomment when you have a resume PDF
        // e.preventDefault();
        // const link = document.createElement('a');
        // link.href = 'path/to/your/resume.pdf';
        // link.download = 'Resume_MauveAndromeda.pdf';
        // link.click();

        // For now, show a message
        alert('Resume download feature coming soon!');
    });
});

// Easter egg: Click avatar 5 times quickly
let avatarClickCount = 0;
let avatarClickTimer = null;

const avatar = document.querySelector('.avatar-circle');
if (avatar) {
    avatar.addEventListener('click', function() {
        avatarClickCount++;

        if (avatarClickTimer) {
            clearTimeout(avatarClickTimer);
        }

        avatarClickTimer = setTimeout(function() {
            avatarClickCount = 0;
        }, 1000);

        if (avatarClickCount === 5) {
            activateAvatarEasterEgg();
            avatarClickCount = 0;
        }
    });
}

function activateAvatarEasterEgg() {
    const avatar = document.querySelector('.avatar-circle');

    // Rainbow animation
    avatar.style.animation = 'rainbowRotate 2s linear infinite';

    const style = document.createElement('style');
    style.textContent = `
        @keyframes rainbowRotate {
            0% { filter: hue-rotate(0deg); transform: rotate(0deg); }
            100% { filter: hue-rotate(360deg); transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);

    // Show message
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
        animation: bounceIn 0.6s ease-out;
    `;
    message.textContent = '🎨 You unlocked the rainbow! 🌈';
    document.body.appendChild(message);

    setTimeout(function() {
        message.remove();
        avatar.style.animation = 'fadeInDown 0.6s ease-out';
    }, 3000);
}

// Log portfolio info to console
console.log('%c👨‍💻 Portfolio Website', 'font-size: 20px; font-weight: bold; color: #6366f1;');
console.log('%cMauveAndromeda - AI Engineer & Quantitative Developer', 'font-size: 14px; color: #8b5cf6;');
console.log('%cBuilt with passion and attention to detail', 'font-size: 12px; color: #64748b;');
console.log('%cClick the avatar 5 times quickly for a surprise! 👀', 'font-size: 10px; color: #94a3b8;');
