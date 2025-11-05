# AI Agents Forex - Project Website

This directory contains the project website and portfolio pages for AI Agents Forex.

## 🌐 Live Website

The website is hosted on GitHub Pages at: `https://mauveandromeda.github.io/AI_Agents_Forex/`

## 📁 Files

- **index.html** - Project showcase page
- **portfolio.html** - Personal portfolio/resume page
- **style.css** - Main stylesheet
- **portfolio.css** - Portfolio-specific styles
- **script.js** - Main JavaScript functionality
- **portfolio.js** - Portfolio-specific JavaScript

## 🚀 Features

### Project Showcase (index.html)
- ✨ Modern, animated hero section
- 🎯 Feature cards with hover effects
- 📊 Interactive architecture diagram
- 📈 Project statistics and code breakdown
- 💻 Terminal demo with typing animation
- 🌙 Dark/Light mode toggle
- 📱 Fully responsive design

### Portfolio Page (portfolio.html)
- 👤 Personal profile section
- 💪 Skills visualization with progress bars
- 🎨 Featured projects showcase
- 📅 Timeline-based experience section
- 📧 Contact information
- 🎨 Animated UI elements

## 🎨 Design Features

- **Modern UI**: Clean, professional design with gradient accents
- **Animations**: Smooth fade-in, hover effects, and particle animations
- **Dark Mode**: Automatic dark/light theme switching
- **Responsive**: Mobile-first, adapts to all screen sizes
- **Interactive**: Particles canvas, typing animations, hover effects
- **Easter Eggs**: Hidden surprises for curious visitors

## 🛠️ Setup for GitHub Pages

### Method 1: Using GitHub Settings (Recommended)

1. Go to your repository on GitHub
2. Click **Settings** → **Pages**
3. Under **Source**, select:
   - Branch: `main` (or your default branch)
   - Folder: `/docs`
4. Click **Save**
5. Wait a few minutes for deployment
6. Your site will be live at `https://<username>.github.io/<repository>/`

### Method 2: Using GitHub Actions

Create `.github/workflows/pages.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
```

## 📝 Customization

### Update Personal Information

Edit `portfolio.html` and update:
- Your name
- Email address
- Social media links
- Projects
- Experience/Education
- Skills

### Update Project Information

Edit `index.html` and update:
- Project statistics
- Features
- Links
- Contact information

### Change Colors

Edit CSS variables in `style.css`:

```css
:root {
    --color-primary: #6366f1;
    --color-secondary: #8b5cf6;
    --color-accent: #ec4899;
    /* etc. */
}
```

### Add Your Resume PDF

1. Add your PDF to `/docs/files/resume.pdf`
2. Uncomment the download button code in `portfolio.js`

## 🖼️ Adding Images

To add profile picture or project images:

1. Create `/docs/images/` directory
2. Add your images
3. Update HTML to reference them:

```html
<img src="images/profile.jpg" alt="Profile">
```

## 🌟 Features to Customize

1. **Social Links**: Update all `href="#"` with your actual profiles
2. **Email**: Replace `your-email@example.com` with your real email
3. **Projects**: Add your own projects in the projects section
4. **Experience**: Update timeline with your actual experience
5. **Skills**: Adjust skill levels to match your expertise

## 📱 Testing Locally

To test the website locally:

```bash
# Navigate to docs directory
cd docs

# Start a simple HTTP server
python -m http.server 8000

# Or use Node.js
npx serve

# Open browser to localhost:8000
```

## 🎯 Performance Tips

- Images: Optimize and compress all images
- Fonts: Google Fonts are loaded async
- Code: Minify CSS and JS for production
- Caching: GitHub Pages handles caching automatically

## 🔧 Troubleshooting

### Website not showing up
- Check GitHub Pages settings
- Ensure branch and folder are correct
- Wait 5-10 minutes after first deployment

### Styles not loading
- Check file paths are relative
- Clear browser cache
- Verify all CSS files are committed

### Dark mode not working
- Check localStorage permissions
- Try in incognito mode
- Check browser console for errors

## 📄 License

This website template is part of the AI Agents Forex project and follows the same MIT License.

## 🙏 Credits

- Built with vanilla HTML, CSS, and JavaScript
- Icons: [Font Awesome](https://fontawesome.com/)
- Fonts: [Google Fonts](https://fonts.google.com/) (Inter & Fira Code)
- Animations: Custom CSS keyframes
- Inspired by modern portfolio designs

---

**Made with ❤️ for the AI Agents Forex project**
