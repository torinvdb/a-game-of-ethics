# Asset ledger: Three Years in Thirty Minutes (v2)

Every visual in the v2 deck is **drawn by code in this directory**. There are no
photographs, film frames, posters, wallpapers or AI-generated illustrations.
The art direction borrows the *vocabulary* of late-1980s/1990s cyberpunk anime
backgrounds (painted dusk haze, dense vertical signage, overhead cables, phosphor
terminals, machine rooms). It does not copy any specific frame, character, logo or
composition from Akira, Ghost in the Shell or any other work.

The v1 deck used two crops from a third-party Ghost in the Shell-themed wallpaper
collection with unclear rights. **They have been removed** from the repository, along
with their provenance file, so the talk carries no third-party image rights.

| Asset | Made by | What it is | Data? |
| --- | --- | --- | --- |
| `plates/megacity-teal.jpg`, `megacity-ember.jpg` | `scenery.py` (seeds 7, 19) | Dusk skyline: haze layers, sign cliffs, expressway light trails, cables, rain | No |
| `plates/sign-wall.jpg` | `scenery.py` (seed 11) | Dense signage façade, AC units, pipes | No |
| `plates/machine-room.jpg` | `scenery.py` (seed 23) | One-point-perspective server hall | No |
| `plates/console-room.jpg` | `scenery.py` (seed 31) | Bank of CRT monitors over a control desk | No |
| `backgrounds/<slide>.jpg` | `motion.compose_background` | Plate + readability scrim, per slide | No |
| `motion/neon-ethics.*` | `motion.py` | 倫理 ("ethics") neon sign with a failing tube and small sparks | No |
| `motion/terminal-incident.*` | `motion.py` | CRT console typing the **fixture** incident facts | Fixture text |
| `motion/terminal-demo.*` | `motion.py` | CRT console with lines summarising a **recorded** demo run | Recorded run summary |
| `motion/neon-fault.*`, `sign-*.png` | `motion.py` | Neon placards: 解除 disable, 例外 exception, 延期 defer, 上申 escalate, 医療 medical, 学費 tuition | No |
| `motion/branch-timeline.*` | `motion.py` | Schematic of three branches over 36 logical months | Schematic only |
| `motion/time-odometer.*` | `motion.py` | Logical vs wall clock vs carried state (wall clock ≈ 2 s measured for the 8-trajectory demo) | Schematic |
| `motion/robot-seal.*` | `motion.py` | Robot arm stamping a scenario cartridge FROZEN with its real story sha256 prefix | Real hash prefix |
| `motion/robot-fault.*` | `motion.py` | Arm with a localized spark fault: "adapter fault: logged, not scored" | No |
| `motion/label-swap.*` | `motion.py` | Label swap schematic with 36 allocation cells | Mirrors recorded 0/36 vs 36/36 |
| `qr-repo.png` | `build.py` (qrcode 8.2) | QR code for the repository URL | No |

Motion is restrained: small localized sparks and flicker, no full-frame flashing
(well under three flashes per second over small areas), no audio. Each GIF has a
PNG still for the static PPTX, the PDF and reduced-motion playback.

## Fonts (all SIL Open Font License 1.1; texts in `fonts/licenses/`)

| File | Family | Use |
| --- | --- | --- |
| `Oswald-Bold.ttf` | Oswald | Titles (editable PPTX text) |
| `Rajdhani-SemiBold.ttf` | Rajdhani | Body text |
| `ShareTechMono-Regular.ttf` | Share Tech Mono | Labels, terminal text |
| `VT323-Regular.ttf` | VT323 | CRT text inside motion assets only |
| `DelaGothicOne-Regular.ttf` | Dela Gothic One (subset to the glyphs used) | Kanji signage inside images only |

Obtained from the Fontsource npm packages (`@fontsource/*` 5.3.x), converted from
WOFF2 to TTF with fontTools. **Install the first three on the presenting machine**
for PPTX playback; otherwise PowerPoint substitutes fonts and line breaks can move.
The HTML deck embeds all fonts. The small kanji in the chapter tags are editable
text and render with the system's Japanese font.
