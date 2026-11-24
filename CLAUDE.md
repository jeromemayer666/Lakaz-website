# Lakaz website — project notes for Claude

## Who I'm working with
Jérôme (owner of Lakaz holiday rentals, Mont Choisy, Mauritius). **Not a coder.**
- Explain every step in simple words.
- When he must do something himself, tell him exactly what to click / type.
- Keep checks light (few screenshots, few tool calls) to save usage. Tell him whenever there's a way to use less usage.

## What this folder is
The holiday-rental website **Lakaz** — https://lakazmauritius.com
- 6 static pages: `index.html`, `houses.html`, `filao.html`, `coco.html`, `story.html`, `contact.html`
- `build.py` generated those pages from the Claude Design canvas. **For small changes, edit the HTML files directly** (don't re-run build.py unless asked — it would overwrite hand edits).
- `netlify.toml` tells Netlify: no build command, publish the folder root. It also hides CLAUDE.md / build.py from visitors.
- `.gitignore` keeps junk (and the preview folder) out of GitHub.

## Style (keep consistent)
- Colours: green `#1F3B2D`, terracotta `#B4633A`, cream `#F4EDE1`
- Fonts: Cormorant Garamond (titles) + Jost (text)
- Header is transparent over the top photo; a 3-line menu button top right opens a small green panel (Our Houses, Lakaz Story, Contact Us).
- Photos are hotlinked from Unsplash. Sand-coloured **"Photo coming soon"** boxes are placeholders for Jérôme's own unit photos.

## Hosting (don't break these)
- GitHub: private repository **lakaz-website** (branch `main` = the live site).
- Netlify project **prismatic-crumble-142e4f** is linked to that repo: every change on `main` goes live automatically. No build command, publish directory = root.
- Domain lakazmauritius.com (+ www) is registered at Hostinger and already points to Netlify. **Never touch DNS.**
- The guest guide **guide.lakazmauritius.com** is a separate Netlify project (**"lakaz-guide"**). **Never touch it.**
- **Never include the folder "Lakaz website preview"** (it's a preview copy only, lives next to this folder).

## How we make changes (the workflow)
1. **New branch for every change.** Never edit `main` directly. Name it after the change, e.g. `feature/new-photos`, `fix/contact-typo`.
2. **Make the change** on that branch and save it (a "commit") with a short plain-English message.
3. **Push the branch to GitHub and open a Pull Request** into `main`.
4. **Check the Netlify preview.** Netlify automatically builds a "Deploy Preview" for the Pull Request — a private test link (looks like `deploy-preview-3--prismatic-crumble-142e4f.netlify.app`). The link appears on the Pull Request page on GitHub. Jérôme looks at it on his phone/laptop.
5. **Merge to go live.** If happy, click "Merge pull request" on GitHub. Netlify publishes `main` to lakazmauritius.com within about a minute. If not happy, keep changing the same branch — the preview updates.
6. Afterwards, switch back to `main` and pull the latest version before starting the next change.

Jérôme uses **GitHub Desktop** (no command line). When guiding him, give GitHub Desktop button names:
- New branch: *Current branch* (top) → *New branch* → type name → *Create branch*
- Save: bottom-left *Summary* box → type message → *Commit to <branch>*
- Upload: *Publish branch* / *Push origin* (top right)
- Open PR: *Preview Pull Request* / *Create Pull Request* (opens GitHub in the browser)
- After merging: *Current branch* → `main` → *Fetch origin* → *Pull origin*
If Claude Code is running in this folder and `git` is available, Claude can do the branch/commit/push steps itself — but always on a branch, never straight to `main`.

## To do later (not yet)
- [ ] Fill the `[X]` placeholders: bedrooms/guests per house, WhatsApp number, check-in/check-out times, minimum stay.
- [ ] Link the "Book on Airbnb" buttons once the listings are live.
- [ ] Replace the "Photo coming soon" boxes with Jérôme's real unit photos (after the photo shoot).
