# Naoya's Personal Website

## Getting Started
Install Dependencies
```sh
pnpm install
```

Development
```sh
pnpm run dev
```

Build
```sh
pnpm run build
```

Preview
```sh
pnpm run preview
```

## Project Structure

Inside of your Astro project, you'll see the following folders and files:

```text
/
├── public/
│   └── favicon.svg
│   └── social-image.svg
├── src/
│   ├── actions/
│   │   └── # Astro server actions
│   ├── assets/
│   │   └── # Images that are transformed, optimized and bundled by Astro 
│   ├── components/
│   │   └── # Astro and React components
│   ├── layouts/
│   │   └── RootLayout.astro
│   └── pages/
│   │   └── blog/
│   │   │   └── index.astro
│   │   │   └── [...slug].astro
│   │   └── about.astro
│   │   └── contact.astro
│   │   └── index.astro
│   │   └── projects.astro
│   └── styles/
│   │   └── global.css
└── .gitignore
└── astro.config.mjs
└── package.json
└── tsconfig.json
```

## Deployment
Deployed on [Cloudflare Pages](https://pages.cloudflare.com/). For more information, see the [Cloudflare Pages documentation](https://developers.cloudflare.com/pages/).