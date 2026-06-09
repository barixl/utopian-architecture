# INTERIOR-PROJECT

**Intereal** – Architecture & Interior Design Website

## Project Structure

```
INTERIOR-PROJECT/
│── assets/
│   ├── css/
│   │   ├── style.css          ← Main styles (colors, layout, components)
│   │   ├── responsive.css     ← All media query overrides
│   │   ├── animation.css      ← Keyframes & entrance animations
│   │   ├── plugin.css         ← Third-party plugin styles
│   │   ├── bootstrap.min.css
│   │   └── font-awesome.min.css
│   │
│   ├── js/
│   │   ├── main.js            ← Core interactivity (nav, counter, back-to-top)
│   │   ├── slider.js          ← Slick slider configurations
│   │   ├── animation.js       ← IntersectionObserver scroll animations
│   │   ├── plugin.js          ← Third-party plugins (SlickNav, jQuery UI, Slick)
│   │   ├── jquery-3.7.1.min.js
│   │   └── bootstrap.bundle.min.js
│   │
│   ├── fonts/                 ← Font Awesome webfonts
│   │
│   └── img/
│       ├── hero/              ← Banner/hero background images
│       ├── about/             ← About page & team photos
│       ├── services/          ← Service card images
│       ├── portfolio/         ← Project portfolio images
│       ├── furniture/         ← Shop/furniture product images
│       ├── gallery/           ← Gallery & testimonial images
│       ├── icons/             ← Process, feature, UI icons
│       ├── logo/              ← Logo variants & favicon
│       └── bg/                ← Section backgrounds & CTA images
│
├── index.html                 ← Home page
├── about.html                 ← About Us
├── services.html              ← Services list
├── portfolio.html             ← Project portfolio
├── shop.html                  ← Furniture shop (coming soon)
├── contact.html               ← Contact form
├── package.json
└── README.md
```

## Pages

| Page | File | Description |
|------|------|-------------|
| Home | `index.html` | Hero slider, about teaser, services, portfolio, process, testimonials, blog |
| About | `about.html` | Company story, team, values |
| Services | `services.html` | Full service list with details |
| Portfolio | `portfolio.html` | Project showcase |
| Shop | `shop.html` | Furniture & decor (coming soon) |
| Contact | `contact.html` | Contact form & location |

## Tech Stack

- **Bootstrap 5** – Layout & grid
- **Slick Slider** – Banner & testimonial carousels
- **SlickNav** – Mobile responsive navigation
- **jQuery 3.7.1** – DOM & interactions
- **Font Awesome 4.7** – Icons
- **Google Fonts** – Teko + Poppins

## Getting Started

```bash
# Install dev dependency
npm install

# Run local dev server
npm run dev
```

Or simply open `index.html` in a browser.

## Color Palette

| Name | Hex | Usage |
|------|-----|-------|
| Primary | `#252525` | Text, header bg, footer |
| Secondary | `#906E49` | Accents, hover, highlights |
| Secondary Light | `#F6F2EB` | Page background |
| White | `#ffffff` | Cards, text on dark |
| Grey | `#F1F1F1` | Borders, dividers |
