# Elki Jacobs Design: Reel Style Guide

Permanent reference for every event Reel. Event-specific decisions live in `events/<date>_<event>/NOTES.md`.

**Guiding principle:** keep the artistic quality consistent without repeating an editing formula. Every event gets its own personality, music and rhythm. Don't just show what the event looked like; make the viewer feel what it was like to walk into the world Elki created.

**Evidence levels used below**
- **[verified]** observed directly in Elki's own material or brand notes.
- **[brief]** from the creative brief Anna supplied (Nov 2026). That brief was based on Instagram descriptions, not a frame-by-frame audit.
- **[rec]** editor recommendation, to be tested against Insights.

---

## Part A: permanent brand guidelines

### Identity
- Luxury event design studio; the design itself is the protagonist. The goal is an editorial or cinematic short film: fashion campaign or architectural editorial, never a recap template or slideshow. [brief]
- Theatre background: events are told as stories. [verified, brand book]
- Reference Reels to study (not yet analysed frame by frame): Harvard Club `instagram.com/elkija71/reel/DfjVBrmtstd/`, Havana at Cipriani `instagram.com/elkija71/reel/DeEL1EuNcRR/`, Noah's Ark / Chagall `instagram.com/deone.social/reel/DetZ8adtfh_/`. [brief]
- The best-performing Reel on record (17K views vs. a typical 300–2,200) was a **collab** from a verified videographer account. Post major events as collabs. [verified, brand book]

### Branding
- End on the approved logo only (`brand/logo_square.png`: EJ monogram + ELKI JACOBS DESIGN, white on black). The background is keyed to pure black so no grey box shows. Logo holds about 2.5 s with a slow 5% scale; no animation tricks. [verified asset]
- No logo intro, slogans, stickers or "SOUND ON" badges. [brief + brand book]
- Palette for any text: ivory `#FFF8F0`, light gold `#E8D7AE`. Fonts in `brand/fonts/` (Pinyon Script and Cormorant Garamond) are stand-ins until the approved Canva script font is confirmed. [verified palette; font **check**]
- Text only when it adds meaning; keep it inside the safe area (clear of the top 250 px and bottom 400 px). [brief]
- Never show a private or corporate client's name or logo without written permission: crop it out or skip the photo. [verified, brand book]

### Structure (flexible)
| Part | Approx. | Purpose |
|---|---|---|
| Opening | 0–3 s | One extraordinary image, no intro |
| Introduction | 3–10 s | Atmosphere: where are we, what world is this |
| Discovery | 10–22 s | Details, textures, flowers, bespoke elements; build curiosity |
| Transformation | 22–32 s | Wides showing how the pieces become one space |
| Climax | 32–38 s | The most powerful composition (not a repeat of the opening angle) |
| Ending | last 2–3 s | Hero image → discreet logo |
Total length about 30–45 s. Don't spend every strong image up front. [brief]

### Rhythm
- Hero 2–3 s · architectural wide 1.5–2.5 s · detail 0.8–1.5 s · rhythmic run 0.5–1 s · closing hero 2–3 s. Never one duration for everything. [brief]
- Build the timeline on a musical beat grid (BPM in the edit file) so cuts land on beats once the track is added; a short rhythmic run in the Discovery section works well. [rec]
- Alternate wide / medium / close. Avoid near-identical angles back to back. [brief]

### Transitions
- Mostly clean cuts. Dissolves only where they mean something: a time shift (night → day), a match (printed linen → the stained glass it quotes), and the fade to the logo. [brief + rec]
- Match by shape, colour or architectural line. [brief]
- Never: whip pans, glitches, flashes, spins, shake, template transitions. [brief]

### Motion on stills
- Slow push-ins, gentle pull-backs, lateral moves across a row of objects, or a slow tilt down a vertical space. Eased, never linear-jerky. [brief + rec]
- Strong symmetrical architecture can stay **static**. [brief]
- No artificial parallax, warping or aggressive zoom. Maximum drift is about 10–15% per shot. [brief + rec]

### Vertical crops
- 1080 × 1920. Crop every photo by hand. A landscape photo shows only 37.5% of its width in 9:16, so either pan across it or choose a vertical alternative. [rec]
- No blurred-background fill, no black bars. Remove distractions in the crop (tape, rigging, client branding). [brief + verified practice]

### Colour
- Keep the photographer's grade. Correct only to fix continuity; no blanket LUT, no extra saturation or orange push, no crushed blacks. Each event keeps its own palette. [brief]

### Music
- Music is part of the concept: pick it to suit the event (Cuban → Cuban, club → jazz, fashion → editorial electronic, wedding → emotive, theatrical → cinematic). [brief]
- Business accounts usually get only Meta's Sound Collection, not the full Instagram library. Music added in the Instagram app doesn't carry over to TikTok or YouTube, so choose sound per platform or bake in a licensed track. Flag licensing before publishing. [verified: Instagram Help]
- Videos are exported silent unless a licensed track is supplied. When choosing the track in Instagram, pick one near the edit's BPM and set its start point so the first downbeat lands at 0:00. [rec]

### Audience
- Luxury planners, high-end private clients, international wedding planners, corporate producers, venues, creative professionals. Create desire through image and atmosphere, not selling. [brief]

### Technical
- H.264 MP4, 1080 × 1920, 30 fps, yuv420p, faststart, CRF about 18. [rec]
- Pipeline: `tools/make_reel.py <edit.json> <photos_dir> <out.mp4> --storyboard <sheet.jpg>`. The JSON timeline is the editable project: swap a photo, crop, duration or transition there and re-render. Originals are never modified. Every export is versioned (`renders/reel_vN.mp4`) and never overwritten.

### QC before delivery
Hook within 3 s · clear concept · coherent journey · varied pacing · best images held long enough · no repeats · crops keep the key elements · palette intact · no black frames or glitches · no client branding without permission · logo clean · it feels like an international luxury designer made it.

---

## Part B: open items
- [ ] Analyse the three reference Reels frame by frame (needs a screen recording or a session that can open Instagram) and add **[verified]** findings above.
- [ ] Pull Insights for Elki's last 20 Reels and record what the top performers share.
- [ ] Confirm the approved script font from the Canva "Reel cover – MASTER".
